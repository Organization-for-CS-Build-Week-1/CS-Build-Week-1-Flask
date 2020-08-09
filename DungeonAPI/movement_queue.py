import time
from flask_socketio import emit
import DungeonAPI


class Ticker:

    def __init__(self, tick):
        self.tick = tick
        self.current = time.time()

    def did_tick(self):
        now = time.time()
        if now - self.current > self.tick:
            self.current = now
            return True
        return False

