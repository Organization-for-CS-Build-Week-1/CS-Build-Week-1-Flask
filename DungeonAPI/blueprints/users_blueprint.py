from flask import Blueprint, jsonify
from DungeonAPI.models import Users
from .middleware import admin_only

blueprint = Blueprint('users', __name__, url_prefix="/api/models/users")


@blueprint.route('/', methods=['GET'])
@admin_only
def get_all():
    users = Users.query.all()
    return jsonify([user.serialize() for user in users]), 200


@blueprint.route('/<user_id>', methods=['GET'])
@admin_only
def get_by_id(user_id):
    user = Users.query.filter_by(id=user_id).first()
    return jsonify(user.serialize()), 200
