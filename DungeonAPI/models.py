from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class Worlds(DB.Model):
    __tablename__ = 'worlds'

    """World data"""
    id = DB.Column(DB.Integer, primary_key=True)
    password_salt = DB.Column(DB.LargeBinary, nullable=False)

    def __init__(self, password_salt):
        self.password_salt = password_salt

    def __repr__(self):
        output = {
            'id': self.id,
            'password_salt': self.password_salt
        }
        return str(output)

    def __str__(self):
        return self.__repr__()


class Users(DB.Model):
    __tablename__ = 'users'

    """Player data"""
    id = DB.Column(DB.Integer, primary_key=True)
    user_name = DB.Column(DB.Text, nullable=False)
    password_hash = DB.Column(DB.LargeBinary, nullable=False)
    auth_key = DB.Column(DB.Text, nullable=False)
    admin_q = DB.Column(DB.Boolean, nullable=False)
    x = DB.Column(DB.Integer, nullable=True)
    y = DB.Column(DB.Integer, nullable=True)
    # inventory_id = DB.Column(DB.Integer, nullable=False)

    # , inventory_id):
    def __init__(self, user_name, password_hash, auth_key, admin_q, x, y):
        self.user_name = user_name
        self.password_hash = password_hash
        self.auth_key = auth_key
        self.admin_q = admin_q
        self.x = x
        self.y = y
        # self.inventory_id = inventory_id

    def __repr__(self):
        output = {
            'id': self.id,
            'user_name': self.user_name,
            'current_room_id': self.current_room_id,
            'password_hash': self.password_hash,
            'auth_key': self.auth_key,
            'admin_q': self.admin_q
            # 'inventory_id':self.inventory_id
        }
        return str(output)

    def __str__(self):
        return self.__repr__()


class Rooms(DB.Model):
    __tablename__ = 'rooms'

    """Room data"""
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.Text, nullable=False)
    description = DB.Column(DB.String(256), nullable=True)
    x = DB.Column(DB.Integer, nullable=True)
    y = DB.Column(DB.Integer, nullable=True)
    # inventory_id = DB.Column(DB.Integer, nullable=False)

    # , inventory_id):
    def __init__(self, id, name, description, north_id, south_id, east_id, west_id, x, y):
        self.id = id
        self.name = name
        self.description = description
        self.x = x
        self.y = y
        # self.inventory_id = inventory_id

    def __repr__(self):
        output = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'north': self.north_id,
            'south': self.south_id,
            'east': self.east_id,
            'west': self.west_id,
            'x': self.x,
            'y': self.y
            # 'inventory_id':self.inventory_id
        }
        return str(output)

    def __str__(self):
        return self.__repr__()


class Items(DB.Model):
    __tablename__ = "items"

    """Item data"""
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.Text, nullable=True)
    weight = DB.Column(DB.Integer, nullable=False)
    score = DB.Column(DB.Integer, nullable=False)
    # inventory_id = DB.Column(DB.Integer, nullable=False)

    def __init__(self, id, name, weight, score):  # , inventory_id):
        self.id = id
        self.name = name
        self.weight = weight
        self.score = score
        # self.inventory_id = inventory_id

    def __repr__(self):
        output = {
            'id': self.id,
            'name': self.name,
            'weight': self.weight,
            'score': self.score,
            # 'inventory_id':self.inventory_id,
        }
        return str(output)

    def __str__(self):
        return self.__repr__()
