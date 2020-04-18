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
    def __init_(self):
        # Initialise the class without arguments
        # Inherit the parent init properties
        super().__init__()

        # Set additional properties
        self.turn = 0
        self.researched = {market:{produc:[amount, price]}}
        self.rumours = {market:{product:price}}
        self.inventory = {product:[amount, asset_cost]}
        self.goal_acheived = False  
        # visited node {node: times_visited}
        self.visited_node = defaultdict(int)
    
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
        update_rumours(info)

        # check inventory
        result1 = check_inventory()

        # check if goal acheieved
        goal_acheived = check_goal(result1)

        # check if goal exist in any of any researched/rumoured markets
        if not goal_acheived:

            # search for a market that player can afford
            togomarket = search_market(result1, gold)
            
            # next step
            nextstepstring = nextstep(currentnode, togomarket)

            if currentnode != nextstepstring:
                go_to = self.move_to(currentnode,nextstepstring)
                return (MOVE, go_to)
            # already at target market
            else:
                # check if market is researched
                if check_if_researched(location) == True:
                    # find out what we need to buy
                    buytuple = whattobuy(result1)
                    # buy
                    return (BUY, buytuple)
                else:
                    return (RESEARCH, None)

        else:
            return (PASS, None)

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
