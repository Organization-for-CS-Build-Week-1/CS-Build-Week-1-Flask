import hashlib
import json
from functools import wraps
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from decouple import config

from .room import Room
from .player import Player
from .world import World
from .blueprints import items_blueprint, users_blueprint, rooms_blueprint, worlds_blueprint

from .models import DB, Users, Items, Worlds


def create_app():

    def room_update(player):
        """
        Emits info via socket to all players
        in the same room as the given player.

        Used for init/move/take/drop,
        to update all players in room simulatneously.
            Player → Player who just performed action
        """
        response = {
            'room': player.current_room.serialize(),
            'player': player.serialize(),
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
        # Creates world with one player and 3 items in our DB
        world.create_world()  # TODO: Remove when done testing.
        world.save_to_db(DB)
        quth = world.add_player("6k6", "fdfhgg", "fdfhgg")["key"]
        player_u = world.get_player_by_auth(quth)
        new_i1 = Items("Hammer", 0, 0, player_id=player_u.id)
        new_i2 = Items("Trash", 10, 5, player_id=player_u.id)
        new_i3 = Items("Gem", 25, 50, player_id=player_u.id)
        DB.session.bulk_save_objects([new_i1, new_i2, new_i3])
        DB.session.commit()
        world.load_from_db(DB)

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
        emit("connected", "hello")

    @socketio.on("disconnect")
    def disconnect():
        print_socket_info(request.sid, "Left the server.")

    @socketio.on("test")
    def test(data):
        print_socket_info(request.sid, data)
        emit("test", data)

    @app.route('/')
    def home():
        return jsonify({'Hello': 'World!'}), 200

    @app.route('/socketoptions')
    def socket_options():
        return jsonify(["register", "login", "test", "init", "move", "take", "drop"]), 200

    @app.route('/api/check')
    def check():
        # Check if server is running and load world.
        world.create_world()  # TODO: Remove when done testing.
        world.save_to_db(DB)
        if not world.loaded:
            try:
                world.load_from_db(DB)
            except Exception:
                pass

            world.loaded = True

        return jsonify({'message': 'World is up and running'}), 200

    @socketio.on('register')
    def register(data):
        print_socket_info(request.sid, data)
        required = ['username', 'password1', 'password2']

        if not all(k in data for k in required):
            response = {'error': "Missing Values",
                        'required': 'username, password1, password2'}
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
    def login(data):
        print_socket_info(request.sid, data)

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
    def debug(player):
        print_socket_info(request.sid)
        response = {'message': "Authority accepted."}
        return emit('debug', response)

    @socketio.on('debug/save')
    @player_in_world
    @player_is_admin
    def save(player):
        print_socket_info(request.sid)
        world.save_to_db(DB)

        response = {'message': "Successfully saved world."}
        return emit('debug/save', response)

    @socketio.on('debug/load')
    @player_in_world
    @player_is_admin
    def load(player):
        print_socket_info(request.sid)
        world.load_from_db(DB)

        response = {'message': "Successfully loaded world."}
        return emit('debug/load', response)

    @socketio.on('debug/reset')
    @player_in_world
    @player_is_admin
    def reset(player):
        print_socket_info(request.sid)
        world.create_world()

        response = {'message': "Successfully reset world."}
        return emit('debug/reset', response)

    @socketio.on('init')
    @player_in_world
    def init(player):
        print_socket_info(request.sid)

        # Send map information
        response = {
            'map': player.world.get_map_info(),
        } 
        emit('mapinfo', response)

        # Send current room information
        join_room(str(player.world_loc))
        return room_update(player)

    @socketio.on('move')
    @player_in_world
    def move(player, direction):
        print_socket_info(request.sid, direction)

        if direction is None:
            return emit("moveError", {
                "error": "You must move a direction: 'n', 's', 'e', 'w'"})

        previous_room = str(player.world_loc)

        if player.travel(direction):
            # If the player travels successfully
            leave_room(previous_room)
            join_room(str(player.world_loc))
            return room_update(player)
        else:
            response = {
                'error': "You cannot move in that direction.",
            }
            return emit("moveError", response)

    @socketio.on('take')
    @player_in_world
    def take_item(player, item_id):
        print_socket_info(request.sid, f"take {item_id}")

        success = player.take_item(item_id)
        if success:
            return room_update(player)
        elif success is None:
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
    def drop_item(player, item_id):
        print_socket_info(request.sid, f"drop {item_id}")

        if player.drop_item(item_id):
            return room_update(player)
        else:
            response = {
                'error': 'You don\'t have this item'
            }
            emit('dropError', response)

    @socketio.on('inventory')
    def inventory():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400

    @socketio.on('buy')
    def buy_item():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400

    @socketio.on('sell')
    def sell_item():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400

    @socketio.on('rooms')
    def rooms():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400

    return app, socketio


if __name__ == '__main__':
    APP, socketio = create_app()
    print("app")
    socketio.run(APP)
