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

class Tunnel(Room):

    def __init__(self, world, world_loc, id=0, items=None):
        name        = f"Tunnel segment {world_loc[0]}-{world_loc[1]}"
        description = "An underground tunnel. Where does it lead? Continue to find out!"
        super.__init__(world, name, description, world_loc, id, items)

class DeadEnd(Room):

    def __init__(self, world, world_loc, id=0, items=None):
        name = f"Dead end {world_loc[0]}-{world_loc[1]}"
        description = "A dead end. Some thoughtless ant built a tunnel to nowhere! Better turn around."
        super.__init__(world, name, description, world_loc, id, items)