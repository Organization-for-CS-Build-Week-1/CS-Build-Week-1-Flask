"""Entry point for our DungeonAPI flask app"""

from .app import create_app

APP, socketio = create_app()

if __name__ == '__main__':
    socketio.run(APP)