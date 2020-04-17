import random
import math
import bcrypt

from DungeonAPI.room import Room
from DungeonAPI.player import Player

from DungeonAPI.models import *

class World:
    def __init__(self):
        self.starting_room = None
        self.rooms = {}
        self.players = {}
        self.create_world()
        self.password_salt = bcrypt.gensalt()

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
        player = Player(username, list(self.rooms.values())[0], password_hash, admin_q = len(self.players) == 0)
        self.players[player.auth_key] = player
        return {'key': player.auth_key}

    def get_player_by_auth(self, auth_key):
        if auth_key in self.players:
            return self.players[auth_key]
        else:
            return None

    def get_player_by_username(self, username):
        for auth_key in self.players:
            if self.players[auth_key].username == username:
                return self.players[auth_key]
        return None

    def authenticate_user(self, username, password):
        user = self.get_player_by_username(username)
        if user is None:
            return None
        password_hash = bcrypt.hashpw(password.encode() ,self.password_salt)
        if user.password_hash == password_hash:
            return user
        return None

    def create_world(self):
        # UPDATE THIS:
        # Should create 100 procuedurally generated rooms
        self.rooms = {
            'outside':  Room("Outside Cave Entrance",
                             "North of you, the cave mount beckons", 1, 1, 1),

            'foyer':    Room("Foyer", """Dim light filters in from the south. Dusty
        passages run north and east.""", 2, 1, 2),

            'overlook': Room("Grand Overlook", """A steep cliff appears before you, falling
        into the darkness. Ahead to the north, a light flickers in
        the distance, but there is no way across the chasm.""", 3, 1, 3),

            'narrow':   Room("Narrow Passage", """The narrow passage bends here from west
        to north. The smell of gold permeates the air.""", 4, 2, 2),

            'treasure': Room("Treasure Chamber", """You've found the long-lost treasure
        chamber! Sadly, it has already been completely emptied by
        earlier adventurers. The only exit is to the south.""", 5, 2, 3),
        }

        # Link rooms together
        self.rooms['outside'].connect_rooms('n', self.rooms['foyer'])
        self.rooms['foyer'].connect_rooms('n', self.rooms['overlook'])
        self.rooms['foyer'].connect_rooms('e', self.rooms['narrow'])
        self.rooms['narrow'].connect_rooms('n', self.rooms['treasure'])

        self.starting_room = self.rooms['outside']

    def save_to_db(self, DB):
        DB.drop_all()
        DB.create_all()

        new_world = Worlds(self.password_salt)
        DB.session.add(new_world)

        #items = []

        for r in self.rooms.values():
          if r.n_to is None:
            n_id = None
          else:
            n_id = r.n_to.id

          if r.s_to is None:
            s_id = None
          else:
            s_id = r.s_to.id

          if r.e_to is None:
            e_id = None
          else:
            e_id = r.e_to.id

          if r.w_to is None:
            w_id = None
          else:
            w_id = r.w_to.id

          new_room = Rooms(r.id, r.name, r.description, n_id, s_id, e_id, w_id, r.x, r.y) #r.inventory_id)
          DB.session.add(new_room)

          #items += zip(r.items, [r.inventory_id] * len(r.items))

        DB.session.commit()

        for p in self.players.values():
          new_user = Users(p.username, p.current_room.id, p.password_hash, p.auth_key, p.admin_q) #, p.inventory_id)
          DB.session.add(new_user)

          # items += zip(p.items, [p.inventory_id] * len(p.items))

        # for i, inv_id in items:
          # new_item = Items(i.name, i.description, inv_id)
          # DB.session.add(new_item)

        DB.session.commit()

    def load_from_db(self, DB):
        self.password_salt = Worlds.query.all()[0].password_salt

        self.rooms = {}
        self.players = {}

        for r in Rooms.query.all():
            self.rooms[r.id] = Room(r.name, r.description, id = r.id,
                               # items = [], inventory_id = r.inventory_id,
                               n_to = r.north_id, s_to = r.south_id,
                               e_to = r.east_id, w_to = r.west_id,
                               x = r.x, y = r.y)
            # for i in Items.query.filter_by(inventory_id = r.inventory_id).all():
                # rooms[r.id].items += [Item(i.name, i.description)]

        for r in self.rooms.values():
            if r.n_to is not None:
                r.n_to = self.rooms[r.n_to]
            if r.s_to is not None:
                r.s_to = self.rooms[r.s_to]
            if r.e_to is not None:
                r.e_to = self.rooms[r.e_to]
            if r.w_to is not None:
                r.w_to = self.rooms[r.w_to]

        for u in Users.query.all():
            self.players[u.auth_key] = Player(u.user_name, self.rooms[u.current_room_id],\
                                               u.password_hash, u.admin_q==1)
            self.players[u.auth_key].auth_key = u.auth_key
                                    #, [], u.inventory_id)
            # for i in Items.query.filter_by(inventory_id = u.inventory_id).all():
                # self.players[u.id].items += [Item(i.name, i.description)]
