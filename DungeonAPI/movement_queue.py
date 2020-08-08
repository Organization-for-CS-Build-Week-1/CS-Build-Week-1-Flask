import time
from flask_socketio import emit
import DungeonAPI


class MovementQueue:

    def __init__(self):
        self.moves = []
        self.isTicking = False
        self.tick = 0.015
        self.time1 = time.time()

    def add(self, item):
        self.moves.append(item)
        time2 = time.time()
        if time2 - self.time1 > self.tick:
            self.time1 = time2
            self.move_all_and_emit()

    def move_all_and_emit(self):

        moves = [*self.moves]
        self.moves = []

        worldy_moves = {}

        for move in moves:
            player    = move[0]
            vx        = move[1]
            vy        = move[2]
            player.move(vx, vy)
            world_loc = player.world_loc

            if world_loc not in worldy_moves:
                worldy_moves[world_loc] = {}

            worldy_moves[world_loc][player.auth_key] = player.room_loc
        
        for world_loc in worldy_moves:
            emit("movementupdate", worldy_moves[world_loc], room=str(world_loc))
