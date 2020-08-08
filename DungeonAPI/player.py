import random
import uuid
from threading import Thread
from flask import current_app
from flask_socketio import emit, leave_room, join_room
from .item import Trash
from .room import Store
from .models import update_items_db


class Player:
    def __init__(self, world, id, name, world_loc, password_hash, auth_key=None, highscore=0, admin_q=False, items=None):
        self.id            = id
        self.username      = name
        self.__auth_key    = auth_key if auth_key else Player.__generate_auth_key()
        self.password_hash = password_hash
        self.uuid          = uuid.uuid4
        self.admin_q       = admin_q

        self.room_loc      = {'x': 150, 'y': 150,
                              'vx': 0, 'vy': 0}  # Location and velocity
        self.world         = world
        self.world_loc     = world_loc  # tuple of coordinates in world (x, y)
        self.max_weight    = 100
        self.highscore     = highscore
        # Inventory { key: Item.id, value: Item }
        self.items         = items if items is not None else {}

    @property
    def weight(self):
        total_weight = 0
        for item in self.items.values():
            total_weight += item.weight
        return total_weight

    @property
    def score(self):
        total_score = 0
        for item in self.items.values():
            total_score += item.score
        return total_score

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

    def travel(self, direction, show_rooms=False):
        next_room = self.current_room.get_room_in_direction(direction)
        if next_room is None:
            return

        previous_room = str(self.world_loc)
        next_room.check_inventory_reset()
        self.world_loc = next_room.world_loc
        if direction == "n":
            self.room_loc['y'] = 440
        if direction == "s":
            self.room_loc['y'] = 60
        if direction == "w":
            self.room_loc['x'] = 440
        if direction == "e":
            self.room_loc['x'] = 60

        leave_room(previous_room, sid=self.auth_key)
        join_room(str(self.world_loc), sid=self.auth_key)

        response = {
            'room': self.current_room.serialize(),
            'chat': f"{self.username} entered the room"
        }
        return emit("roomupdate", response, room=str(self.world_loc))

    def move(self, vx, vy):
        new_x = self.room_loc['x'] + vx
        if new_x < 40:
            new_x = 40
        if new_x > 460:
            new_x = 460

        new_y = self.room_loc['y'] + vy
        if new_y < 40:
            new_y = 40
        if new_y > 460:
            new_y = 460

        self.room_loc['x'] = new_x
        self.room_loc['y'] = new_y
        self.room_loc['vx'] = vx
        self.room_loc['vy'] = vy

        possible_travel = self.travel_direction()
        self.travel(possible_travel)

    def travel_direction(self):
        x = self.room_loc['x']
        y = self.room_loc['y']

        if 232 < x and x < 268 and y <= 50:
            return 'n'
        if 232 < x and x < 268 and y >= 450:
            return 's'
        if 220 < y and y < 268 and x <= 50:
            return 'w'
        if 220 < y and y < 268 and x >= 450:
            return 'e'

    def drop_item(self, item_id):
        """
        Drops an item in the room.
        When successful, creates thread to update item in DB.

        Returns:
            player doesn't have item → False
            successful drop → chatmessage for the room
        """
        if item_id not in self.items:
            return False
        item = self.items.pop(item_id)
        self.current_room.add_item(item)
        Thread(target=update_items_db, args=(current_app._get_current_object(), [
               item.id], None, self.current_room.id)).start()
        article = "some" if isinstance(item, Trash) else "a"
        return f"{self.username} dropped {article} {item.name}"

    def barter(self, item_ids, store_item_id):
        """
        Sells several items to a store.
        When successful, creates thread to update items in DB.

        Returns:
            player doesn't have item ids → False
            successful sell → chatmessage
        """
        # Get total score and weight from items
        total_value = 0
        total_weight = 0
        for id in item_ids:
            if id not in self.items:
                # If an item isn't in player inventory, fail
                return {'error': 'You don\'t have all of these items.'}
            total_value  += self.items[id].score
            total_weight += self.items[id].weight

        success = self.current_room.barter_item(store_item_id, total_value)
        if success is None:
            return {'error': 'This item is not in the room.'}
        if success == False:
            return {'error': 'You need to barter something more valuable!'}

        item_weight = self.current_room.get_item_weight(store_item_id)
        new_weight = self.weight - total_weight + item_weight
        if new_weight > self.max_weight:
            return {'error': 'Your inventory is too full!', 'full': None}

        for item_id in item_ids:
            item = self.items.pop(item_id)
            self.current_room.add_item(item)
        Thread(target=update_items_db, args=(current_app._get_current_object(),
                                             item_ids, None, self.current_room.id)).start()
        message = self.take_item(store_item_id)
        return {'chat': f"{self.username} bartered at the store"}

    def take_item(self, item_id):
        """
        Takes an item from the room.
        When successful, creates thread to update items in DB.

        If the player's new score is greater than the highscore,
        also updates highscore.

        Returns:
            item not in room → None
            player's inventory too full → False
            successful take → chatmessage for the room
        """
        item_weight = self.current_room.get_item_weight(item_id)
        if item_weight is None:
            return None
        if self.weight + item_weight > self.max_weight:
            return False
        item = self.current_room.remove_item(item_id)
        self.items[item.id] = item
        if self.score > self.highscore:
            self.highscore = self.score
            self.world.confirm_highscores(self)
        Thread(target=update_items_db, args=(
            current_app._get_current_object(), [item.id], self.id, None)).start()
        article = "some" if isinstance(item, Trash) else "a"
        return f"{self.username} took {article} {item.name}"

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'world_loc': self.world_loc,
            'room_loc': self.room_loc,
            'weight': self.weight,
            'score': self.score,
            'highscore': self.highscore,
            'items': [item.serialize() for item in self.items.values()]
        }
