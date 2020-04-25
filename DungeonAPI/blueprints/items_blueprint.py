from flask import Blueprint, jsonify
from DungeonAPI.models import Items
from .middleware import admin_only

blueprint = Blueprint('items', __name__, url_prefix="/api/models/items")


@blueprint.route('/', methods=['GET'])
@admin_only
def get_all():
    items = Items.query.all()
    return jsonify([item.serialize() for item in items]), 200


@blueprint.route('/<item_id>', methods=['GET'])
@admin_only
def get_by_id(item_id):
    item = Items.query.filter_by(id=item_id).first()
    return jsonify(item.serialize()), 200
