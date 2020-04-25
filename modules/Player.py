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
    - Refer to code comments
    - Update docstrings

Dream TODO List:
    - Machine Learning to predict where to go, maybe
    - A*/BFS for optimisation of movement
"""

import Command
from BasePlayer import BasePlayer
from collections import defaultdict, deque
import random
import math


class Player(BasePlayer):
    def __init__(self):
        # Initialise the class without arguments
        # Inherit the parent init properties
        super().__init__()

        # Set additional properties
        self.turn = 0                           # how many turns taken in game:     0,1,..*
        self.researched = set()                 # researched markets:               set({market1, market2..})
        self.market_prices = {}                 # market prices from self/players:  {market:{product:[amount, price]}}
        self.inventory = {}                     # record items in inventory:        {product:[amount, asset_cost]}
        self.gold = 0                           # gold:                             0,1,..*
        self.score = 0                          # score from inventory and gold:    0,1,..*
        self.goal_achieved = False              # indicates whether goal achieved:  True/False
        self.visited_node = defaultdict(int)    # location visit counts:            {location: times_visited}
        self.loc = ''                           # player's current location:        str(market location)
        self.bonus = 10000
        self.ctr = ''
        self.target_loc = ''


    # TODO _________________________________________________________________________________
    # Add logic for selling. Most of it will be reverse of buying so leave it for now.
    # ______________________________________________________________________________________
    def take_turn(self, location, prices, info, bm, gm):
        """Player takes a turn with (hopefully) informed choices.
        Player can take any one of the following turns:
        - Research current market
        - Buy from market
        - Sell to market
        - Move to adjacent market
        - Pass turn
        Args:
            location (str): Current player location as a string
            prices (dict): The market's current prices after turn order correction
                           {product: (price, amount)}
            info (dict): Prices of products from random markets from other players
                         {market: {product: price}}
            bm (list): A list of all nodes that are currently black markets
            gm (list): A list of all nodes that are currently grey markets
        Output:
            cmd (tup): A tuple of (Command.CMD, data)
        """
        # Increase turn counter
        self.turn += 1

        # define the player location
        self.loc = location

        # add information from current market
        self.save_market_prices(self.market_prices, prices)

        # collect information from other player
        self.collect_rumours(info)

        # check if goal achieved
        self.goal_acheived = self.check_goal(self.inventory, self.goal)

        # Determine current strategy
        cmd = self.get_strategy(self.turn, info, bm, gm)

        return cmd

        # # if goal achieved, move to the market closest to the centre of the map
        # # Then do nothing
        # if self.goal_acheived:
        #     # invoke the function to find the central market
        #     destination = self.central_market(self.map)
        #     next_step, target_path = self.get_next_step(destination)
        #     if next_step:
        #         return Command.MOVE_TO, next_step
        #     else:
        #         return Command.PASS, None
        #
        # # basic strategy if not yet acheive goal
        # else:
        #     # search for a market that player can afford
        #     destination = self.search_market(self.inventory, self.gold, self.goal)
        #
        #     # obtains the next step and the path to the target destination
        #     # the target path will be required for some optimisation in future
        #     next_step, target_path = self.get_next_step(destination)
        #     # If the function returns a next step, player must go to the next step.
        #     # Otherwise, the player is already at the destination. Determine if research is required.
        #     if next_step:
        #         return Command.MOVE_TO, next_step
        #
        #     else:
        #         # reseach market if haven't
        #         if location not in self.researched:
        #             self.researched.append(location)
        #             return Command.RESEARCH, location
        #         else:
        #             # find out what we need to buy and proceed
        #             to_buy = self.purchase(self.inventory, self.gold, prices)
        #             return Command.BUY, to_buy

    # TODO ______________________________________________________________________________________
    # Complete the functions below. Please add/remove additional arguments as you need.
    # Think of possible test cases for each of them too.
    # __________________________________________________________________________________________

    def get_strategy(self, turn, bm_list, gm_list):
        """Returns a function that dictates the player's current strategy
        Args:
            turn (int): The current turn
            bm_list (list): List of black markets passed from take_turn
            gm_list (list): List of grey markets passed from take_turn
        Output:
            cmd (tup): A tuple of Command.CMD, data, output by children functions
        """
        if turn == 1:
            return self.first_turn(bm_list, gm_list)
        else:
            return Command.PASS, None

    def first_turn(self, bm, gm):
        """The set of instructions on the first turn of the player.
        The player must get a sense of the map by following these steps.
        1. Store the central market on the map.
        2. Set the furthest node from the central market as target node.
        3. Find the fastest path to the target.
        4. Set the next node as the next step.
        5. If the current location is a terminal node, switch to research strat.
        Args:
            bm (list): Current list of black markets
            gm (list): Current list of grey markets
        Output:
            cmd (tup): A tuple of (Command.CMD, data)
        """
        # Set the central market
        self.ctr, distances = central_market()

        # Determine the furthest node from the central market
        t1_target = max(distances, key=distances.get)

        # If we are already at the maximum node, research the node
        if self.loc == t1_target:
            return Command.RESEARCH, None

        # Find the first, random white market closest to the target market
        # This is done recursively until a white market is found
        # On turn 1, white markets are expected
        def first_white(tm, map_obj, bg_set, assessed=set()):
            # return the target market if it is a white market
            if tm not in bg_set:
                return tm

            # get the neighbours of the target market that have not been assessed
            # if this set less the black/grey market set is not empty,
            # return a random target location
            neighbour_set = set(map_obj.get_neighbours(tm)) - assessed
            if neighbour_set - bg_set:
                return random.choice(neighbour_set)

            # otherwise, the assessed locations and all of the neighbours are black
            # The assessed should be updated to include all neighbours
            # and a random next_market chosen from any of the neighbour set
            else:
                assessed.add(tm)
                assessed = assessed.union(neighbour_set)
                next_market = random.choice(neighbour_set)
                return first_white(next_market, map_obj, bg_set, assessed)

        t1_target = first_white(t1_target, self.map, set(bm + gm))
        return Command.MOVE_TO, self.get_next_step(t1_target)

    def collect_rumours(self, market_prices, info):
        """Collect intel from other players at the same location, then store it in self.market_prices.
        Args:
            market prices : {market:{product:[amount, price]}}
                    dictionary of market and products and price they sell.
            info : { market : {product:price} }
                    dictionary of information from other players
        Output: None
        """
        pass

    def save_market_prices(self, market_prices, prices):
        """Save current market prices information into self.market_prices.
        Args:
            market prices : {market:{product:(amount, price)}}
                    dictionary of market and products and price they sell.
            prices : {product : price}
                    items and prices sold in current market.
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

    def get_next_step(self, target_location):
        """Finds the fastest path by employing a breadth-first search algorithm.
        Since all edges are currently unweighted, only a simplified breadth-first
        while storing each previous node is required
        """
        # TODO: need to update location before calling function
        # TODO: This is not the best path, this is the path that takes the fewest turns.
        # TODO: Update this with a check if the intermediary nodes are black or grey markets

        # Set the starting location as the player's current location
        start = self.loc

        # Collect all the nodes in the given map
        nodes = self.map.get_node_names()
        assert(target_location in nodes, "Target node not found in map")

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
        # Identify the currently assessed node by popping the right of the queue
        while queue:
            current = queue.pop()

            # If the current node is the target node, we are done we need to backtrack to the start to create the path
            # to avoid re-sorting a list, we need a structure that would show the path from start to end, left -> right.
            # We want to return the path and the steps taken to reach the target node.
            if current == target_location:
                path = deque()
                while current:
                    path.appendleft(current)
                    current = previous[current]

                # Path provides the nodes to traverse in order, so the next node is the best next step
                # If the path is of length 1, the player is starting at the target node, so the function
                # Returns None as the next step. Use an exception here instead of if statement
                # for lower comparison overhead
                try:
                    adjacent_market = path[1]
                except IndexError:
                    adjacent_market = None
                return adjacent_market, path

            # Collect the neighbours of this market and iterate over them.
            # If the neighbours have not been visited, add them to the queue
            # Set the current node as the previous node for all neighbours.
            neighbours = self.map.get_neighbours(current)
            for n in neighbours:
                if not visited[n]:
                    queue.appendleft(n)
                    visited[n] = True
                    previous[n] = current

    def central_market(self):
        """Function to determine which market is at the centre of the map
        Player is meant to move to the central market toward the end of the game
        """
        # Obtain the Euclidean distance between two points by the formula
        # sqrt( (x2 - x1)^2 + (y2 - y1)^2 )
        def central_dist(x, y):
            # TODO: Ensure that the circle closes at midpoint
            # TODO: Probably let Andrew know that the circle needs to surround
            #       the geometric centre

            # If the map corner is (0, 0), the map central is always as below
            cx, cy = self.map.map_width / 2, self.map.map_height / 2
            return math.sqrt((x - cx) ** 2 + (y - cy) ** 2)

        # To iterate only once over each node, the minimum distance is first
        # initialised as a maximum possible distance, i.e. the corner of the
        # map. The shape of the circle is also a rectangle, equivalent to the
        # map dimensions. Therefore, the true safest market must satisfy the
        # map ratios as well.
        # If the current minimum distance is greater than the distance of
        # the current node to the map center, reassign. This must be done
        # while keeping the angle of incident to the map center in mind
        node_coords = self.map.map_data["node_positions"]
        map_ratio = self.map.map_width / self.map.map_height
        min_dist = central_dist(self.map.map_width, self.map.map_height)
        distance_dict = dict()
        for node, coord in node_coords.items():
            current_dist = central_dist(coord[0], coord[1])
            current_ratio = coord[0] / coord[1]
            distance_dict[node] = current_dist

            # If more than 1 node is equidistant from the centre
            # The player does not care which one he goes to
            if min_dist >= current_dist and current_ratio <= map_ratio:
                min_dist = current_dist
                min_node = node

        return min_node, distance_dict

    # __________________________________________________________________________
    #                              END TODO
    # __________________________________________________________________________

    def __repr__(self):
        """Define the representation of the Player as the state of
        current attributes.
        """
        s = str(self.__dict__)
        return s


