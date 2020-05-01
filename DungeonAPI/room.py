import random
from datetime import datetime, timedelta
from .item import Item, Trash, Stick, Gem, Hammer, db_to_class
from .models import DB, Items


class Room:

    def __init__(self, world, name, description, world_loc, loc_name=None, id=0, items=None):
        self.id          = id
        self.world       = world
        self.name        = name
        self.description = description
        self.world_loc   = world_loc
        self.loc_name    = loc_name
        self.items       = items if items is not None else {}

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "world_loc": self.world_loc,
            "items": self.item_coords(),
            "direction": self.directions
        }

    def __repr__(self):
        return (
            f"{{\n"
            f"\t\tid: {self.id},\n"
            f"\t\tname: {self.name},\n"
            f"\t\tdescription: {self.description},\n"
            f"\t\tworld_loc: {self.world_loc},\n"
            f"\t\tloc_name: {self.loc_name},\n"
            f"\t\titems: {self.items},\n"
            f"\t}}\n"
        )

    @property
    def directions(self):
        dir_list = []
        for d in "nesw":
            if self.get_room_in_direction(d) is not None:
                dir_list.append(d)
        return dir_list

    def get_room_in_direction(self, direction):
        if direction == 'n':
            return self.world.rooms.get((self.world_loc[0], self.world_loc[1] + 1), None)
        elif direction == 's':
            return self.world.rooms.get((self.world_loc[0], self.world_loc[1] - 1), None)
        elif direction == 'e':
            return self.world.rooms.get((self.world_loc[0] + 1, self.world_loc[1]), None)
        elif direction == 'w':
            return self.world.rooms.get((self.world_loc[0] - 1, self.world_loc[1]), None)
        else:
            return None

    def get_item_coords(self, item):
        """ Hash an item into a pair of coordniates. """
        x = hash((self.name, self.description, item)) % 420
        y = hash((item, self.name, self.description)) % 420

        return (x, y)

    def item_coords(self):
        """ Hash all items into a pair of coordniates. """
        return [(self.get_item_coords(i), i.serialize()) for i in self.items.values()]

    def add_item(self, item):
        if not item or not item.id:
            return False
        self.items[item.id] = item
        return True

    def get_item_weight(self, item_id):
        item = self.items.get(item_id, None)
        if item is None:
            return None
        else:
            return item.weight

    def remove_item(self, item_id):
        return self.items.pop(item_id)


class Tunnel(Room):

    def __init__(self, world, world_loc, loc_name=None, id=0, items=None):
        name        = f"Tunnel segment {world_loc[0]}-{world_loc[1]}"
        description = "An underground tunnel. Where does it lead? Continue to find out!"
        super().__init__(world, name, description, world_loc, loc_name, id, items)

class DeadEnd(Room):

    def __init__(self, world, world_loc, loc_name=None, id=0, items=None):
        name = f"Dead end {world_loc[0]}-{world_loc[1]}"
        description = "A dead end. Some thoughtless ant built a tunnel to nowhere! Better turn around."
        super().__init__(world, name, description, world_loc, loc_name, id, items)

class Store(Room):

    def __init__(self, world, world_loc, loc_name=None, id=0, items=None):
        name = "Ant Store"
        description = "A fabulous store where you can buy all things ant!"
        super().__init__(world, name, description, world_loc, loc_name, id, items)
        self.last_reset = datetime.now()
        if items is None:
            self.set_inventory()

    def set_inventory(self):
        potential_inventory = [
            [Trash(random.randint(0, 10**8)) for _ in range(15)],
            [Stick(random.randint(0, 10**8)) for _ in range(15)],
            [Gem(random.randint(0, 10**8)) for _ in range(15)],
            [Hammer(random.randint(0, 10**8)) for _ in range(15)]
        ]
        inventory = random.choice(potential_inventory)
        self.items = {}
        for i in inventory:
            item = Items(i.name, i.weight, i.score)
            DB.session.add(item)
            DB.session.commit()
            self.items[item.id] = db_to_class(item)

    def barter_item(self, item_id, barter_value):
        now = datetime.now()
        if now > self.last_reset + timedelta(minutes=10):
            self.last_reset = now
            self.set_inventory()
        item = self.items.get(item_id)
        if not item:
            return None
        elif item.score > barter_value:
            return False
        return item

def room_db_to_class(world, model_info, items):
    """Function that takes in DB information and returns the correct Room class"""
    name = model_info.name.lower()
    world_loc = (model_info.x, model_info.y)
    if "tunnel" in name:
        return Tunnel(world, world_loc, id=model_info.id, items = items)
    elif "dead end" in name:
        return DeadEnd(world, world_loc, id=model_info.id, items = items)
    elif "store" in name:
        return Store(world, world_loc, id=model_info.id, items = items)
    else:
        return Room(world, model_info.name, model_info.description, world_loc,
                    id=model_info.id, items = items)

