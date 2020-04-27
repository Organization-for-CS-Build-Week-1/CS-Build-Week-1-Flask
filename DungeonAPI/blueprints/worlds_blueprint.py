from flask import Blueprint, jsonify, request
from DungeonAPI.models import Worlds
from .middleware import admin_only

blueprint = Blueprint('world', __name__, url_prefix="/api/models/world")

@blueprint.route('/', methods=['GET'])
@admin_only
def get():
    worlds = Worlds.query.all()
    return jsonify([world.serialize() for world in worlds]), 200