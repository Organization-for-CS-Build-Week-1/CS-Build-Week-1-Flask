import random
from datetime import datetime, timedelta
from .item import Item, Trash, Stick, Gem, Hammer, db_to_class
from .models import DB, Items


class Room:

    def __init__(self, world, name, description, world_loc, loc_name=None, id=0, items=None, minutes_to_wait=20, item_max=10):
        self.id              = id
        self.world           = world
        self.name            = name
        self.description     = description
        self.world_loc       = world_loc
        self.loc_name        = loc_name
        self.last_reset      = datetime.now()
        self.minutes_to_wait = minutes_to_wait
        self.item_max        = item_max
        self.items           = items if items is not None else {}

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

    def set_inventory(self):
        """Resets a Room's inventory based to its max capacity"""
        potential_items = [Trash(random.randint(0, 10**8)) for _ in range(10)]
        potential_items += [Stick(random.randint(0, 10**8)) for _ in range(10)]
        potential_items += [Hammer(random.randint(0, 10**8)) for _ in range(5)]
        potential_items += [Gem(random.randint(0, 10**8)) for _ in range(1)]

        inventory = [i for i in random.choices(
            potential_items, k=self.item_max)]
        Items.query.filter_by(room_id=self.id).delete()
        DB.session.commit()
        items = [Items(i.name, i.weight, i.score, room_id=self.id)
                 for i in inventory]
        DB.session.bulk_save_objects(items)
        DB.session.commit()
        items = Items.query.filter_by(room_id=self.id).all()
        self.items = {i.id: db_to_class(i) for i in items}

    def check_inventory_reset(self):
        now = datetime.now()
        reset_time = self.last_reset + timedelta(minutes=self.minutes_to_wait)
        if now > reset_time and (len(self.items) < self.item_max // 2 or len(self.items) > 35):
            self.last_reset = now
            self.set_inventory()


class Tunnel(Room):

    def __init__(self, world, world_loc, loc_name=None, id=0, items=None):
        name        = f"Tunnel segment {world_loc[0]}-{world_loc[1]}"
        description = "An underground tunnel. Where does it lead? Continue to find out!"
        super().__init__(world, name, description, world_loc,
                         loc_name, id, items, minutes_to_wait=30, item_max=4)


class DeadEnd(Room):

    def __init__(self, world, world_loc, loc_name=None, id=0, items=None):
        name = f"Dead end {world_loc[0]}-{world_loc[1]}"
        description = "A dead end. Some thoughtless ant built a tunnel to nowhere! Better turn around."
        super().__init__(world, name, description, world_loc,
                         loc_name, id, items, minutes_to_wait=30, item_max=2)


class Store(Room):

    def __init__(self, world, world_loc, loc_name=None, id=0, items=None):
        name = "Ant Store"
        description = "A fabulous store where you can buy all things ant!"
        super().__init__(world, name, description, world_loc,
                         loc_name, id, items, minutes_to_wait=15)
        if items is None:
            self.set_inventory(reset=None)

    def set_inventory(self, reset=None):
        potential_inventory = [
            [Trash(random.randint(0, 10**8)) for _ in range(15)],
            [Stick(random.randint(0, 10**8)) for _ in range(15)],
            [Gem(random.randint(0, 10**8)) for _ in range(15)],
            [Hammer(random.randint(0, 10**8)) for _ in range(15)]
        ]
        inventory = random.choice(potential_inventory)
        if reset:
            Items.query.filter_by(room_id=self.id).delete()
            DB.session.commit()
            items = [Items(i.name, i.weight, i.score, room_id=self.id)
                     for i in inventory]
            DB.session.bulk_save_objects(items)
            DB.session.commit()
            items = Items.query.filter_by(room_id=self.id).all()
            self.items = {i.id: db_to_class(i) for i in items}
        else:
            self.items = {i.id: db_to_class(i) for i in inventory}

    def check_inventory_reset(self):
        now = datetime.now()
        if now > self.last_reset + timedelta(minutes=self.minutes_to_wait):
            self.last_reset = now
            self.set_inventory(True)

    def barter_item(self, item_id, barter_value):
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
        return Tunnel(world, world_loc, id=model_info.id, items=items)
    elif "dead end" in name:
        return DeadEnd(world, world_loc, id=model_info.id, items=items)
    elif "store" in name:
        return Store(world, world_loc, id=model_info.id, items=items)
    else:
        return Room(world, model_info.name, model_info.description, world_loc,
                    id=model_info.id, items=items)
