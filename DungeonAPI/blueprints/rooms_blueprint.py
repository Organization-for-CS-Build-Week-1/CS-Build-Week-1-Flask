from flask import Blueprint, jsonify, request
from ..models import Rooms
from .middleware import admin_only

blueprint = Blueprint('rooms', __name__, url_prefix="/api/models/rooms")

@blueprint.route('/', methods=['GET'])
@admin_only
def get_all():
    rooms = Rooms.query.all()
    return jsonify([room.serialize() for room in rooms]), 200


@blueprint.route('/<room_id>', methods=['GET'])
@admin_only
def get_by_id(room_id):
    room = Rooms.query.filter_by(id=room_id).first()
    if room:
        return jsonify(room.serialize()), 200
    else:
        return jsonify({}), 200

