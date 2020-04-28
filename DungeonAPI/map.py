import random
import time
from .room import Room, Tunnel, DeadEnd
from .constants.adjectives import adjectives
from .constants.places import places


class Map:
    def __init__(self, size, room_limit):
        self.grid = []
        row = [0] * size
        for i in range(size):
            row = row.copy()
            self.grid.append(row)
        self.locations = [''] * (len(adjectives) * len(places))
        i = 0
        for adjective in adjectives:
            for place in places:
                self.locations[i] = {"adjective": adjective, "place": place}
                i += 1
        self.center     = size // 2
        self.room_count = 0
        self.size       = size
        self.room_limit = room_limit
        self.rooms      = dict()
        self.set_grid(self.center, self.center)

    def get_loc_name(self):
        if not self.locations:
            return {"adjective": "invisible", "place": "nowhere"}
        idx = random.randint(0, len(self.locations)-1)
        loc_name = self.locations[idx]
        del self.locations[idx]
        return loc_name

    def to_title_case(self, string):
        chars = list(string)
        prev = ' '
        word_breaks = [' ', '-']
        for i in range(len(chars)):
            if prev in word_breaks:
                chars[i] = chars[i].upper()
            prev = chars[i]
        return ''.join(chars)

    def create_room(self, x, y, room_type, world=None):
        id          = int(f"{str(x)}{str(y)}")
        world_loc   = (x,y)
        if room_type == "dead-end":
            loc_name = {"place": "dead end", "adjective": None}
            return DeadEnd(world, world_loc, loc_name, id)
        elif room_type == "tunnel":
            loc_name = {"place": "tunnel", "adjective": None}
            return Tunnel(world, world_loc, loc_name, id)
        else:
            loc_name    = self.get_loc_name()
            title_adj   = self.to_title_case(loc_name["adjective"])
            title_place = self.to_title_case(loc_name["place"])
            name        = f"The {title_adj} {title_place}"
            description = f"Wow, this place is so {loc_name['adjective']}!"
            return Room(world, name, description, world_loc, loc_name, id)

    def set_grid(self, y, x):
        if self.grid[y][x] != 1:
            self.grid[y][x] = 1
            self.room_count += 1

    def generate_grid(self, map_seed = None):
        walkers = [
            Walker(self, 1, 2, self.center, self.center + 1),
            Walker(self, 2, 3, self.center + 1, self.center)
        ]
        if map_seed is None:
            grid_seed = random.randint(0, 10**6)
        else:
            grid_seed = map_seed
        random.seed(grid_seed)
        while self.room_count < self.room_limit:
            for walker in walkers:
                if self.room_count == self.room_limit:
                    break
                walker.move(self)
        return grid_seed

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

    def get_indef_article(self, string):
        vowels = ['a', 'e', 'i', 'o', 'u']
        stupid_exceptions = ['union', 'university', 'united', 'uniform']
        string = string.lower()
        if string[0] in vowels and string not in stupid_exceptions:
            return 'an'
        else:
            return 'a'

    def get_descriptions(self):
        for coords, room in self.rooms.items():
            if isinstance(room, Tunnel) or isinstance(room, DeadEnd):
                continue
            neighbors = {
                "north": self.rooms.get((coords[0], coords[1]-1)),
                "south": self.rooms.get((coords[0], coords[1]+1)),
                "east":  self.rooms.get((coords[0]+1, coords[1])),
                "west":  self.rooms.get((coords[0]-1, coords[1]))
            }
            desc_strings = []
            for direction, neighbor in neighbors.items():
                if neighbor:
                    article = self.get_indef_article(neighbor.loc_name["place"])
                    desc_strings.append(f"to the {direction} is {article} {neighbor.loc_name['place']}")
            for i, string in enumerate(desc_strings):
                length = len(desc_strings)
                if i == 0:
                    desc_strings[i] = ' ' + string[:1].upper() + string[1:]
                if i < length-1 and length > 2:
                    desc_strings[i] += ','
                elif i == length-1:
                    desc_strings[i] += '.'
            desc_strings.insert(-1, 'and')
            room.description += ' '.join(desc_strings)

    def generate_rooms(self, world=None):
        room_count = 0
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 1:
                    neighbors = self.get_neighbors(i, j)
                    if len(neighbors) == 1:
                        room_type = 'dead-end'
                    elif len(neighbors) > 2:
                        room_type = 'room'
                    else:
                        corner = self.get_corner_type(neighbors)
                        if corner and self.has_inside_diag_neighbor(corner, i, j):
                            room_type = 'room'
                        else:
                            room_type = 'tunnel'
                    self.rooms[(j,i)] = self.create_room(j, i, room_type, world)
                    room_count += 1
        self.get_descriptions()
        return self.rooms

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
    def __init__(self, map, mode, rand_factor, y=0, x=0):
        self.y    = y
        self.x    = x
        self.mode = mode % 4
        self.rand_factor = rand_factor
        map.set_grid(y, x)
        # modes map as follows:
        # 0 => up
        # 1 => right
        # 2 => down
        # 3 => left

    def move(self, map):
        map_size = map.size - 1
        action   = random.randint(0, self.rand_factor)
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
