from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


def update_items_db(app, item_ids, player_id, room_id):
    """
    Finds the items with the given id,
    and updates their foreign keys in the DB.

    item_ids MUST be passed in as a list.
    """
    with app.app_context():
        db_items = Items.query.filter(Items.id.in_(item_ids)).all()
        for i in db_items:
            i.room_id = room_id
            i.player_id = player_id
        DB.session.commit()
    return


class Worlds(DB.Model):
    __tablename__ = 'worlds'

    """World data"""
    id            = DB.Column(DB.Integer, primary_key=True)
    password_salt = DB.Column(DB.LargeBinary, nullable=False)
    map_seed      = DB.Column(DB.Integer)

    def __init__(self, password_salt, map_seed):
        self.password_salt = password_salt
        self.map_seed      = map_seed

    def serialize(self):
        return {
            'id': self.id,
            'password_salt': str(self.password_salt),
            'map_seed': self.map_seed
        }

    def __repr__(self):
        output = {
            'id': self.id,
            'password_salt': self.password_salt,
            'map_seed': self.map_seed
        }
        return str(output)

    def __str__(self):
        return self.__repr__()


class Users(DB.Model):
    __tablename__ = 'users'

    """Player data"""
    id            = DB.Column(DB.Integer, primary_key=True)
    username      = DB.Column(DB.Text, nullable=False)
    password_hash = DB.Column(DB.LargeBinary, nullable=False)
    admin_q       = DB.Column(DB.Boolean, nullable=False)
    x             = DB.Column(DB.Integer, nullable=True)
    y             = DB.Column(DB.Integer, nullable=True)
    highscore     = DB.Column(DB.Integer, nullable=False, default=0)
    items         = DB.relationship('Items', backref="player", lazy=True)

    def __init__(self, username, password_hash, admin_q, x, y, items=None, highscore=0):
        self.username      = username
        self.password_hash = password_hash
        self.admin_q       = admin_q
        self.x             = x
        self.y             = y
        self.highscore     = highscore
        self.items         = items if items is not None else []

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'admin_q': self.admin_q,
            'x': self.x,
            'y': self.y,
            'highscore': self.highscore,
            'items': [item.serialize() for item in self.items]
        }

    def __repr__(self):
        output = {
            'id': self.id,
            'password_hash': self.password_hash,
            'username': self.username,
            'admin_q': self.admin_q,
            'x': self.x,
            'y': self.y,
            'highscore': self.highscore,
            'items': self.items
        }
        return str(output)

    def __str__(self):
        return self.__repr__()


class Rooms(DB.Model):
    __tablename__ = 'rooms'

    """Room data"""
    id          = DB.Column(DB.Integer, primary_key=True)
    name        = DB.Column(DB.Text, nullable=False)
    description = DB.Column(DB.String(256), nullable=True)
    x           = DB.Column(DB.Integer, nullable=True)
    y           = DB.Column(DB.Integer, nullable=True)
    items       = DB.relationship('Items', backref="room", lazy=True)

    def __init__(self, name, description, x, y, items=None):
        self.name        = name
        self.description = description
        self.x           = x
        self.y           = y
        self.items       = items if items is not None else []

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'x': self.x,
            'y': self.y,
            'items': [item.serialize() for item in self.items]
        }

    def __repr__(self):
        output = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'x': self.x,
            'y': self.y,
            'items': self.items
        }
        return str(output)

    def __str__(self):
        return self.__repr__()


class Items(DB.Model):
    __tablename__ = "items"

    """Item data"""
    id        = DB.Column(DB.Integer, primary_key=True)
    name      = DB.Column(DB.Text, nullable=True)
    weight    = DB.Column(DB.Integer, nullable=False)
    score     = DB.Column(DB.Integer, nullable=False)
    player_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'), nullable=True)
    room_id   = DB.Column(DB.Integer, DB.ForeignKey('rooms.id'), nullable=True)

    def __init__(self, name, weight, score, player_id=None, room_id=None):
        self.name      = name
        self.weight    = weight
        self.score     = score
        self.player_id = player_id
        self.room_id   = room_id

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'weight': self.weight,
            'score': self.score,
            'player_id': self.player_id,
            'room_id': self.room_id
        }

    def __repr__(self):
        output = {
            'id': self.id,
            'name': self.name,
            'weight': self.weight,
            'score': self.score,
            'player_id': self.player_id,
            'room_id': self.room_id
        }
        return str(output)

    def __str__(self):
        return self.__repr__()
