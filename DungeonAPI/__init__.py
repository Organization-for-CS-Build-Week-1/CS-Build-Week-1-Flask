"""Entry point for our DungeonAPI flask app"""

from .adventure import create_app

APP = create_app()
