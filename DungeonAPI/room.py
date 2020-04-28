# Implement a class to hold room information. This should have name and
# description attributes.


class Room:

    def __init__(self, world, name, description, world_loc, loc_name=None, id=0, items=None):
        self.id          = id
        self.world       = world
        self.name        = name
        self.description = description
        self.world_loc   = world_loc
        self.loc_name    = loc_name
        self.items       = items if items is not None else {}

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