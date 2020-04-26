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
        self.turn = 0                               # how many turns taken in game:     0,1,..*
        self.researched = set()                     # researched markets:               set({market1, market2..})
        self.market_prices = {}                     # market prices from self/players:  {market:{product:[price, amount]}}
        self.inventory = defaultdict(lambda: (0, 0))# record items in inventory:        {product:[amount, asset_cost]}
        self.gold = 0                               # gold:                             0,1,..*
        self.score = 0                              # score from inventory and gold:    0,1,..*
        self.goal_achieved = False                  # indicates whether goal achieved:  True/False
        self.visited_node = defaultdict(int)        # location visit counts:            {location: times_visited}
        self.loc = ''                               # player's current location:        str(market location)
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
        self.save_market_prices(prices)

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
        self.ctr, distances = self.central_market()

        # Determine the furthest node from the central market
        t1_target = max(distances, key=distances.get)

        # If we are already at the maximum node, research the node
        if self.loc == t1_target:
            return Command.RESEARCH, None

        # Find the first, random white market closest to the target market
        # This is done recursively until a white market is found
        # On turn 1, white markets are expected
        def nearest_white(tm, map_obj, bg_set, assessed=set()):
            # return the target market if it is a white market
            if tm not in bg_set:
                return tm

            # get the neighbours of the target market that have not been assessed
            # if this set less the black/grey market set is not empty,
            # return a random target white market
            neighbour_set = map_obj.get_neighbours(tm) - assessed
            white_set = neighbour_set - bg_set
            if white_set:
                return random.choice(list(white_set))

            # otherwise, the assessed locations and all of the neighbours are black
            # The assessed should be updated to include all neighbours
            # and a random next_market chosen from any of the neighbour set
            else:
                assessed.add(tm)
                assessed = assessed.union(neighbour_set)
                next_market = random.choice(list(neighbour_set))
                return nearest_white(next_market, map_obj, bg_set, assessed)

        self.target_loc = nearest_white(t1_target, self.map, set(bm + gm))
        return Command.MOVE_TO, self.get_next_step(self.target_loc)[0]

    def collect_rumours(self, info):
        """Collect intel from other players at the same location, then store it in self.market_prices.
        Args:
            market prices : {market:{product:[price, amount]}}
                    dictionary of market and products and price they sell.
            info : { market : {product:price} }
                    dictionary of information from other players
        Output: None
        """
        if info:
            for market, information in info.items():
                if not self.market_prices.get(market):
                    self.market_prices[market] = {k: (v, None) for k, v in information.items()}

    def save_market_prices(self, market, prices):
        """Save current market prices information into self.market_prices.
        Args:
            market (str): market location
            prices (dict): {product: (price, amount)}
                    items and prices sold in current market.
        Output: None
        """
        if prices:
            self.market_prices[market] = prices

    def check_goal(self):
        """Check if goal is acheived by comparing inventory and goal.
           Switch self.acheived_goal = True if acheived goal.
        Args:
            inventory : {product:[amount, asset_cost]}
                    dictionary of products in inventory.
            goal : dictionary {product:amount needed}
                    dictionary of products required to acheive goal.
        Output: None
        """
        for prod, amount in self.goal.items():
            if self.inventory[prod][1] < amount:
                return None
        self.goal_achieved = True
        return None

    def search_market(self, bm, gm):
        """Given current location, inventory, gold, and goal, what is the best market to buy from.
           What market to choose if doesn't have any researched/rumoured information?
           Feel free to improvise and document the details here.
        Args:
            bm (list): list of current black markets
            gm (list): list of current grey markets
        Output:
            target_market (str): returns the target market from search. If all information on markets
                                 are black, returns None
        """
        # distance=len(get_next_step(self, target)[1])
        # self.market_prices   # market prices from self/players:  {market:{product:[price, amount]}}
        # self.inventory record items in inventory:        {product:[amount, asset_cost]}
        # get the product name which has not reached the goal
        possible_targets = {product: [None, math.inf]
                            for product, amount in self.goal.items()
                            if self.inventory[product][0] < amount}
        if possible_targets:
            for market, info in self.market_prices.items():
                # check if markets are white
                if market not in bm + gm:
                    for product in info.keys():
                        market_price = info[product][0]
                        min_price = possible_targets[product][1]
                        if (product in self.goal.keys()) and (market_price < min_price):
                            possible_targets[product] = [market, market_price]
        else:
            return None
        # calculate the distances to these markets
        dist_to_target = {market: len(self.get_next_step(market)[1])
                          for market, price in possible_targets.values()}
        # find the closest white market to achieve the goal
        # TODO: if returns none, logic is required to find more markets and research
        if dist_to_target:
            target_market = min(dist_to_target, key=dist_to_target.get)
        else:
            target_market = None

        return target_market

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
        # TODO: Update this with a check if the intermediary nodes are black or grey markets

        # Set the starting location as the player's current location
        start = self.loc

        # Collect all the nodes in the given map
        nodes = self.map.get_node_names()

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

    def dist_to(self, from_loc, to_loc):
        """Function to calculate the distance between two points
        Args:
            from_loc (tup): (x1, y1) starting coordinates
            to_loc (tup): (x2, y2) ending coordinates
        Output:
            dist (float): distance between the coordinates as a result of
                          sqrt((x2 - x1)^2 + (y2 - y1)^2)
            """
        x1, y1 = from_loc
        x2, y2 = to_loc
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def central_market(self):
        """Function to determine which market is at the centre of the map
        Player is meant to move to the central market toward the end of the game
        """
        # To iterate only once over each node, the minimum distance is first
        # initialised as a maximum possible distance, i.e. the corner of the
        # map. The shape of the circle is also a rectangle, equivalent to the
        # map dimensions. Therefore, the true safest market must satisfy the
        # map ratios as well.
        # If the current minimum distance is greater than the distance of
        # the current node to the map center, reassign. This must be done
        # while keeping the angle of incident to the map center in mind
        map_center = self.map.map_width / 2, self.map.map_height / 2
        map_corner = self.map.map_width, self.map.map_height
        node_coords = self.map.map_data["node_positions"]
        map_ratio = self.map.map_width / self.map.map_height
        min_dist = self.dist_to(map_corner, map_center)
        distance_dict = dict()
        for node, coord in node_coords.items():
            coord = coord[:2]
            current_dist = self.dist_to(coord, map_center)
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
from itertools import cycle
from Map import Map


