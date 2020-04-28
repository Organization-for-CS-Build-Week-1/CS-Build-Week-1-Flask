# Implement a class to hold room information. This should have name and
# description attributes.


class Room:

    def __init__(self, world, name, description, world_loc, id=0, items=None):
        self.id          = id
        self.world       = world
        self.name        = name
        self.description = description
        self.world_loc   = world_loc
        self.items       = items if items is not None else {}

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "world_loc": self.world_loc,
            "items": self.item_coords(),
        }

    def __repr__(self):
        return (
            f"{{\n"
            f"\t\tid: {self.id},\n"
            f"\t\tname: {self.name},\n"
            f"\t\tdescription: {self.description},\n"
            f"\t\tworld_loc: {self.world_loc},\n"
            f"\t\titems: {self.items},\n"
            f"\t}}\n"
        )

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

    def get_item_coords(self, item):
        """ Hash an item into a pair of coordniates. """
        x = hash((self.name, self.description, item)) % 480
        y = hash((item, self.name, self.description)) % 480

        return (x, y)

    def item_coords(self):
        """ Hash all items into a pair of coordniates. """
        return [ (self.get_item_coords(i),i.serialize()) for i in self.items.values() ]

class Tunnel(Room):

    def __init__(self, world, world_loc, id=0, items=None):
        name        = f"Tunnel segment {world_loc[0]}-{world_loc[1]}"
        description = "An underground tunnel. Where does it lead? Continue to find out!"
        super().__init__(world, name, description, world_loc, id, items)

class DeadEnd(Room):

    def __init__(self, world, world_loc, id=0, items=None):
        name = f"Dead end {world_loc[0]}-{world_loc[1]}"
        description = "A dead end. Some thoughtless ant built a tunnel to nowhere! Better turn around."
        super().__init__(world, name, description, world_loc, id, items)