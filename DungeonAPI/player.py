import random
import uuid
from .item import db_to_class


class Player:
    def __init__(self, world, id, name, world_loc, password_hash, auth_key=None, highscore=0, admin_q=False, items=None):
        self.id            = id
        self.username      = name
        self.__auth_key    = auth_key if auth_key else Player.__generate_auth_key()
        self.password_hash = password_hash
        self.uuid          = uuid.uuid4
        self.admin_q       = admin_q

        self.world         = world
        self.world_loc     = world_loc  # tuple of coordinates in world (x, y)
        self.max_weight    = 100
        self.highscore     = highscore
        # Inventory { key: Item.id, value: Item }
        self.items         = Player.create_items(items) if items else {}

    @property
    def weight(self):
        total_weight = 0
        for item in self.items.values():
            total_weight += item.weight
        return total_weight

    @property
    def auth_key(self):
        return self.__auth_key

    @property
    def current_room(self):
        """
        `self.current_room`

        Returns the Room object the player is in.

        If there is no valid Room found, returns None.
        """
        return self.world.rooms.get(self.world_loc, None)

    def __generate_auth_key():
        digits = ['0', '1', '2', '3', '4', '5', '6',
                  '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
        auth_key_list = []
        for i in range(40):
            auth_key_list.append(random.choice(digits))
        return "".join(auth_key_list)

    def create_items(items):
        return {i.id: db_to_class(i) for i in items}

    def travel(self, direction, show_rooms=False):
        next_room = self.current_room.get_room_in_direction(direction)
        if next_room is not None:
            self.world_loc = next_room.world_loc
            return True
        else:
            print("You cannot move in that direction.")
            return False

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'world_loc': self.world_loc,
            'weight': self.weight,
            'highscore': self.highscore,
            'items': [item.serialize() for item in self.items.values()]
        }
