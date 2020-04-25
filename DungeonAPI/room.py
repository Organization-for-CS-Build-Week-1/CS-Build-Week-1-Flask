# Implement a class to hold room information. This should have name and
# description attributes.
class Room:
    def __init__(self, name, description, id=0, x=None, y=None, n_to=None, s_to=None, e_to=None, w_to=None):
        self.id = id
        self.name = name
        self.description = description
        self.n_to = n_to
        self.s_to = s_to
        self.e_to = e_to
        self.w_to = w_to
        self.x = x
        self.y = y

    def __repr__(self):
        return (
            f"{{\n"
            f"\t\tid: {self.id},\n"
            f"\t\tname: {self.name},\n"
            f"\t\tdescription: {self.description},\n"
            f"\t\ty: {self.y},\n"
            f"\t\tx: {self.x},\n"
            f"\t\tn_to: {self.n_to},\n"
            f"\t\ts_to: {self.s_to},\n"
            f"\t\te_to: {self.e_to},\n"
            f"\t\tw_to: {self.w_to},\n"
            f"\t}}\n"
        )
    def get_exits(self):
        exits = []
        if self.n_to is not None:
            exits.append("n")
        if self.s_to is not None:
            exits.append("s")
        if self.w_to is not None:
            exits.append("w")
        if self.e_to is not None:
            exits.append("e")
        return exits
    def connect_rooms(self, direction, connecting_room):
        if direction == "n":
            self.n_to = connecting_room
            connecting_room.s_to = self
        elif direction == "s":
            self.s_to = connecting_room
            connecting_room.n_to = self
        elif direction == "e":
            self.e_to = connecting_room
            connecting_room.w_to = self
        elif direction == "w":
            self.w_to = connecting_room
            connecting_room.e_to = self
        else:
            print("INVALID ROOM CONNECTION")
            return None
    def get_room_in_direction(self, direction):
        if direction == "n":
            return self.n_to
        elif direction == "s":
            return self.s_to
        elif direction == "e":
            return self.e_to
        elif direction == "w":
            return self.w_to
        else:
            return None
    def get_coords(self):
        return [self.x, self.y]
