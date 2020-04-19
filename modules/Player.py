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
        self.turn = 0                           # how many turns taken in game:     0,1,..*
        self.researched = {}                    # intel from research:              {market:{product:[amount, price]}}
        self.rumours = {}                       # intel from other players:         {market:{product:[amount, price]}}
        self.inventory = {}                     # record items in inventory:        {product:[amount, asset_cost]}
        self.gold = 0                           # gold:                             0,1,..*
        self.score = 0                          # score from inventory and gold:    0,1,..*
        self.goal_acheived = False              # indicates whether goal achieved:  True/False
        self.visited_node = defaultdict(int)    # location visit counts:            {location: times_visited}
        self.loc = ''                           # player's current location:        str(market location)

    #TODO _________________________________________________________________________________
    # Add logic for selling. Most of it will be reverse of buying so leave it for now.
    #______________________________________________________________________________________
    def take_turn(self, location, prices, info, bm, gm):
        '''Player takes a turn with (hopefully) informed choices.
        Player can take any one of the following turns:
        - Research current market
        - Buy from market
        - Sell to market
        - Move to adjacent market
        - Pass turn
        '''

        # define the player location
        self.loc = location

        # collect information from other player
        self.collect_rumours(info)

        # check if goal achieved
        self.goal_acheived = self.check_goal(self.inventory, self.goal)

        # if goal acheived
        if self.goal_acheived:
            return Command.PASS, None

        # basic strategy if not yet acheive goal
        else:
            # search for a market that player can afford
            destination = self.search_market_buy(self.inventory, self.gold, self.goal)

            # obtains the next step and the path to the target destination
            # the target path will be required for some optimisation in future
            next_step, target_path = self.get_next_step(destination)

            # take next step to reach destination if any
            if next_step:
                return Command.MOVE, next_step

            # already at destination:
            else:
                # reseach market if haven't
                if not location in self.researched:
                    self.researched[location] = info
                    return Command.RESEARCH, location
                
                else:
                    # find out what we need to buy and proceed
                    to_buy = self.purchase(self.inventory, self.gold, prices)

                    return Command.BUY, to_buy

    #TODO ______________________________________________________________________________________ 
    # Complete the functions below. Please add/remove additional arguments as you need.
    # Think of possible test cases for each of them too.
    # __________________________________________________________________________________________
    def collect_rumours(self, info):
        """Collect intel from other players at the same location, then store it in self.rumours.
        Args:
            info : { market : {product:price} }
                    dictionary of information from other players
            Output: None

        """
        pass


    def check_goal(self, inventory, goal):
        """Check if goal is acheived by comparing inventory and goal. 
           Switch self.acheived_goal = True if acheived goal.
        Args:
            inventory : {product : price}
                    dictionary of products in inventory.
            goal : {product : price}
                    dictionary of products required to acheive goal.
            Output: None
        """

        pass


    def search_market(self, inventory, gold, location):
        """Given current location, inventory, gold, and goal, what is the best market to buy from.
           What market to choose if doesn't have any researched/rumoured information?
           Feel free to improvise and document the details here.
        Args:
            inventory : {product : price}
                    dictionary of products in inventory.
            goal : {product : price}
                    dictionary of products required to acheive goal.
            gold : int
                    How many gold the player has currently.
            Output: None
        """
        pass


    def purchase(self, inventory, gold, prices):
        """Return the item and anoubt to buy when player is at a destination market.
           Update self inventory and gold too before returning.
        Args:
            inventory : {product : price}
                    dictionary of products in inventory.
            goal : {product : price}
                    dictionary of products required to acheive goal.
            prices : {product : price}
                    prices of item in the market.
            Output: (product, amount)
        """
        return None


    def compute_score(self, inventory, gold, goal):
        """Compute and return score.
        Args:
            inventory : {product : price}
                    dictionary of products in inventory.
            goal : {product : price}
                    dictionary of products required to acheive goal.
            gold : int
                    How many gold the player has currently.
            Output: score (int)
        """
        pass


    def get_next_step(self, target):
        """Finds the fastest path by employing a breadth-first search algorithm.
        Since all edges are currently unweighted, only simplified breadth-first
        while storing each previous node is required
        """
        # TODO: need to update location before calling function
        # TODO: This is not the best path, this is the path that takes the fewest turns.
        # TODO: Update this with a check if the intermediary nodes are black or grey markets
        # Set the starting location as the player's current location
        start = self.loc
        # Collect all the nodes in the given map
        nodes = self.map.get_node_names()
        assert target in nodes, "Target node not found in map"
        # Since it is a BFS, all nodes necessarily have one previous node. This is required for the backtracking later
        # All nodes will have a not None node except the starting node
        # Example: None -> A -> B -> C :: Backtrack None <- A <- B <- C
        previous = {node: None for node in nodes}
        # Must only visit every node exactly once for a BFS
        # Set current market as visited
        visited = {node: False for node in nodes}
        visited[start] = True
        # Create a queue data structure for markets to visit. A queue is required for FIFO, we want to analyse all
        # neighbouring nodes of the current node before we proceed.
        queue = deque([start])
        # Start looping through the map from the current node.
        while queue:
            # Identify the currently assessed node
            current = queue.pop()
            # If the current node is the target node, we are done we need to backtrack to the start to create the path
            # to avoid re-sorting a list, we need a structure that would show the path from start to end, left -> right.
            # We want to return the path and the steps taken to reach the target node.
            if current == target:
                path = deque()
                while current:
                    path.appendleft(current)
                    current = previous[current]
                # path provides the nodes to traverse in order, so the next node is the best next step
                return path[1], path
            # Collect the neighbours of this market and iterate over them.
            neighbours = self.map.get_neighbours(current)
            for n in neighbours:
                # If the neighbours have not been visited, add them to the queue.
                # Set the current node as the previous node for all neighbours.
                if not visited[n]:
                    queue.appendleft(n)
                    visited[n] = True
                    previous[n] = current
    #____________________________________________________________________________________________ 
    #                                       END TODO
    # ___________________________________________________________________________________________


    def __repr__(self):
        '''Define the representation of the Player as the state of
        current attributes.
        '''
        s = str(self.__dict__)
        return s


# Write a main function for testing
def main():
    import unittest
    import random
    from time import time
    from Map import Map
    import string

    map_width = 200
    map_height = 100
    resolution_x = 2
    resolution_y = 3

    node_list = list(string.ascii_uppercase)[:10]
    # keep a list of good seeds
    good_seeds = [23624]
    test_map = Map(node_list, map_width, map_height, resolution_x, resolution_y, seed=good_seeds[0])

    print('map_data["node_positions"]\n')
    test_map.pretty_print_node_positions()
    print('map_data["node_graph"]\n')
    test_map.pretty_print_node_graph()

    test_map.pretty_print_map()

    t1 = time()
    p = Player()
    p.set_map(test_map)
    p.loc = 'A'
    target = 'E'
    next_step, path = p.get_next_step(target)
    turns_req = len(path)
    t2 = time()
    interval = t2 - t1
    print(f"Player is at {p.loc}. The quickest path to {target} takes {turns_req} turns.")
    print(f"The next stpe on the path {path} is")
    print(f"Time taken {interval} seconds")


if __name__ == "__main__":
    main()
