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

At the start of each turn, the player will:
 |Take stock of current inventory.
 |Take stock of current gold.
 |Tally gold on most recent previous market event.
 |Tally gold on most recent previous market colour change (if present).
 |Tally gold on most recent previous overdraft event.
 |Check glossary of researched information.
 |Check glossary of rumoured information. Rumours are information from other players.

Given the information, the player can do one of the following at the end of each turn:
 |Research current market.
 |Buy (product, amount) from current market.
 |Sell (product, amount) to current market.
 |Move to adjacent (market) from current market.
 |Pass turn and do nothing.

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
from BasePlayer import BasePlayer
from collections import defaultdict, deque
from operator import itemgetter as ig
from random import sample


class Player(BasePlayer):
    def __init__(self):
        # Initialise the class without arguments
        # Inherit the parent init properties
        super().__init__()

        # Set additional properties
        self.turn = 0               # how many turns taken in game:     0,1,..*
        self.researched = {}        # market intel from other players:  {market:{produc:[amount, price]}}
        self.rumours = {}           # market intel from other players:  {market:{produc:[amount, price]}}
        self.inventory = {}         # record items in inventory:        {product:[amount, asset_cost]}
        self.gold = 0               # gold.                             0,1,..*
        self.score = 0              # score from inventory and gold:    0,1,..*
        self.goal_acheived = False  # indicates whether goal acheived:  True/False
        self.visited_node = defaultdict(int)  # location visit counts:  {location: times_visited}
        
    
    def take_turn(self, location, prices, info, bm, gm):
        '''Player takes a turn with (hopefully) informed choices.
        Player can take any one of the following turns:
        - Research current market
        - Buy from market
        - Sell to market
        - Move to adjacent market
        - Pass turn
        '''

        # collect information from other player
        collect_rumours(info)

        # check if goal acheieved
        goal_acheived = check_goal(self.inventory, self.goal_acheived)

        # do nothing if goal achieved
        if goal_acheived:
            return (PASS, None)

        # basic strategy if not yet acheive goal
        else:

            # search for a market that player can afford
            destination = search_market(self.inventory, self.gold, self.goal)

            # whats the next step to reach destination
            next_step = get_next_step(location, destination)

            # take next step to reach destination if any
            if next_step != None:
                go_to = self.move_to(location, destination)
                return (MOVE, go_to)

            # already at destination:
            else:
                # reseach market if haven't
                if not location in self.researched:
                    self.researched[location] = info
                    return (RESEARCH, location)
                
                else:
                    # find out what we need to buy:
                    to_buy = purchase(self.inventory, self.gold, prices)

                    return (BUY, to_buy)
               
                    

    # check if goal acheived by comparing goal with inventory
    def check_goal(inventory, goal):
        return None

    # search for a market to go to
    def search_market(self.inventory, self.gold, self.goal):
        return None

    # get next step (BFS)
    def get_next_step(location, destination):
        return None

    # select and purchase and item form market (update self inventory and gold)
    # return (item, quantity) to buy
    def purchase(inventory, gold, prices):
        return None

    # player moves. update self location and return that location.
    def move_to(self, start, end):
        '''Player moves to end node from start node.
        If end node is not in start node's neighbours, move to random unvisited neighbour
        '''
        self.visited_node[currentnode] += 1
        neighbours = check_neighbours(start)
        if end not in neighbours:
            min_visited = min(self.visited_node.items(), key=ig(1))
            for neighbour in neighbours:
                if self.visited_node.get(neighbour) and neighbour == min_visited[0]:
                    return neighbour
            return sample(neighbours)
        else:
            return end



    def __repr__(self):
        '''Define the representation of the Player as the state of 
        current attributes.
        '''
        s = str(self.__dict__)
        return s
        

if __name__ == "__main__":
    print(Player())
