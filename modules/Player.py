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


class Player(BasePlayer):
    def __init__(self):
        # Initialise the class without arguments
        # Inherit the parent init properties
        super().__init__()

        # Set additional properties
        self.turn = 0
        self.researched = {}
        self.rumours = {}
        self.inventory = {}
        self.loc = ''
    
    def take_turn(self, location, prices, info, bm, gm):
        '''Player takes a turn with (hopefully) informed choices.
        Player can take any one of the following turns:
        - Research current market
        - Buy from market
        - Sell to market
        - Move to adjacent market
        - Pass turn
        '''
        return Command.PASS, None

    def __repr__(self):
        '''Define the representation of the Player as the state of 
        current attributes.
        '''
        s = str(self.__dict__)
        return s

    def best_path(self, target):
        """Finds the fastest path by employing a breadth-first search algorithm.
        Since all edges are currently unweighted, only simplified breadth-first
        while storing each previous node is required
        """
        # TODO: need to update location before calling function
        # TODO: This is not the best path, this is the path with the fewest turns.
        # TODO: Update this with a check if the intermediary nodes are black or grey markets
        # Set the starting location as the player's current location
        start = self.loc

        # Collect all the nodes in the given map
        nodes = self.map.get_node_names()
        assert(target in nodes, "Target node not found in map")

        # Since it is a BFS, all nodes necessarily have one previous node. This is required for the backtracking later
        # All nodes will have a not None node except the starting node
        # Example: None -> A -> B -> C :: Backtrack None <- A <- B <- C
        previous = {node: None for node in nodes}

        # Must only visit every node exactly once for a BFS
        # Set current market as visited
        visited = {node: False for node in nodes}
        visited[start] = True

        # Create a queue data structure for markets to visit. A queue is required for FIFO, we want to analyse all
        # neighbouring nodes of the current node before we proceed
        queue = deque([start])

        # Start looping through the map from the current node
        while True:
            # Identify the currently assessed node
            current = queue.pop()

            # If the current node is the target node, we are done we need to backtrack to the start to create the path
            # to avoid re-sorting a list, we need a structure that would show the path from start to end, left -> right
            if current == target:
                path = deque()
                while current:
                    path.appendleft(current)
                    current = previous[current]

                return path

            # Collect the neighbours of this market and iterate over them
            neighbours = self.map.get_neighbours(current)
            for n in neighbours:
                # if the neighbours have not been visited, add them to the queue.
                # Set the current node as the previous node for all neighbours.
                if not visited[n]:
                    queue.appendleft(n)
                    visited[n] = True
                    previous[n] = current


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

    p = Player()
    p.set_map(test_map)
    p.loc = 'A'
    target = 'E'
    print(f"Player is at {p.loc}. Best path to {target} is {list(p.best_path(target))}")


if __name__ == "__main__":
    main()
