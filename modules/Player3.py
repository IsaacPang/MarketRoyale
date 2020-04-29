"""
 __    __  ______  ______  __  __   ______  ______
/\ "-./  \/\  __ \/\  == \/\ \/ /  /\  ___\/\__  _\
\ \ \-./\ \ \  __ \ \  __<\ \  _"-.\ \  __\\/_/\ \/
 \ \_\ \ \_\ \_\ \_\ \_\ \_\ \_\ \_\\ \_____\ \ \_\
  \/_/  \/_/\/_/\/_/\/_/ /_/\/_/\/_/ \/_____/  \/_/
 ______  ______  __  __  ______  __      ______
/\  == \/\  __ \/\ \_\ \/\  __ \/\ \    /\  ___\
\ \  __<\ \ \/\ \ \____ \ \  __ \ \ \___\ \  __\
 \ \_\ \_\ \_____\/\_____\ \_\ \_\ \_____\ \_____\
  \/_/ /_/\/_____/\/_____/\/_/\/_/\/_____/\/_____/


Player class for the Market Royale game.

This module creates a player for the Market Royale game.
The player is modelled after a rational buyer with imperfect information of the market.

At the start of the game, the player will venture towards the external areas of the map,
while collecting information along the way to increase the library of market information the player stores.
Upon reaching a threshold, the player will calculate statistics of the markets to maximise profits.

To maximise profits, the player will visit the markets that have products for sale with prices under the 25th percentile
of prices of markets known. The player will then visit the markets that will buy the products with prices over 75th
percentile of prices of markets known.

The statistics of the market will update every turn as the player gains more information from passing players.

The player will also blacklist markets that have nothing for sale of a given product to inform decision making.

To avoid going into negative gold, the player will dump any acquired stock before proceeding with any other strategy.

The player is also very risk averse, preferring to avoid black and grey markets entirely. Since grey markets turn
black the next turn, the player is effectively treating grey markets as black markets.

At the start of each turn, the player will:
 |Take stock of current inventory.
 |Take stock of current gold.
 |Check glossary of market information
 |Update statistics on the markets
 |Decide on the strategies available, what to do with information

Given the information, the player can do one of the following at the end of each turn:
 |Research current market.
 |Buy (product, amount) from current market, and update inventory and gold.
 |Sell (product, amount) to current market, and update inventory and gold.
 |Move to adjacent (market) from current market.
 |Pass turn and do nothing.

Authors: Syndicate 8 - MBusA2020 Module 2
             Isaac Pang          (i.pang2@student.unimelb.edu.au)
             Tann Tan            (h.tan49@student.unimelb.edu.au)
             Renee He            (h.he13@student.unimelb.edu.au)
             Ellie Meng          (h.meng2@student.unimelb.edu.au)
             Grace Zhu           (grace.zhu@student.unimelb.edu.au)
             Joshua Xujuang Lin  (xujiang.lin@student.unimelb.edu.au)
"""

import Command
from BasePlayer import BasePlayer
from collections import defaultdict
from operator import attrgetter


class Player(BasePlayer):
    """
    Player class for the Market Royale game.
    What are the player's priorities:
    1. Avoid loss of gold from black markets
    2.
    """
    # -------------------- #
    #  Market Class Start  #
    # -------------------- #
    class PlayerMarket:
        def __init__(self, name):
            self.prices = defaultdict(list)
            self.amounts = defaultdict(list)
            self.name = name
            self.researched = False
            self.neighbours = {}

    # sorting classes in a collection by attribute:
    # In place: list.sort(key=attrgetter('attribute'), reverse=True)
    # Getting the first item in a collection by attribute:
    # Generator: next((x for x in list if x.value == value), None) # returns None if no exact match found.
    # Filter: next(filter(lambda x: x.value == value, list)) # an exact match must be found, raises an error otherwise.

    # ------------------ #
    #  Market Class End  #
    # ------------------ #

    def __init__(self):
        # Inherit the parent class init items before defining own.
        super().__init__()