# ========================= TESTS ===================================
# TODO: Ensure Map & Game are imported for testing
# TODO: Test cases need to be more organised with themes around test cases

import unittest
import string
from Map import Map


# Define the test suite for all test cases.
def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(MapTestCase('test_central'))
    test_suite.addTest(MovementTestCase('test_move'))
    test_suite.addTest(MovementTestCase('test_stay'))
    return test_suite


# Creates a test case class specifically for map identification.
class MapTestCase(unittest.TestCase):
    # Tests if the output of a central market is correct.
    # In this test case, there is exactly one central market.
    def test_central(self):
        p1 = Player()
        p1.map = test_map()
        self.assertEqual(p1.central_market(), "V")


# Creates a test case class specifically for basic player movement.
class MovementTestCase(unittest.TestCase):
    # Tests if the next step is definitely within the neighbouring nodes.
    # Tests if the path length is correct.
    def test_move(self):
        p1 = Player()
        p1.map = test_map()
        p1.loc = "A"
        next_step, path = p1.get_next_step("V")
        self.assertTrue(next_step in p1.map.get_neighbours("A"))
        self.assertEqual(len(path), 4)

    # Tests if the next step is to stay put if the player arrives.
    # Tests if the number of turns required is to stay still is 0.
    def test_stay(self):
        p1 = Player()
        p1.map = test_map()
        p1.loc = "A"
        next_step, path = p1.get_next_step("A")
        self.assertIsNone(next_step)
        self.assertEqual(len(path), 1)


# This function helps output the map for testing.
# Allows the size and seed to be mutable.
def test_map(size=26, seed=23624):
    assert(type(size) == int)
    assert(1 <= size <= 26)
    map_width = 200  # Dimensions of map
    map_height = 100
    res_x = 2  # Resolution to render the map at
    res_y = 3
    node_list = list(string.ascii_uppercase)[:26]
    return Map(node_list, map_width, map_height, res_x, res_y, seed=seed)


if __name__ == "__main__":
    # Print visual diagnostics
    p1 = Player()
    p1.map = test_map()
    p1.loc = "A"
    target = "V"
    next_step, path = p1.get_next_step(target)
    central_market = p1.central_market()
    p1.map.pretty_print_map()
    print(f"Starting at {p1.loc}, the next step toward {target} is {next_step}.")
    print(f"The optimal path is {list(path)}. This takes {len(path)} turns.")
    print(f"The central market is {central_market}")

    # Run tests.
    runner = unittest.TextTestRunner()
    runner.run(suite())