# Define the test suite for all test cases.
def suite():
    # Test suite instance
    test_suite = unittest.TestSuite()

    # Map testing
    test_suite.addTest(MapTestCase('test_central'))
    test_suite.addTest(MapTestCase('test_search_market'))

    # Movement testing
    test_suite.addTest(MovementTestCase('test_move'))
    test_suite.addTest(MovementTestCase('test_stay'))

    # Knowledge testing
    test_suite.addTest(KnowledgeTestCase('test_check_goal'))
    test_suite.addTest(KnowledgeTestCase('test_rumours'))
    test_suite.addTest(KnowledgeTestCase('test_prices'))

    # Strategy testing
    test_suite.addTest(StrategyTestCase('test_first_turn'))

    return test_suite


# Creates a test case class specifically for map identification.
class MapTestCase(unittest.TestCase):
    # Tests if the output of a central market is correct.
    # In this test case, there is exactly one central market.
    def test_central(self):
        p = Player()
        p.map = test_map()
        self.assertEqual(p.central_market()[0], "V")

    def test_search_market(self):
        p = Player()
        p.map = test_static_map()
        p.loc = "E"
        prod = ["Food", "Electronics", "Social", "Hardware"]
        goal = dict(zip(prod, [5]*len(prod)))
        p.set_goal(goal)
        nodes = p.map.get_node_names()
        temp = list(zip(cycle(prod), map(list, enumerate(range(len(prod) * len(nodes))))))
        temp2 = []
        for i in range(len(nodes)):
            temp2.append((nodes[i], dict(temp[(i*4):(4*(i+1))])))
        p.market_prices = dict(temp2)
        # p.market_prices should look like:
        # {'A': {'Food': [0, 0],
        #        'Electronics': [1, 1],
        #        'Social': [2, 2],
        #        'Hardware': [3, 3]},
        #  'B': {'Food': [4, 4],
        #        'Electronics': [5, 5],
        #        'Social': [6, 6],
        #        'Hardware': [7, 7]}}...
        # test when inventory be empty with no bm and gm
        target = p.search_market(bm=[], gm=[])
        self.assertEqual(target, "A")
        # test when black market is "A"
        target = p.search_market(bm=["A"], gm=[])
        self.assertEqual(target, 'B')
        # test when grey market is "A"
        target = p.search_market(bm=[], gm=["A"])
        self.assertEqual(target, "B")
        # test when goal is reached
        p.inventory = dict(zip(prod, map(list, [(5, 0)] * len(prod))))
        target = p.search_market(bm=[], gm=[])
        self.assertIsNone(target)


# Creates a test case class specifically for basic player movement.
class MovementTestCase(unittest.TestCase):
    # Tests if the next step is definitely within the neighbouring nodes.
    # Tests if the path length is correct.
    def test_move(self):
        p = Player()
        p.map = test_map()
        p.loc = "A"
        next_step, path = p.get_next_step("V")
        self.assertTrue(next_step in p.map.get_neighbours("A"))
        self.assertEqual(len(path), 4)

    # Tests if the next step is to stay put if the player arrives.
    # Tests if the number of turns required is to stay still is 0.
    def test_stay(self):
        p = Player()
        p.map = test_map()
        p.loc = "A"
        next_step, path = p.get_next_step("A")
        self.assertIsNone(next_step)
        self.assertEqual(len(path), 1)


