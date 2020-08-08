import hashlib
import json
from functools import wraps
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit, join_room
from decouple import config

from .room import Room, Store
from .player import Player
from .world import World
from .blueprints import items_blueprint, users_blueprint, rooms_blueprint, worlds_blueprint

from .models import DB, Users, Items, Worlds, Rooms


def create_app():

    def room_update(player, chatmessage, chat_only=False):
        """
        Emits info via socket to all players
        in the same room as the given player.

        Used for init/move/take/drop,
        to update all players in room simulatneously.
            Player      → Player who just performed action
            chatmessage → message for FE chat
        """
        response = {
            'room': None if chat_only else player.current_room.serialize(),
            'chat': chatmessage
        }
        return emit("roomupdate", response, room=str(player.world_loc))

    def print_socket_info(sid, data=None):
        print(f"\n{sid}")
        if data:
            print(data)
        print()

    def player_in_world(f):
        """
        Checks if the player's socket id exists in the world.
        -  exists → Continue request
        - !exists → emit 'noPlayer' error
        Any following function MUST include player as the first parameter.
        """
        @wraps(f)
        def handler(*args, **kwargs):
            player = world.get_player_by_auth(request.sid)
            if player is None:
                response = {'error': 'No player found in world'}
                return emit('noPlayer', response)
            else:
                return f(player, *args, **kwargs)
        return handler

    def player_is_admin(f):
        """
        Checks if the existing player has `admin_q` set to True.
        -  True → Continue request
        - False → emit 'noAdmin' error
        This decorator MUST come after `@player_in_world` to access
        the player.

        Any following function MUST include player as the first parameter.
        """
        @wraps(f)
        def handler(player, *args, **kwargs):
            if not player.admin_q:
                response = {'error': "User not authorized"}
                return emit('noAdmin', response)
            else:
                return f(player, *args, **kwargs)
        return handler

    world = World()

    app = Flask(__name__)

    # Add config for database
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')

    # Stop tracking modifications on sqlalchemy config
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    socketio = SocketIO(app, cors_allowed_origins="*")
    DB.init_app(app)

    with app.app_context():
        # Create Tables if they don't already exist
        Worlds.__table__.create(DB.engine, checkfirst=True)
        Rooms.__table__.create(DB.engine, checkfirst=True)
        Users.__table__.create(DB.engine, checkfirst=True)
        Items.__table__.create(DB.engine, checkfirst=True)
        # Loads our world if it exists
        world.load_from_db(DB)

        if len(world.rooms) == 0:
            # If the world is empty, creates one
            world.create_world()
            world.save_to_db(DB)
        if len(Users.query.all()) == 0:
            # If we have no users, start with our admin user
            username = config("ADMIN_USERNAME")
            password = config("ADMIN_PASSWORD")
            quth = world.add_player(username, password, password)
            if 'key' in quth:
                player = world.get_player_by_auth(quth['key'])
                world.save_player_to_db(player)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    app.register_blueprint(items_blueprint.blueprint)
    app.register_blueprint(users_blueprint.blueprint)
    app.register_blueprint(rooms_blueprint.blueprint)
    app.register_blueprint(worlds_blueprint.blueprint)

    def get_player_by_header(world, auth_header):
        if auth_header is None:
            return None

        auth_key = auth_header.split(" ")
        if auth_key[0] != "Token" or len(auth_key) != 2:
            return None

        player = world.get_player_by_auth(auth_key[1])
        return player

    @socketio.on("connect")
    def connect():
        print_socket_info(request.sid, "Joined the server.")
        emit("connected", request.sid)

    @socketio.on("disconnect")
    def disconnect():
        print_socket_info(request.sid, "Left the server.")
        player = world.get_player_by_auth(request.sid)
        if player is not None:
            world.save_player_to_db(player)

    @socketio.on("test")
    def test(data):
        print_socket_info(request.sid, data)
        emit("test", data)

    @app.route('/')
    def home():
        return jsonify({'Hello': 'World!'}), 200

    @app.route('/socketoptions')
    def socket_options():
        return jsonify(["register", "login", "test", "init", "move", "take", "drop", "chat"]), 200

    @app.route('/api/check')
    def check():
        # Check if server is running and load world.
        value = request.get_json()
        world.create_world(value.get('seed'))
        world.save_to_db(DB)
        if not world.loaded:
            try:
                world.load_from_db(DB)
            except Exception:
                pass

            world.loaded = True

        return jsonify({'message': 'World is up and running'}), 200

    @socketio.on('register')
    def register(data=None, *_, **__):
        print_socket_info(request.sid, data)
        required = ['username', 'password1', 'password2']

        if not data or not all(k in data for k in required):
            response = {
                'error': 'Please provide: username, password1, password2'}
            return emit('registerError', response)

        username = data.get('username')
        password1 = data.get('password1')
        password2 = data.get('password2')

        response = world.add_player(
            username, password1, password2, request.sid)
        if 'error' in response:
            return emit('registerError', response)
        else:
            return emit('register', response)

    @socketio.on('login')
    def login(data=None, *_, **__):
        print_socket_info(request.sid, data)

        if not data:
            response = {'error': 'Please provide a username and password'}
        else:
            response = world.load_player_from_db(data.get('username'),
                                                 data.get('password'),
                                                 request.sid)

        if 'error' in response:
            return emit('loginError', response)
        else:
            return emit('login', response)

    @socketio.on('debug')
    @player_in_world
    @player_is_admin
    def debug(player, *_, **__):
        print_socket_info(request.sid)
        response = {'message': "Authority accepted."}
        return emit('debug', response)

    @socketio.on('debug/save')
    @player_in_world
    @player_is_admin
    def save(player, *_, **__):
        print_socket_info(request.sid)
        world.save_to_db(DB)

        response = {'message': "Successfully saved world."}
        return emit('debug/save', response)

    @socketio.on('debug/load')
    @player_in_world
    @player_is_admin
    def load(player, *_, **__):
        print_socket_info(request.sid)
        world.load_from_db(DB)

        response = {'message': "Successfully loaded world."}
        return emit('debug/load', response)

    @socketio.on('debug/reset')
    @player_in_world
    @player_is_admin
    def reset(player, *_, **__):
        print_socket_info(request.sid)
        world.create_world()

        response = {'message': "Successfully reset world."}
        return emit('debug/reset', response)

    @socketio.on('init')
    @player_in_world
    def init(player, *_, **__):
        print_socket_info(request.sid)

        # Send map and highscore information
        response = player.world.get_map_info(),
        highscoreupdate = player.world.confirm_highscores(
            player, single_socket=True)
        emit("highscoreupdate", highscoreupdate)
        emit('mapinfo', response)
        emit('playerupdate', player.serialize())
        # Send current room information
        join_room(str(player.world_loc))
        chatmessage = f"{player.username} entered the room"
        return room_update(player, chatmessage)

    @socketio.on('move')
    @player_in_world
    def move(player, movement, *_, **__):
        vx = movement["vx"]
        vy = movement["vy"]
        world.add_to_movement_queue((player, vx, vy))

    @socketio.on('take')
    @player_in_world
    def take_item(player, item_id=None, *_, **__):
        print_socket_info(request.sid, f"take {item_id}")

        if item_id is None or not isinstance(item_id, int):
            return emit("takeError", {
                "error": "You must provide a valid item_id integer"})

        if isinstance(player.current_room, Store):
            return emit("takeError", {"error": "You must barter at the store"})

        chatmessage = player.take_item(item_id)
        if chatmessage:
            emit("playerupdate", player.serialize())
            return room_update(player, chatmessage)
        elif chatmessage is None:
            response = {
                'error': 'This item is not in the room'
            }
            return emit('takeError', response)
        else:
            response = {
                'error': 'Your inventory is too full!'
            }
            return emit('full', response)

    @socketio.on('drop')
    @player_in_world
    def drop_item(player, item_id=None, *_, **__):
        print_socket_info(request.sid, f"drop {item_id}")

        if item_id is None or not isinstance(item_id, int):
            return emit("takeError", {
                "error": "You must provide a valid item_id integer"})

        chatmessage = player.drop_item(item_id)
        if chatmessage:
            emit("playerupdate", player.serialize())
            return room_update(player, chatmessage)
        else:
            response = {
                'error': 'You don\'t have this item'
            }
            emit('dropError', response)

    @socketio.on('chat')
    @player_in_world
    def inventory(player, message=None, *_, **__):
        print_socket_info(request.sid, f"CHAT: {message}")

        if message is None or not isinstance(message, str):
            return emit("chatError", {
                "error": "You must send a message"})

        room_update(player, f"{player.username}: {message}", chat_only=True)

    @socketio.on('inventory')
    def inventory():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return emit('error', response)

    @socketio.on('barter')
    @player_in_world
    def barter_item(player, data=None, *_, **__):
        print_socket_info(request.sid, data)

        bad_format = {
            'error': 'Please provide a valid data dictionary.',
            'required': '{"player_item_ids": int[], "store_item_id": int}'
        }

        if not isinstance(data, dict):
            return emit('barterError', bad_format)

        player_item_ids = data.get('player_item_ids')
        store_item_id   = data.get('store_item_id')
        store = world.rooms.get(tuple(player.world_loc))

        if not store or not isinstance(store, Store):
            response = {
                'error': 'The current room is not a store.'
            }
            return emit('storeError', response)

        if not isinstance(player_item_ids, list) or not isinstance(store_item_id, int):
            return emit('barterError', bad_format)

        for id in player_item_ids:
            if not isinstance(id, int):
                return emit('barterError', bad_format)

        response = player.barter(player_item_ids, store_item_id)
        if 'error' in response:
            if 'full' in response:
                response = {
                    'error': 'Your inventory is too full!'
                }
                return emit('full', response)
            else:
                return emit('barterError', response)

        emit('playerupdate', player.serialize())
        return room_update(player, response.get('chat'))

    @socketio.on('sell')
    def sell_item():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return emit('error', response)

    @socketio.on('rooms')
    def rooms():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return emit('error', response)

    return app, socketio


if __name__ == '__main__':
    APP, socketio = create_app()
    print("app")
    socketio.run(APP)
