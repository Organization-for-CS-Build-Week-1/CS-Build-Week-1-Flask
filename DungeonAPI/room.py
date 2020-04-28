from .item import Item

class Room:

    def __init__(self, world, name, description, world_loc, loc_name=None, id=0, items=None):
        self.id          = id
        self.world       = world
        self.name        = name
        self.description = description
        self.world_loc   = world_loc
        self.loc_name    = loc_name
        self.items       = Item.create_items(items) if items is not None else {}

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "world_loc": self.world_loc,
            "items": [item.serialize() for item in self.items.values()],
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
            return self.world.rooms.get((self.world_loc[0], self.world_loc[1]+1), None)
        elif direction == 's':
            return self.world.rooms.get((self.world_loc[0], self.world_loc[1]-1), None)
        elif direction == 'e':
            return self.world.rooms.get((self.world_loc[0]+1, self.world_loc[1]), None)
        elif direction == 'w':
            return self.world.rooms.get((self.world_loc[0]-1, self.world_loc[1]), None)
        else:
            return None

    def add_item(self, item):
        if not item or not item.id:
            return False
        self.items[item.id] = item
        return True

    def remove_item(self, item_id):
        if item_id not in self.items:
            return None
        return self.items.pop(item_id)

class Tunnel(Room):

    def __init__(self, world, world_loc, loc_name, id=0, items=None):
        name        = f"Tunnel segment {world_loc[0]}-{world_loc[1]}"
        description = "An underground tunnel. Where does it lead? Continue to find out!"
        super().__init__(world, name, description, world_loc, loc_name, id, items)

class DeadEnd(Room):

    def __init__(self, world, world_loc, loc_name, id=0, items=None):
        name = f"Dead end {world_loc[0]}-{world_loc[1]}"
        description = "A dead end. Some thoughtless ant built a tunnel to nowhere! Better turn around."
        super().__init__(world, name, description, world_loc, loc_name, id, items)