# Creates test case class for player knowledge functions
class KnowledgeTestCase(unittest.TestCase):
    # Tests if the check_goal function works correctly
    def test_check_goal(self):
        p = Player()
        p.inventory['Food'] = [100, 10]
        p.set_goal({'Food': 10})
        p.check_goal()
        self.assertTrue(p.goal_achieved)

        p.set_goal({'Food': 20})
        self.assertFalse(p.check_goal())

    # Tests is if the collect rumours function works correctly
    def test_rumours(self):
        p = Player()
        info = {"A": {'Food': 90,
                      'Social': 60},
                "B": {'Food': 80,
                      'Social': 70}
                }
        p.collect_rumours(info)
        self.assertTrue(p.market_prices)
        self.assertIsNone(p.market_prices["A"]["Food"][1])
        self.assertEqual(p.market_prices["B"]["Social"][0], 70)
        p.market_prices["A"] = {'Food': [90, 100],
                                'Social': [60, 50]}
        p.collect_rumours(info)
        self.assertIsNotNone(p.market_prices["A"]["Food"][1])
        self.assertEqual(p.market_prices["A"]["Social"][1], 50)

    # Tests if the save_market_prices function works correctly
    def test_prices(self):
        p = Player()
        market = "A"
        prices = {'Food': [90, 100],
                  'Social': [60, 50]}
        p.save_market_prices(market, prices)
        self.assertTrue(p.market_prices)
        self.assertEqual(p.market_prices["A"]["Food"], [90, 100])


# Create a class for testing strategy.
class StrategyTestCase(unittest.TestCase):
    # Testing first turn strategy
    def test_first_turn(self):
        p = Player()
        p.map = test_map()
        p.loc = "V"

        # move to the furthest node, U
        cmd, _ = p.first_turn(bm=[], gm=[])
        self.assertEqual(cmd, Command.MOVE_TO)
        self.assertEqual(p.target_loc, "U")

        # move to the furthest node from V that is not U
        cmd, _ = p.first_turn(bm=["U"], gm=[])
        self.assertEqual(cmd, Command.MOVE_TO)
        self.assertNotEqual(p.target_loc, "U")
        self.assertNotEqual(p.target_loc, "V")

        # move to the furthest node from V that is not U or its neighbours
        cmd, _ = p.first_turn(bm=["U"], gm=list(p.map.get_neighbours("U")))
        self.assertEqual(cmd, Command.MOVE_TO)
        self.assertNotEqual(p.target_loc, "U")
        self.assertNotEqual(p.target_loc, "V")

        # stay at the node and research
        p.loc = "U"
        cmd, next_step = p.first_turn([], [])
        self.assertEqual(cmd, Command.RESEARCH)
        self.assertIsNone(next_step)


# This function helps output the map for testing.
# Allows the size and seed to be mutable.
def test_map(size=26, seed=23624):
    assert(type(size) == int)
    assert(1 <= size <= 26)
    map_width = 200  # Dimensions of map
    map_height = 100
    res_x = 2  # Resolution to render the map at
    res_y = 3
    node_list = list(string.ascii_uppercase)[:size]
    return Map(node_list, map_width, map_height, res_x, res_y, seed=seed)


# This function helps output a static map for testing.
def test_static_map():
    class StaticMap(Map):
        def __init__(self, node_positions, node_graph, map_width, map_height, resolution_x, resolution_y):
            self.map_data = {}
            self.map_width = map_width
            self.map_height = map_height
            self.resolution_x = resolution_x
            self.resolution_y = resolution_y

            self.map_data["node_positions"] = node_positions
            self.map_data["node_graph"] = node_graph

            self.init_circle()

            self.render_map()

    node_pos = {"A": (100, 50, 0),
                "B": (10, 50, 0),
                "C": (100, 90, 0),
                "D": (190, 50, 0),
                "E": (100, 10, 0)}
    node_graph = {'A': {'B', 'C', 'D', 'E'},
                  'B': {'A', 'C', 'E'},
                  'C': {'A', 'B', 'D'},
                  'D': {'A', 'C', 'E'},
                  'E': {'A', 'B', 'D'}}
    return StaticMap(node_pos, node_graph, 200, 100, 2, 3)


if __name__ == "__main__":
    # Print visual diagnostics
    player = Player()
    player.map = test_map()
    player.loc = "A"
    central_market = player.central_market()[0]
    next_step, path = player.get_next_step(central_market)
    player.map.pretty_print_map()
    print(f"From {player.loc}, the next step to {central_market} is {next_step}.")
    print(f"The quickest path is {list(path)}. This takes {len(path)} turns.")
    print(f"The central market is {central_market}")

    runner = unittest.TextTestRunner()
    runner.run(suite())

