from .room import Room
from .player import Player
from .item import Item
from .map import Map

import datetime


class Combat:
    """ A class for managing combat functionality """

    def __init__(self, player1, player2, room, id = None):
        player1.in_combat = True
        player2.in_combat = True

        self.player1 = player1
        self.player2 = player2
        self.room = room

        self.full_items = {}
        self.full_items.update(player1.items)
        self.full_items.update(player2.items)

        self.player1_set = set()
        self.player2_set = set()

        self.start_time = datetime.datetime.now().timestamp()
        if id is None:
            self.id = int(start_time * 10 ** 7)
        else:
            self.id = id

    def check_status(self):
        if datetime.datetime.now().timestamp() - self.start_time > 30:
            return self.determine_winner(player1_item_ids, player2_item_ids)
        else:
            response = {"combat":f"Combat is still going between {self.player1.username} and  {self.player2.username}."}
            return response

    def determine_winner(self):
        """
        Determine winner and synthesize appropriate response

        Expects two lists of items; actual items, not models or other json code.
        """
        self.player1.in_combat = False
        self.player2.in_combat = False
        
        player1_total_score  = sum([ i.score for i in self.player1_set ])
        player2_total_score  = sum([ i.score for i in self.player2_set ])
        
        if player1_total_score > player2_total_score:
            self.player1.items = { i.id:i for i in self.player1_set }
            self.player2.items = { i.id:i for i in self.player2_set.difference(self.player1_set) }
            self.room.items.update({ i.id:i for i in set(self.full_items.values()).\
                                                      difference(self.player1_set).\
                                                      difference(self.player2_set) })
            
            return {"outcome":"Player 1 wins the bout!"}

        elif player2_total_score > player1_total_score:
            self.player2.items = { i.id:i for i in self.player2_set }
            self.player1.items = { i.id:i for i in self.player1_set.difference(self.player2_set) }
            self.room.items.update({ i.id:i for i in set(self.full_items.values()).\
                                                      difference(self.player2_set).\
                                                      difference(self.player1_set) })
            
            return {"outcome":"Player 2 wins the bout!"}
            
        else: # Tie
            self.player2.items = { i.id:i for i in self.player2_set.difference(self.player1_set) }
            self.player1.items = { i.id:i for i in self.player1_set.difference(self.player2_set) }
            self.room.items.update({ i.id:i for i in set(self.full_items.values()).\
                                                      difference(self.player2_set).\
                                                      difference(self.player1_set) })
            
            return {"outcome":"The players tied!"}
