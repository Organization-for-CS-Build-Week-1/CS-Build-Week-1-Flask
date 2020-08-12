import time
from flask_socketio import emit
import DungeonAPI


class Ticker:

    def __init__(self, tick):
        self.tick = tick
        self.current = time.time()

    def get_ticks_and_update(self):
        now = time.time()
        ticks_passed = int((now - self.current) // self.tick)
        if ticks_passed > 0:
            self.current = now
        return ticks_passed
