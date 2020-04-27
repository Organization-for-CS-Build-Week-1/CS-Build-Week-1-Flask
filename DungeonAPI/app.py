import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit
from decouple import config

from .room import Room
from .player import Player
from .world import World
from .blueprints import items_blueprint, users_blueprint, rooms_blueprint, world_blueprint

from .models import DB, Users, Items, Worlds


def create_app():
    # Look up decouple for config variables
    #pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

    world = World()

    app = Flask(__name__)

    # Add config for database
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')

    # Stop tracking modifications on sqlalchemy config
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    socketio = SocketIO(app, cors_allowed_origins="*")
    DB.init_app(app)

    with app.app_context():
        # Creates tiny world with one player and item in our DB

        DB.drop_all()
        DB.create_all()

        new_i = Items(0, "hammer", 35, 2)

        DB.session.add(Worlds(world.password_salt, world.map_seed))
        quth = world.add_player("6k6", "fdfhgg", "fdfhgg")["key"]
        player_u = world.get_player_by_auth(quth)
        new_u = Users(player_u.username, player_u.password_hash,
                      False, player_u.world_loc[0], player_u.world_loc[1],
                      [new_i])

        DB.session.add(new_u)

        DB.session.commit()
        #world.load_from_db(DB)

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
    app.register_blueprint(world_blueprint.blueprint)

    def get_player_by_header(world, auth_header):
        if auth_header is None:
            return None

        auth_key = auth_header.split(" ")
        if auth_key[0] != "Token" or len(auth_key) != 2:
            return None

        player = world.get_player_by_auth(auth_key[1])
        return player

    @socketio.on("connect")
    def connection():
        print(f"\n{request.sid} is here!\n")
        emit("connected", "hello")

    @socketio.on("disconnect")
    def connection():
        print(f"\n{request.sid} is leaving\n")
        emit("connected", "hello")

    @socketio.on("test")
    def connection(data):
        print(f"\n{request.sid}")
        print(data)
        emit("we got you", data)

    @app.route('/')
    def home():
        return jsonify({'Hello': 'World!'}), 200

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

        return jsonify({}), 200

    @app.route('/api/registration', methods=['POST'])
    def register():
        values = request.get_json()
        required = ['username', 'password1', 'password2']

        if not all(k in values for k in required):
            response = {'message': "Missing Values"}
            return jsonify(response), 400

        username = values.get('username')
        password1 = values.get('password1')
        password2 = values.get('password2')

        response = world.add_player(username, password1, password2)
        if 'error' in response:
            return jsonify(response), 500
        else:
            return jsonify(response), 200

    @app.route('/api/login', methods=['POST'])
    def login():
        values = request.get_json()

        user = world.authenticate_user(values.get('username'),
                                       values.get('password'))

        if user is None:
            response = {"error": "Username or password incorrect."}
            return jsonify(response), 500

        response = {"key": user.auth_key}
        return jsonify(response), 200

    @app.route('/api/debug', methods=['POST'])
    def debug():
        player = world.get_player_by_auth(request.headers.get("Authorization"))
        if player is None:
            response = {'error': "Malformed auth header"}
            return jsonify(response), 500
        if not player.admin_q:
            response = {'error': "User not authorized"}
            return jsonify(response), 500

        response = {'str': "Authority accepted."}
        return jsonify(response), 200

    @app.route('/api/debug/save', methods=['GET'])
    def save():
        player = world.get_player_by_auth(request.headers.get("Authorization"))
        if player is None:
            response = {'error': "Malformed auth header"}
            return jsonify(response), 500
        if not player.admin_q:
            response = {'error': "User not authorized"}
            return jsonify(response), 500

        world.save_to_db(DB)

        response = {'str': "Successfully saved world."}
        return jsonify(response), 200

    @app.route('/api/debug/load', methods=['GET'])
    def load():
        player = world.get_player_by_auth(request.headers.get("Authorization"))
        if player is None:
            response = {'error': "Malformed auth header"}
            return jsonify(response), 500
        if not player.admin_q:
            response = {'error': "User not authorized"}
            return jsonify(response), 500

        world.load_from_db(DB)

        response = {'str': "Successfully loaded world."}
        return jsonify(response), 200

    @app.route('/api/debug/reset', methods=['GET'])
    def reset():
        player = world.get_player_by_auth(request.headers.get("Authorization"))
        if player is None:
            response = {'error': "Malformed auth header"}
            return jsonify(response), 500
        if not player.admin_q:
            response = {'error': "User not authorized"}
            return jsonify(response), 500

        world.create_world()

        response = {'str': "Successfully reset world."}
        return jsonify(response), 200

    @app.route('/api/adv/init', methods=['GET'])
    def init():
        player = world.get_player_by_auth(request.headers.get("Authorization"))
        if player is None:
            response = {'error': "Malformed auth header"}
            return jsonify(response), 500

        response = {
            'title': player.current_room.name,
            'description': player.current_room.description,
        }
        return jsonify(response), 200

    @app.route('/api/adv/move', methods=['POST'])
    def move():
        player = world.get_player_by_auth(request.headers.get("Authorization"))
        if player is None:
            response = {'error': "Malformed auth header"}
            return jsonify(response), 500

        values = request.get_json()
        required = ['direction']

        if not all(k in values for k in required):
            response = {'message': "Missing Values"}
            return jsonify(response), 400

        direction = values.get('direction')
        if player.travel(direction):
            response = {
                'title': player.current_room.name,
                'description': player.current_room.description,
            }
            return jsonify(response), 200
        else:
            response = {
                'error': "You cannot move in that direction.",
            }
            return jsonify(response), 500

    @app.route('/api/adv/take', methods=['GET'])
    def take_item():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400

    @app.route('/api/adv/drop', methods=['GET'])
    def drop_item():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400

    @app.route('/api/adv/inventory', methods=['GET'])
    def inventory():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400

    @app.route('/api/adv/buy', methods=['GET'])
    def buy_item():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400

    @app.route('/api/adv/sell', methods=['GET'])
    def sell_item():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400

    @app.route('/api/adv/rooms', methods=['GET'])
    def rooms():
        # IMPLEMENT THIS
        response = {'error': "Not implemented"}
        return jsonify(response), 400
    
    return app, socketio


if __name__ == '__main__':
    APP, socketio = create_app()
    print("app")
    socketio.run(APP)