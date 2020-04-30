import random
import math
import bcrypt
from flask_socketio import emit
from decouple import config

from .room import Room
from .player import Player
from .map import Map
from .item import db_to_class

from .models import *


class World:

    def __init__(self, map_seed=16358):
        # rooms   { key: Room.world_loc,  value: Room }
        # players { key: Player.auth_key, value: Player }

        self.password_salt = bcrypt.gensalt()
        self.rooms         = {}
        self.players       = {}
        self.highscores    = [None, None, None]
        self.loaded        = False
        self.map_seed      = map_seed

    def add_player(self, username, password1, password2, socketid=None):
        """
        Adds a new player:
            - Verifies username/passwords
            - adds user to db
            - creates player in game

        Returns:
            - success → {'key': player.auth_key}
            - error   → {'error': error}
        """
        if password1 != password2:
            return {'error': "Passwords do not match"}
        elif len(username) <= 2:
            return {'error': "Username must be longer than 2 characters"}
        elif len(password1) <= 5:
            return {'error': "Password must be longer than 5 characters"}

        user = Users.query.filter_by(username=username).first()
        if user is not None:
            return {'error': "Username already exists"}

        password_hash = bcrypt.hashpw(password1.encode(), self.password_salt)
        world_loc = list(self.rooms.keys())[0]

        # Add user to DB first to get player id
        new_user = Users(username, password_hash, username == config("ADMIN_USERNAME"),
                         world_loc[0], world_loc[1])
        DB.session.add(new_user)
        DB.session.commit()
        player = Player(self, new_user.id, username, world_loc, password_hash,
                        auth_key=socketid, admin_q=new_user.admin_q)

        self.players[player.auth_key] = player
        return {'message': 'Player registered', 'key': player.auth_key}

    def get_player_by_auth(self, auth_key):
        return self.players.get(auth_key, None)

    def get_player_by_username(self, username):
        for auth_key in self.players:
            if self.players[auth_key].username == username:
                return self.players[auth_key]
        return None

    def load_player_from_db(self, username, password, socketid):
        user = Users.query.filter_by(username=username).first()
        if user is None:
            return {'error': 'Invalid username'}
        password_hash = bcrypt.hashpw(password.encode(), self.password_salt)
        if user.password_hash != password_hash:
            return {'error': 'Invalid password'}

        world_loc = (user.x, user.y)
        items = {i.id: db_to_class(i) for i in user.items}
        player = Player(self, user.id, user.username, world_loc,
                        user.password_hash, auth_key=socketid, admin_q=user.admin_q, items=items, highscore=user.highscore)
        self.players[player.auth_key] = player
        return {'message': 'logged in', 'key': player.auth_key}

    def save_player_to_db(self, player):
        """Saves player to db, and sets all items to have player's foreign key"""

        # Get user from DB
        user = Users.query.filter_by(username=player.username).first()
        new_user = False
        if user is None:
            # No user? Create one
            new_user = True
            user = Users(player.username, player.password_hash, player.admin_q,
                         player.world_loc[0], player.world_loc[1], highscore=player.highscore)
        else:
            # Is a user? Update these values
            user.x         = player.world_loc[0]
            user.y         = player.world_loc[1]
            user.highscore = player.highscore

        # Resets items from db, and only assigns items that the player has
        for i in user.items:
            i.player_id = None
        if new_user:
            DB.session.add(user)
        DB.session.commit()  # Ensure that our user object has a proper id

        for i in player.items.values():
            # Get item from db
            item = Items.query.filter_by(id=i.id).first()
            new_item = False
            if item is None:
                # No item? Create a new one
                new_item = True
                item = Items(i.name, i.weight, i.score, player_id=user.id)
            else:
                # Yes item? Update these values
                item.player_id = user.id
                item.room_id = None
            if new_item:
                DB.session.add(item)
        DB.session.commit()  # Save DB changes
        self.players.pop(player.auth_key)

    def confirm_highscores(self, player):
        """
        Checks the player's highscore with the top three.

        If the player is in the top three, update the values
        and send to all players.

        emits "highscoreupdate"
        """
        sendScores = False
        if player in self.highscores:
            # Even if the player doesn't move a place,
            # their score change still needs to be sent
            sendScores = True
            for i in range(2, 0, -1):
                if self.highscores[i - 1] is None or (self.highscores[i] and self.highscores[i].highscore > self.highscores[i - 1].highscore):
                    # If the compare value is None, or
                    # our current highscore is greater than compared highscore
                    # swap.
                    temp = self.highscores[i]
                    self.highscores[i] = self.highscores[i - 1]
                    self.highscores[i - 1] = temp
        else:
            for i in range(2):
                if self.highscores[i] is None or player.highscore > self.highscores[i].highscore:
                    # If you find a highscore lower than the player, or
                    # the compared spot is None, stick the player in there
                    sendScores = True
                    temp = player
                    player = self.highscores[i]
                    self.highscores[i] = temp
        if sendScores:
            send_highscores = [None, None, None]
            for i in range(len(self.highscores)):
                p = self.highscores[i]
                if isinstance(p, Player):
                    send_highscores[i] = f"{p.username} {p.highscore}"
            emit("highscoreupdate", send_highscores, broadcast=True)

    def get_map_info(self):
        """
        Returns a dictionary the FE can use to build a map

        Dict contains:
            - coordinates where rooms exist
            - coordinates where stores are
        """
        rooms, stores = [], []
        for room_coord in self.rooms.keys():
            # if isinstance(self.rooms[room_coord], Store):
            #     stores.append(room_coord)
            rooms.append(room_coord)

        return {"rooms": rooms, "stores": stores}

    def create_world(self):
        map = Map(25, 150)
        self.map_seed = map.generate_grid(map_seed=self.map_seed)
        self.rooms = map.generate_rooms(self)

    def save_to_db(self, DB):
        """
        Erases all world/room/item data and resaves.

        User data is preserved.
        """
        Items.__table__.drop(DB.engine, checkfirst=True)
        Worlds.__table__.drop(DB.engine, checkfirst=True)
        Rooms.__table__.drop(DB.engine, checkfirst=True)
        Worlds.__table__.create(DB.engine)
        Rooms.__table__.create(DB.engine)
        Users.__table__.create(DB.engine, checkfirst=True)
        Items.__table__.create(DB.engine)

        new_world = Worlds(self.password_salt, self.map_seed)
        DB.session.add(new_world)

        DB.session.commit()

        items = []

        for r in self.rooms.values():
            new_room = Rooms(r.name, r.description,
                             r.world_loc[0], r.world_loc[1])
            DB.session.add(new_room)
            DB.session.commit()

            for i in r.items.values():
                new_item = Items(i.name, i.weight, i.score,
                                 room_id=new_room.id)
                items.append(new_item)

        DB.session.bulk_save_objects(items)
        DB.session.commit()

    def load_from_db(self, DB):
        """
        Loads all Rooms and any associated items from the database
        into the game, if they exist.

        This function does NOT load any players. Use `add_player()`
        or `load_player_from_db()` to load players into the game.
        """
        db_worlds = Worlds.query.all()
        if db_worlds is None or len(db_worlds) == 0:
            DB.session.commit()
            return
        self.password_salt = db_worlds[0].password_salt
        self.map_seed = db_worlds[0].map_seed

        self.rooms = {}
        self.players = {}

        for r in Rooms.query.all():
            world_loc = (r.x, r.y)
            items = {i.id: db_to_class(i) for i in r.items}
            room = Room(self, r.name, r.description,
                        world_loc, id=r.id, items=items)

            self.rooms[room.world_loc] = room

        self.loaded = True
        DB.session.commit()
