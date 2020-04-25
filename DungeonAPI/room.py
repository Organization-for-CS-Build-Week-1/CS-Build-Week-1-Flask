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
            f"\t\titems: {self.self.items},\n"
            f"\t}}\n"
        )

