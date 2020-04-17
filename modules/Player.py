"""
Player class for the Market Royale game.

This module creates a player for the Market Royale game.
The player can do one of the following at the end of each turn:
 |Research current market.
 |Buy (product, amount) from current market.
 |Sell (product, amount) to current market.
 |Move to adjacent (market) from current market.
 |Pass turn and do nothing.

At the start of each turn, the player will:
 |Take stock of current inventory.
 |Take stock of current gold.
 |Tally gold on most recent previous market event.
 |Tally gold on most recent previous market colour change (if present).
 |Tally gold on most recent previous overdraft event.
 |Check glossary of researched information.
 |Check glossary of rumoured information. Rumours are information from other players.

Authors: Syndicate 8 - MBusA2020 Module 2

         Renee He            (h.he13@student.unimelb.edu.au)
         Joshua Xujuang Lin  (xujiang.lin@student.unimelb.edu.au)
         Ellie Meng          (h.meng2@student.unimelb.edu.au)
         Isaac Pang          (i.pang2@student.unimelb.edu.au)
         Tann Tan            (h.tan49@student.unimelb.edu.au)
         Grace Zhu           (grace.zhu@student.unimelb.edu.au)

TODO List:
    - Literally everything

Dream TODO List:
    - Machine Learning to predict where to go, maybe
    - A*/BFS for optimisation of movement
"""


import Command
from BasePlayer import Baseplayer
from collections import defaultdict, deque


class Player(BasePlayer):
    def __init_(self):
        # Initialise the class without arguments
        # Inherit the parent init properties
        super().__init__()

        # Set additional properties
        self.turn = 0
        self.researched = {}
        self.rumours = {}
        self.inventory = {}

