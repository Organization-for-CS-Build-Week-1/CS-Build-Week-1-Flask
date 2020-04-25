import random
import time
from DungeonAPI.room import Room

class Map:
    def __init__(self, size, room_limit):
        self.grid = []
        row = [0] * size
        for i in range(size):
            row = row.copy()
            self.grid.append(row)
        self.center     = size//2
        self.room_count = 0
        self.size       = size
        self.room_limit = room_limit
        self.rooms      = dict()
        self.set_room(self.center, self.center)

    def create_room(self, y, x):
        id          = int(f"{str(y)}{str(x)}")
        name        = f"Room #{id}"
        description = f"The description for {name}."
        return Room(name, description, id, x, y)

    def set_room(self, y, x):
        if self.grid[y][x] != 1:
            self.grid[y][x] = 1
            self.room_count += 1
            self.rooms.update({(y, x): self.create_room(y, x)})

    def generate_rooms(self):
        walkers = [
            Walker(self, 0, self.center-1, self.center),
            Walker(self, 1, self.center, self.center+1),
            Walker(self, 2, self.center+1, self.center),
            Walker(self, 3, self.center, self.center-1),#
        ]
        while self.room_count < self.room_limit:
            for walker in walkers:
                if self.room_count == self.room_limit:
                    break
                walker.move(self)
        return self.rooms

    def print_grid(self):
        for row in self.grid:
            row_str = ''
            for item in row:
                if item == 1:
                    item_str = "\x1b[1;33m1"
                else:
                    item_str = "\x1b[1;34m0"
                row_str += item_str
            print(row_str)

class Walker:
    def __init__(self, map, mode, y=0, x=0):
        self.y    = y
        self.x    = x
        self.mode = mode % 4
        map.set_room(y, x)
        # modes map as follows:
                # 0 => up 
                # 1 => right 
                # 2 => down 
                # 3 => left

    def move(self, map):
        map_size = map.size-1
        action   = random.randint(0,2)
        if action == 0:
            self.mode = (self.mode + 1) % 4
        if self.mode == 0 and self.y > 0:
            self.y -= 1
            map.set_room(self.y, self.x)
        elif self.mode == 1 and self.x < map_size:
            self.x += 1
            map.set_room(self.y, self.x)
        elif self.mode == 2 and self.y < map_size:
            self.y += 1
            map.set_room(self.y, self.x)
        elif self.mode == 3 and self.x > 0:
            self.x -= 1
            map.set_room(self.y, self.x)