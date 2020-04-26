import random
import time
from DungeonAPI.room import Room, Tunnel, DeadEnd


class Map:
    def __init__(self, size, room_limit):
        self.grid = []
        row = [0] * size
        for i in range(size):
            row = row.copy()
            self.grid.append(row)
        self.center     = size // 2
        self.room_count = 0
        self.size       = size
        self.room_limit = room_limit
        self.rooms      = dict()
        self.set_grid(self.center, self.center)

    def create_room(self, x, y, room_type):
        id          = int(f"{str(y)}{str(x)}")
        world_loc   = (x,y)
        name        = f"Room #{id}"
        description = f"The description for {name}."
        if room_type == "dead-end":
            return DeadEnd(None, world_loc, id)
        elif room_type == "tunnel":
            return Tunnel(None, world_loc, id)
        else:
            return Room(None, name, description, world_loc, id)

    def set_grid(self, y, x):
        if self.grid[y][x] != 1:
            self.grid[y][x] = 1
            self.room_count += 1

    def generate_grid(self):
        walkers = [
            Walker(self, 0, self.center - 1, self.center),
            Walker(self, 1, self.center, self.center + 1),
            Walker(self, 2, self.center + 1, self.center),
            Walker(self, 3, self.center, self.center - 1),
        ]
        while self.room_count < self.room_limit:
            for walker in walkers:
                if self.room_count == self.room_limit:
                    break
                walker.move(self)

    def get_neighbors(self, i, j):
        neighbors = []
        if i > 0 and self.grid[i-1][j] == 1:
            neighbors.append('n')
        if i < self.size-1 and self.grid[i+1][j] == 1:
            neighbors.append('s')
        if j < self.size-1 and self.grid[i][j+1] == 1:
            neighbors.append('e')
        if j > 0 and self.grid[i][j-1] == 1:
            neighbors.append('w')
        return neighbors
    
    def get_corner_type(self, neighbors):
        if len(neighbors) != 2:
            return None
        neighbor_str = ''.join(neighbors)
        if neighbor_str == 'ns' or neighbor_str == 'ew':
            return None
        else:
            return neighbor_str
        
    def has_inside_diag_neighbor(self, corner_type, i, j):
        bound = self.size-1
        switcher = {
            "ne": i > 0     and j < bound and self.grid[i-1][j+1],
            "nw": i > 0     and j > 0     and self.grid[i-1][j-1],
            "se": i < bound and j < bound and self.grid[i+1][j+1],
            "sw": i < bound and j > 0     and self.grid[i+1][j-1],
        }
        return switcher.get(corner_type) == 1

    def generate_rooms(self):
        for i in range(self.size):
            for j in range(self.size):
                neighbors = self.get_neighbors(i, j)
                if len(neighbors) == 1:
                    room = self.create_room(j, i, 'dead-end')
                elif len(neighbors) > 2:
                    room = self.create_room(j, i, 'room')
                else:
                    corner = self.get_corner_type(neighbors)
                    if corner and self.has_inside_diag_neighbor(corner, i, j):
                        room = self.create_room(j, i, 'room')
                    else:
                        room = self.create_room(j, i, 'tunnel')
                self.rooms.update({(j,i): room})

    def print_grid(self):
        for i, row in enumerate(self.grid):
            row_str = ''
            for j, item in enumerate(row):
                if item == 1:
                    room = self.rooms.get((j,i))
                    if isinstance(room, Tunnel):
                        item_str = "\x1b[1;32m1"
                    elif isinstance(room, DeadEnd):
                        item_str = "\x1b[1;35m1"
                    else:
                        item_str = "\x1b[1;33m1"
                else:
                    item_str = "\x1b[1;30m0"
                row_str += item_str
            print(row_str)


class Walker:
    def __init__(self, map, mode, y=0, x=0):
        self.y    = y
        self.x    = x
        self.mode = mode % 4
        map.set_grid(y, x)
        # modes map as follows:
        # 0 => up
        # 1 => right
        # 2 => down
        # 3 => left

    def move(self, map):
        map_size = map.size - 1
        action   = random.randint(0, 2)
        if action == 0:
            self.mode = (self.mode + 1) % 4
        if self.mode == 0 and self.y > 0:
            self.y -= 1
            map.set_grid(self.y, self.x)
        elif self.mode == 1 and self.x < map_size:
            self.x += 1
            map.set_grid(self.y, self.x)
        elif self.mode == 2 and self.y < map_size:
            self.y += 1
            map.set_grid(self.y, self.x)
        elif self.mode == 3 and self.x > 0:
            self.x -= 1
            map.set_grid(self.y, self.x)
