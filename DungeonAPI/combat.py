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

        start_time = datetime.datetime.now().timestamp()
        if id is None:
            self.id = int(start_time * 10 ** 7)
        else:
            self.id = id

    def determine_winner(self, player1_item_ids, player2_item_ids):
        """
        Determine winner and synthesize appropriate response

        Expects two lists of items; actual items, not models or other json code.
        """
        self.player1.in_combat = False
        self.player2.in_combat = False

        player1_set = { self.full_items.get(i, None) for i in player1_item_ids }
        player2_set = { self.full_items.get(i, None) for i in player2_item_ids }

        # Check that all of items are possible.
        if None in player1_set:
            return {"error":"Player 1 tried using items that neither player had."}
        if None in player2_set:
            return {"error":"Player 2 tried using items that neither player had."}
        
        player1_total_weight = sum([ i.weight for i in player1_set ])
        player1_total_score  = sum([ i.score  for i in player1_set ])
        player2_total_weight = sum([ i.weight for i in player2_set ])
        player2_total_score  = sum([ i.score  for i in player2_set ])

        if player1_total_weight > 100:
            return {"error":"Player 1 tried using items with too much total weight."}
        if player2_total_weight > 100:
            return {"error":"Player 2 tried using items with too much total weight."}
        
        if player1_total_score > player2_total_score:
            self.player1.items = { i.id:i for i in player1_set }
            self.player2.items = { i.id:i for i in player2_set.difference(player1_set) }
            self.room.items.update({ i.id:i for i in set(self.full_items.values()).\
                                                      difference(player1_set).\
                                                      difference(player2_set) })
            
            return {"outcome":"Player 1 wins the bout!"}

        elif player2_total_score > player1_total_score:
            self.player2.items = { i.id:i for i in player2_set }
            self.player1.items = { i.id:i for i in player1_set.difference(player2_set) }
            self.room.items.update({ i.id:i for i in set(self.full_items.values()).\
                                                      difference(player2_set).\
                                                      difference(player1_set) })
            
            return {"outcome":"Player 2 wins the bout!"}
            
        else: # Tie
            self.player2.items = { i.id:i for i in player2_set.difference(player1_set) }
            self.player1.items = { i.id:i for i in player1_set.difference(player2_set) }
            self.room.items.update({ i.id:i for i in set(self.full_items.values()).\
                                                      difference(player2_set).\
                                                      difference(player1_set) })
            
            return {"outcome":"The players tied!"}
