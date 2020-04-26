import random
import math
import bcrypt

from DungeonAPI.room import Room
from DungeonAPI.player import Player
from DungeonAPI.map import Map
from DungeonAPI.item import Item

from DungeonAPI.models import *


class World:

    def __init__(self):
        # rooms   { key: Room.world_loc,  value: Room }
        # players { key: Player.auth_key, value: Player }

        self.password_salt = bcrypt.gensalt()
        self.rooms         = {}
        self.players       = {}
        self.loaded        = False
        # self.create_world()

    def add_player(self, username, password1, password2):
        if password1 != password2:
            return {'error': "Passwords do not match"}
        elif len(username) <= 2:
            return {'error': "Username must be longer than 2 characters"}
        elif len(password1) <= 5:
            return {'error': "Password must be longer than 5 characters"}
        elif self.get_player_by_username(username) is not None:
            return {'error': "Username already exists"}

        password_hash = bcrypt.hashpw(password1.encode(), self.password_salt)
        world_loc = (4, 5)

        # Add user to DB first to get player id
        new_user = Users(username, password_hash, False, 4, 5)
        DB.session.add(new_user)
        DB.session.commit()

        player = Player(self, new_user.id, username, world_loc, password_hash,
                        admin_q=len(self.players) == 0)

        self.players[player.auth_key] = player
        return {'key': player.auth_key}

    def get_player_by_auth(self, auth_key):
        return self.players.get(auth_key, None)

    def get_player_by_username(self, username):
        for auth_key in self.players:
            if self.players[auth_key].username == username:
                return self.players[auth_key]
        return None

    def authenticate_user(self, username, password):
        user = self.get_player_by_username(username)
        if user is None:
            return None
        password_hash = bcrypt.hashpw(password.encode(), self.password_salt)
        if user.password_hash == password_hash:
            return user
        return None

    def create_world(self):
        map = Map(25, 150)
        self.rooms = map.generate_rooms()

    def save_to_db(self, DB):
        """
        Erases all data and resaves.

        Not recommended unless a full server refresh is needed.
        """
        DB.drop_all()
        DB.create_all()

        new_world = Worlds(self.password_salt)
        DB.session.add(new_world)

        DB.session.commit()

        items = []

        for r in self.rooms.values():
            new_room = Rooms(r.name, r.description,
                             r.world_loc[0], r.world_loc[1])
            DB.session.add(new_room)

            for i in r.items:
                new_item = Items(i.name, i.weight, i.score, room_id=r.id)
                items.append(new_item)

        DB.session.commit()

        for p in self.players.values():
            new_user = Users(p.username, p.password_hash,
                             p.admin_q, p.world_loc[0], p.world_loc[1])
            DB.session.add(new_user)

            for i in p.items:
                new_item = Items(i.name, i.weight, i.score, player_id=p.id)
                items.append(new_item)

        DB.session.commit()

        DB.session.bulk_save_objects(items)
        DB.session.commit()

    def load_from_db(self, DB):
        self.password_salt = Worlds.query.all()[0].password_salt

        self.rooms = {}
        self.players = {}

        for r in Rooms.query.all():
            world_loc = (r.x, r.y)
            room = Room(self, r.name, r.description,
                        world_loc, id=r.id, items=r.items)

            self.rooms[room.world_loc] = room

        for u in Users.query.all():
            world_loc = (u.x, u.y)
            player = Player(self, u.id, u.user_name, world_loc, u.password_hash,
                            admin_q=u.admin_q == 1, items=u.items)

            self.players[player.auth_key] = player

        self.loaded = True
