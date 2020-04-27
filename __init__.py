"""
ONLY USED FOR DEVELOPMENT

Heroku will launch this app from DungeonAPI/__init__.py

In development, you cannot use 'flask run' with socketio.
You must run THIS file with python:
"py __init__.py"

Running any other file will give import errors
"""


if __name__ == '__main__':
    from DungeonAPI.app import create_app
    APP, socketio = create_app()
    socketio.run(APP)