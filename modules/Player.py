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
import copy
import numpy as np


class Player(BasePlayer):
    def __init__(self):
        # Initialise the class without arguments
        # Inherit the parent init properties
        super().__init__()

        # Set additional properties
        self.turn = 0                              # how many turns taken in game:     0,1,..*
        self.researched = set()                    # researched markets:               [market1, market2..]
        self.market_prices = {}                    # market prices from self/players:  {market:{product:[amount, price]}}
        self.inventory = defaultdict(lambda:(0,0)) # record items in inventory:        {product:(amount, asset_cost)}
        self.gold = 0                              # gold:                             0,1,..*
        self.score = 0                             # score from inventory and gold:    0,1,..*
        self.goal_achieved = False                 # indicates whether goal achieved:  True/False
        self.visited_node = defaultdict(int)       # location visit counts:            {location: times_visited}
        self.loc = ''                              # player's current location
        self.bonus = 10000                         # bonus points upon reaching goal
        self.ctr = ''                              # the central market, currently unknown
        self.target_loc = ''                       # target location after searching and pathing
        self.black_penalty = 100                   # penalty for being in a black market
        self.interest = 1.1                        # interest rate for overdrawn gold

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

        print("PRINT SOMETHING!")

        # Determine current strategy
        cmd = self.get_strategy(prices, bm, gm)

        return cmd

    # TODO ______________________________________________________________________________________
    # Complete the functions below. Please add/remove additional arguments as you need.
    # Think of possible test cases for each of them too.
    # __________________________________________________________________________________________

    def get_strategy(self, prices, bm, gm):
        """Returns a function that dictates the player's current strategy
        Args:
            prices (dict): Prices of market in current location
            bm (list): List of black markets passed from take_turn
            gm (list): List of grey markets passed from take_turn
        Output:
            cmd (tup): A tuple of Command.CMD, data, output by children functions
        """
        # get the set of black and grey markets
        bg_set = set(bm + gm)
        bm = set(bm)

        # check if goal achieved
        self.check_goal()

        if self.turn == 1:
            return self.first_turn(bg_set)

        # The highest priority is if the player is in a black/grey market
        # Player moves to the closest nearest white market
        if self.loc in bg_set:
            if self.loc in bm:
                self.gold -= self.black_penalty
            self.target_loc = self.nearest_white(self.loc, bg_set)
            return Command.MOVE_TO, self.get_next_step(self.target_loc)

        # If the gold is negative, the player cut losses by dumping inventory
        # At the current market
        if self.gold < 0:
            self.gold = self.interest * self.gold
            if prices:
                return Command.SELL, self.cut_losses(prices)
            else:
                return Command.RESEARCH, None

        # While we don't have information on a third of the markets in the game
        # Move
        if len(self.market_prices.keys()) < len(self.map.get_node_names()) // 2:
            return self.wander(prices, bg_set)

        # Once we have enough information, try to achieve the goal
        if not self.goal_achieved:
            buying_market = self.search_market(bg_set)
            if buying_market:
                self.target_loc = buying_market
                return self.move_to_buy(prices)
            else:
                return self.wander(prices, bg_set)
        else:
            return self.move_to_ctr()

    def move_to_ctr(self):
        self.target_loc = self.ctr
        next_step = self.get_next_step(self.target_loc)
        if next_step:
            return Command.MOVE_TO, next_step
        else:
            return Command.PASS, None

    def cut_losses(self, prices):
        # prices = {product: (prices, amounts)}
        # inventory = {product: (amount, cost)}
        final_assets = -math.inf
        to_sell = None
        sell_num = 0
        for product, info in self.inventory.items():
            tmp_num = -int(self.gold // prices[product][0])
            if info[0] >= tmp_num:
                tmp_inv = copy.deepcopy(self.inventory)
                tmp_indcst = tmp_inv[product][1] / tmp_inv[product][0]
                tmp_newnum = tmp_inv[product][0] - tmp_num
                tmp_newcst = tmp_newnum * tmp_indcst
                tmp_inv[product] = (tmp_newnum, tmp_newcst)
                tmp_assets = sum([cost for amt, cost in tmp_inv.values()])
                if tmp_assets >= final_assets:
                    final_assets = tmp_assets
                    to_sell = product
                    sell_num = tmp_num
        if to_sell:
            inv_num = self.inventory[to_sell][0]
            inv_indcst = self.inventory[to_sell][1] / inv_num
            inv_newnum = inv_num - sell_num
            inv_newcst = inv_newnum * inv_indcst
            self.inventory[to_sell] = (inv_newnum, inv_newcst)
            return to_sell, sell_num
        else:
            to_sell = max(self.inventory, key=lambda x: self.inventory[x][1])
            sell_num = self.inventory[to_sell][0]
            self.inventory[to_sell] = (0, 0)

        self.gold += sell_num * prices[to_sell][0]
        return to_sell, sell_num

    def wander(self, prices, bg_set):
        if self.loc != self.target_loc:
            if self.loc not in self.researched.union(bg_set):
                self.researched.add(self.loc)
                return Command.RESEARCH, None
            else:
                return Command.MOVE_TO, self.get_next_step(self.target_loc)
        else:
            if self.loc in self.researched.union(bg_set):
                next_market = self.choose(bg_set, {self.loc})
                if next_market:
                    self.target_loc = next_market
                    return self.wander(prices, bg_set)
                else:
                    return self.move_to_buy(prices)
            else:
                self.researched.add(self.loc)
                return Command.RESEARCH, None

    def choose(self, bg_set, ignore_set):
        markets = set(self.map.get_node_names())
        researched = self.researched
        avail = list(markets - researched - bg_set - ignore_set)
        if avail:
            return random.choice(avail)
        else:
            return None

    def move_to_buy(self, prices):
        """Function to continue along the path to the target"""
        if self.loc != self.target_loc:
            return Command.MOVE_TO, self.get_next_step(self.target_loc)
        elif self.loc == self.target_loc:
            if prices:
                purchase_item = self.purchase(prices)
                if purchase_item:
                    return Command.BUY, purchase_item
                else:
                    return self.move_to_ctr()
            return Command.RESEARCH, None

    def first_turn(self, bg_set):
        """The set of instructions on the first turn of the player.
        The player must get a sense of the map by following these steps.
        1. Store the central market on the map.
        2. Set the furthest node from the central market as target node.
        3. Find the fastest path to the target.
        4. Set the next node as the next step.
        5. If the current location is a terminal node, switch to research strat.
        Args:
            bg_set (set): Set of black and grey markets
            bm (list): Current list of black markets
            gm (list): Current list of grey markets
        Output:
            cmd (tup): A tuple of (Command.CMD, data)
        """
        # Set the central market
        self.ctr, distances = self.central_market()

        # Set the score to be equal to the amount of gold
        self.score = self.gold

        # Determine the furthest node from the central market
        t1_target = max(distances, key=distances.get)

        # If we are already at the maximum node, research the node
        if self.loc == t1_target:
            self.researched.add(self.loc)
            self.target_loc = self.choose(bg_set, {self.loc})
            return Command.RESEARCH, None

        # Find the first, random white market closest to the target market
        # This is done recursively until a white market is found
        # On turn 1, white markets are expected
        self.target_loc = self.nearest_white(t1_target, bg_set)
        return Command.MOVE_TO, self.get_next_step(self.target_loc)

    def nearest_white(self, target_market, bg_set, assessed=set()):
        """Returns the market location closest to the target market that is white
        If the target market is white, returns the target"""
        # return the target market if it is a white market
        if target_market not in bg_set:
            return target_market

        # get the neighbours of the target market that have not been assessed
        # if this set less the black/grey market set is not empty,
        # return a random target white market
        neighbours = self.map.get_neighbours(target_market)
        neighbour_set = neighbours - assessed
        white_set = neighbour_set - bg_set
        if white_set:
            return random.choice(list(white_set))

        # otherwise, the assessed locations and all of the neighbours are black
        # The assessed should be updated to include all neighbours
        # and a random next_market chosen from any of the neighbour set
        else:
            assessed.add(target_market)
            assessed = assessed.union(neighbour_set)
            next_market = random.choice(list(neighbours))
            return self.nearest_white(next_market, bg_set, assessed)

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

    def save_market_prices(self, prices):
        """Save current market prices information into self.market_prices.
        Args:
            market (str): market location
            prices (dict): {product: (price, amount)}
                    items and prices sold in current market.
        Output: None
        """
        if prices:
            self.market_prices[self.loc] = prices

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

    def search_market(self, bg_set):
        """Given current location, inventory, gold, and goal, what is the best market to buy from.
           What market to choose if doesn't have any researched/rumoured information?
           Feel free to improvise and document the details here.
        Args:
            bg_set (set): Set of black and grey markets
        Output:
            target_market (str): returns the target market from search. If all information on markets
                                 are black, returns None
        """
        # self.market_prices   # market prices from self/players:  {market:{product:[price, amount]}}
        # self.inventory record items in inventory:        {product:[amount, asset_cost]}
        # get the product name which has not reached the goal
        possible_targets = {product: [None, math.inf]
                            for product, amount in self.goal.items()
                            if self.inventory[product][0] < amount}
        if possible_targets:
            for market, info in self.market_prices.items():
                # check if markets are white
                if market not in bg_set:
                    for product in possible_targets.keys():
                        market_price = info[product][0]
                        min_price = possible_targets[product][1]
                        if all([market_price < min_price]):
                            possible_targets[product] = (market, market_price)
        else:
            # Return None if all inventory items have been reached.
            return None
        # calculate the distances to these markets
        dist_to_target = {market: len(self.get_path_to(market))
                          for market, prices in possible_targets.values()
                          if market}
        # find the closest white market to achieve the goal
        # TODO: if returns none, logic is required to find more markets and research
        if dist_to_target:
            target_market = min(dist_to_target, key=dist_to_target.get)
        else:
            target_market = None

        return target_market

    def buy_sell(self, prices):
        """ The purpose of selling is to maximise profit(buy low sell high to take arbitrage)
        Selling is only executed in the later periods when we have sufficient amount of info AND goal 
        is completed. To check if a product worth trading, compute the variances for the product prices across
        all the markets. If the variance is small, it implies the price for the product is stable, so no much
        space for arbitrage and we don't have to bother with this product.
        
        Step 1:  compute the variances of the product price list (order by their variance in the descending order)
        Step 2:  make a target list consisting of eg. the first 5 products as the products we aim to sell
        Step 3:  Check if the market sells the target list products 
                 if yes, go to step 4
        Step 4:  Check if we are suppose to sell the products in this market, ie. is it the right place to sell?
                 Decision making:
                    If the price at this market is above eg. the 75th percentile of the all the prices for this product,
                    it suggests it is the right place to sell
                    --- Implication: if it's below 25th percentile, possibly a right place to buy
                 If yes, go to step 5
        Step 5:  Check if our inventory contains the target products which the market has
                 If yes, go to step 6
        Step 6: Sell the target products
    
        """
        # step 1
        product_price = defaultdict(list)
        for market, market_items in self.market_prices.items():
            for product in market_items.keys():
                if product in product_price.keys():
                    product_price[product].append(self.market_prices[market][product][0])

        # Store the statistical information of the products
        # price stats are: {product: (price variance, 75th percentile, 25th percentile)
        price_stats = {product: (np.var(product_price[product]),
                                 np.percentile(product_price[product], 75),
                                 np.percentile(product_price[product], 25))
                       for product in product_price.keys()}

        # Step 2: compute the target list for selling: eg. the first 5 items with the largest variances
        target_list = sorted(price_stats.items(), key=lambda x: -x[1][0])[:5]
        target_name = {product[0] for product in target_list}

        # Step 3: Check if the market sells the target list products
        to_trade = {target for target in target_name if prices.get(target)}

        # if the market doesn't sell the target products, function ends
        if not to_trade:
            return False

        # step 4: check if it's the right market to sell/buy
        sell_now = {product for product in to_trade
                    if prices[product][0] >= price_stats[product][1]}
        buy_set = {product for product in to_trade
                   if prices[product][0] <= price_stats[product][2]}

        # step 5: Check if our inventory contains the target products which the market has
        # Also check if the we have some items to sell in inventory
        sell_set = sell_now.intersection({product for product in self.inventory.keys()
                                          if self.inventory[product][0] > 0})
        return sell_set, buy_set

    def purchase(self, this_market_info):
        """Return the item and amount to buy when player is at a destination market.
            Update self inventory and gold too before returning.

                1. Find required item to buy (item in goal and under target amount)
                2. Calculate amount to buy
                3. If there are multiple items to required select base on highest score 
                   after purchase         
                4. update self inventory, gold, and return output.
                
            **Note This function is guaranteed to purchase a type of product even
            when the market couldnt meet our demand to reduce complexity as the
            score will be same/reduced when this happens. This is achieved by
            setting initial max_score=0.    
                
        Args:
            1. goal: {prod1:amt1, prod2:amt2}
                a dictionary of products required to achieve goal.
            2. inventory: {prod1:[amt1, asset_cost1], prod2:[amt2, asset_cost2]}
                a dictionary of products, amount of products, cost spent buying the items in inventory.            
            3. gold : gold_amt            
            4. this_market_info: {prod1:(p1, amt1), prod2:(p2, amt2), prod3:(p3, amt3), prod4:(p4, amt4)}
                a dictionary of prices of item in the current market.
        Output: (product, amount)
        """
        # TODO: the score needs to be calculated according to the current score, which is the current gold
        #       and any other goal scores.
        #       Perhaps include a score calculation and score attribute for the player to self track
        max_score = -math.inf
        buy_amt = 0
        to_buy = None

        # find the best item to buy
        for product in this_market_info.keys():

            # initialize dummy variables used to record after purchase inventory and gold to compute score         
            tmp_inventory = copy.deepcopy(self.inventory)
            tmp_gold = self.gold
            
            # if product is what we need
            if product in self.goal.keys() and self.inventory[product][0] < self.goal[product]:
                # tmp_amt = MIN(market available, affordable amount, required amount)                                                                
                tmp_amt = min(int(this_market_info[product][1]),
                              int(self.gold // this_market_info[product][0]),
                              int(self.goal[product] - self.inventory[product][0]))

                # update dummy variables to reflect after purchase inventory and gold level
                tmp_inventory[product] = (tmp_inventory[product][0] + tmp_amt,
                                          tmp_amt * tmp_inventory[product][1] + this_market_info[product][0])
                tmp_gold -= tmp_amt * this_market_info[product][0]

                # compute score and update best item to buy
                tmp_score = self.compute_score(tmp_inventory, tmp_gold, self.goal)
                if tmp_score >= max_score:
                    to_buy = product
                    buy_amt = int(tmp_amt)
                    max_score = tmp_score
        if to_buy:
            # update self inventory/gold then return purchased item
            cost = buy_amt * this_market_info[to_buy][0]
            self.gold = self.gold - cost
            self.inventory[to_buy] = (self.inventory[to_buy][0] + buy_amt, self.inventory[to_buy][1] + cost)
            return to_buy, int(buy_amt)
        else:
            return None

    def compute_score(self, inventory, gold, goal):
        """Compute and return score.
        Args:
            inventory: {prod1:[amt1, asset_cost1], prod2:[amt2, asset_cost2]}
                a dictionary of products, amount of products, cost spent buying the items in inventory.   
            goal : {product : price}
                    dictionary of products required to acheive goal.
            gold : int
                    How many gold the player has currently.
        Output: score (int)
        """
        score = 0
        # score for hitting target
        for item in inventory.keys():
            if inventory[item][0] >= goal[item]:
                score += self.bonus

        # include remaining gold
        score += gold

        return score

    def get_next_step(self, target_location):
        """Returns the next step on the path required.
        """
        shortest_path = self.get_path_to(target_location)

        # Shortest path provides the nodes to traverse in order, so the next node is the best next step
        # If the path is of length 1, the player is starting at the target node, so the function
        # Returns None as the next step. Use an exception here instead of if statement
        # for lower comparison overhead
        try:
            adjacent_market = shortest_path[1]
        except (IndexError, TypeError):
            adjacent_market = None
        return adjacent_market

    def get_path_to(self, target_location):
        """Finds the fastest path by employing a breadth-first search algorithm.
        Since all edges are currently unweighted, only a simplified breadth-first
        while storing each previous node is required
        """
        # TODO: add some sort of priority queue with weights according to the market color
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
                return path

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
    test_suite.addTest(StrategyTestCase('test_purchase'))

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
        target = p.search_market(set())
        self.assertEqual(target, "A")
        # test when black market is "A"
        target = p.search_market(set("A"))
        self.assertEqual(target, 'B')
        # test when goal is reached
        p.inventory = dict(zip(prod, map(list, [(5, 0)] * len(prod))))
        target = p.search_market(set())
        self.assertIsNone(target)


# Creates a test case class specifically for basic player movement.
class MovementTestCase(unittest.TestCase):
    # Tests if the next step is definitely within the neighbouring nodes.
    # Tests if the path length is correct.
    def test_move(self):
        p = Player()
        p.map = test_map()
        p.loc = "A"
        target = "V"
        next_step = p.get_next_step(target)
        next_path = p.get_path_to(target)
        self.assertTrue(next_step in p.map.get_neighbours("A"))
        self.assertEqual(len(next_path), 4)

    # Tests if the next step is to stay put if the player arrives.
    # Tests if the number of turns required is to stay still is 0.
    def test_stay(self):
        p = Player()
        p.map = test_map()
        p.loc = "A"
        target = "A"
        next_step = p.get_next_step(target)
        next_path = p.get_path_to(target)
        self.assertIsNone(next_step)
        self.assertEqual(len(next_path), 1)


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
                      'Social': 70}}
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
        p.loc = "A"
        prices = {'Food': [90, 100],
                  'Social': [60, 50]}
        p.save_market_prices(prices)
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
        cmd, _ = p.first_turn(set())
        self.assertEqual(cmd, Command.MOVE_TO)
        self.assertEqual(p.target_loc, "U")

        # move to the furthest node from V that is not U
        cmd, _ = p.first_turn(set(["U"]))
        self.assertEqual(cmd, Command.MOVE_TO)
        self.assertNotEqual(p.target_loc, "U")
        self.assertNotEqual(p.target_loc, "V")

        # move to the furthest node from V that is not U or its neighbours
        bm = ["U"]
        gm = list(p.map.get_neighbours("U"))
        cmd, _ = p.first_turn(set(bm + gm))
        self.assertEqual(cmd, Command.MOVE_TO)
        self.assertNotEqual(p.target_loc, "U")
        self.assertNotEqual(p.target_loc, "V")

        # stay at the node and research
        p.loc = "U"
        cmd, next_step = p.first_turn(set())
        self.assertEqual(cmd, Command.RESEARCH)
        self.assertIsNone(next_step)

    # Test the purchase function
    def test_purchase(self):
        p = Player()
        goal = {'Food': 10, 'Social': 15}
        p.set_goal(goal)
        p.inventory['Food'] = (5, 0)
        p.set_gold(500.0)
        prices = {'Food': (100, 3),
                  'Electronics': (300, 10),
                  'Social': (150, 5),
                  'Hardware': (350, 5)}
        prod, amt = p.purchase(prices)
        self.assertEqual(prod, 'Food')
        self.assertEqual(amt, 3)


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
    next_step = player.get_next_step(central_market)
    next_path = player.get_path_to(central_market)
    player.map.pretty_print_map()
    print(f"From {player.loc}, the next step to {central_market} is {next_step}.")
    print(f"The quickest path is {list(next_path)}. This takes {len(next_path)} turns.")
    print(f"The central market is {central_market}")

    runner = unittest.TextTestRunner()
    runner.run(suite())

