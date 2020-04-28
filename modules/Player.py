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
             Renee He            (h.he13@student.unimelb.edu.au)
             Joshua Xujuang Lin  (xujiang.lin@student.unimelb.edu.au)
             Ellie Meng          (h.meng2@student.unimelb.edu.au)
             Isaac Pang          (i.pang2@student.unimelb.edu.au)
             Tann Tan            (h.tan49@student.unimelb.edu.au)
             Grace Zhu           (grace.zhu@student.unimelb.edu.au)
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
        self.turn = 0                                 # how many turns taken in game: 0,1,..*
        self.max_turn = 300                           # maximum turns in a game
        self.researched = set()                       # researched markets:           [market1, market2..]
        self.market_prices = {}                       # prices from self/players:     {market:{product:[price, amount]}}
        self.inventory = defaultdict(lambda: (0, 0))  # record items in inventory:    {product:(amount, asset_cost)}
        self.gold = 0                                 # gold:                            0,1,..*
        self.goal_achieved = False                    # indicates whether goal achieved: True/False
        self.visited_node = defaultdict(int)          # location visit counts:           {location: times_visited}
        self.loc = ''                                 # player's current location
        self.bonus = 10000                            # bonus points upon reaching goal
        self.ctr = ''                                 # the central market, currently unknown
        self.target_loc = ''                          # target location after searching and pathing
        self.black_penalty = 100                      # penalty for being in a black market
        self.interest = 1.1                           # interest rate for overdrawn gold
        self.blacklist = defaultdict(set)             # set of markets with no amount for each product
        self.price_stats = {}                         # stats of market prices        {product: (price var, 75th, 25th)}
        self.profit_order = []                        # A list of products in order to sell
        self.final_turns = 0                          # The count of turns used at the end of the game

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

        # Define the player location
        self.loc = location

        # Update gold
        if self.gold < 0:
            self.gold = self.interest * self.gold

        # Blacklist the product in this market if there is nothing here
        if prices:
            for product in prices.keys():
                if prices[product][1] == 0:
                    self.blacklist[product].add(self.loc)

        # Add information from current market
        self.save_market_prices(prices)

        # Collect information from other player
        self.collect_rumours(info)

        # Determine current strategy
        cmd, data = self.get_strategy(prices, bm, gm)

        # If the command is to buy, update the inventory and gold accordingly
        if cmd == Command.BUY:
            self.inventory, self.gold = self.update_inv_gold(prices, self.inventory, data[0], data[1], self.gold,
                                                             action=0)
        # If the command is to sell, update the inventory and gold accordingly
        elif cmd == Command.SELL:
            self.inventory, self.gold = self.update_inv_gold(prices, self.inventory, data[0], data[1], self.gold,
                                                             action=1)

        return cmd, data

    def save_market_prices(self, prices):
        """Save current market prices information into self.market_prices.
        Args:
            prices (dict): {product: (price, amount)}
                    items and prices sold in current market.
        Output: None
        """
        if prices:
            self.market_prices[self.loc] = prices

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

    def get_strategy(self, prices, bm, gm):
        """Returns a tuple that dictates the player's current strategy based on other strategy functions
        This function determines strategy by a number of cascading if statements, similar to a simplified decision tree.
        Args:
            prices (dict): Prices of market in current location
            bm (list): List of black markets passed from take_turn
            gm (list): List of grey markets passed from take_turn
        Output:
            cmd (tup): A tuple of Command.CMD, data, output by other strategy functions
        """
        # get the set of black and grey markets
        bg_set = set(bm + gm)
        bm = set(bm)

        # check if goal achieved
        self.check_goal()

        # On the very first turn, while the player is safe, take stock of surroundings
        # Player will decide movement or research according to position
        if self.turn == 1:
            return self.first_turn(bg_set)

        # The highest priority is if the player is in a black/grey market
        # Player moves to the nearest white market
        # Player will change the target location every turn if the target location is located in the black/grey regions
        if self.loc in bg_set:
            if self.loc in bm:
                self.gold -= self.black_penalty
            if self.target_loc in bg_set or self.target_loc is None:
                self.target_loc = self.nearest_white(self.loc, bg_set)
            return Command.MOVE_TO, self.get_next_step(self.target_loc)

        # Next highest priority:
        # If the gold is negative, the player must cut losses by dumping inventory at the current market
        if self.gold < 0:
            if prices:
                return self.cut_losses(prices)
            else:
                return Command.RESEARCH, None

        # Next highest priority:
        # Towards the end of the game, the player must go to the centre of the map to avoid complexity
        # At the center of the map, the player dumps all his excess inventory to maximise score
        if self.turn >= self.max_turn - self.final_turns:
            return self.dump_stock(prices)

        # Commence Phase 1:
        # While we don't have information on a third of the markets in the game. Move around and research
        if len(self.market_prices.keys()) < len(self.map.get_node_names()) // 2:
            return self.wander(prices, bg_set)

        # Update the statistical knowledge of the player every turn
        self.update_stats(bg_set)

        # Once we have enough information
        # Commence Phase 2:
        # With current gold, maximise profit by arbitrage.
        # When a certain number of turns remain, proceed to buy with the purpose of achieving the goal
        # Once the goal is achieved, the player will choose to maximise profits again
        buy, sell = self.buy_sell(prices)
        if self.turn < self.max_turn * 2 / 3:
            target_market = self.search_market(bg_set, risk=0)
            return self.profit_max(target_market, buy, sell, prices, bg_set)
        elif not self.goal_achieved:
            target_market = self.search_market(bg_set, risk=1)
            return self.opt_goal_achievement(target_market, buy, prices, bg_set)
        else:
            target_market = self.search_market(bg_set, risk=1)
            return self.profit_max(target_market, buy, sell, prices, bg_set, risk=1)

    def check_goal(self):
        """Check if goal is achieved by comparing inventory and goal.
           Switch self.achieved_goal = True if achieved goal.
        """
        for prod, amount in self.goal.items():
            if self.inventory[prod][0] < amount:
                return None
        self.goal_achieved = True
        return None

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
        Output:
            cmd (tup): A tuple of (Command.CMD, data)
        """
        # Set the central market
        self.ctr, distances = self.central_market()

        # Determine the furthest node from the central market
        t1_target = max(distances, key=distances.get)

        # Store information for the final turns needed for endgame.
        # self.final_turns = len(self.get_path_to(t1_target)) + len(self.goal)
        self.final_turns = len(self.goal)

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

    def get_path_to(self, target_location):
        """Finds the fastest path by employing a breadth-first search algorithm.
        Since all edges are currently unweighted, only a simplified breadth-first
        while storing each previous node is required
        """
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
        Player is meant to move to the central market toward the end of the game as part of risk aversion tactic
        """
        # To iterate only once over each node, the minimum distance is first
        # initialised as a maximum possible distance, i.e. the corner of the
        # map. The shape of the circle is also a rectangle, equivalent to the
        # map dimensions. Therefore, the true safest market must satisfy the
        # map ratios as well.
        #
        # If the current minimum distance is greater than the distance of
        # the current node to the map center, reassign. This must be done
        # while keeping the angle of incident to the map center in mind
        map_center = self.map.map_width / 2, self.map.map_height / 2
        map_corner = self.map.map_width, self.map.map_height
        node_coords = self.map.map_data["node_positions"]
        map_ratio = self.map.map_width / self.map.map_height
        min_dist = self.dist_to(map_corner, map_center)
        distance_dict = dict()
        min_node = self.loc
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

    def nearest_white(self, target_market, bg_set, assessed=set()):
        """Returns the market location closest to the target market that is white
           If the target market is white, returns the target.
        Args:
            bg_set (set): Set of black and grey markets
            target_market (str): Target market from search. 
        
        Output:
             (str): return the nearest white market from the current location
        """
        # return the target market if it is a white market
        if target_market not in bg_set:
            return target_market

        # Get the neighbours of the target market that have not been assessed
        # If this set less the black/grey market set is not empty,
        # Return a random target white market
        neighbours = self.map.get_neighbours(target_market)
        neighbour_set = neighbours - assessed
        white_set = neighbour_set - bg_set
        if white_set:
            return random.choice(list(white_set))

        # Otherwise, the assessed locations and all of the neighbours are black
        # The assessed should be updated to include all neighbours and a random
        # next_market chosen from any of the neighbour set
        else:
            assessed.add(target_market)
            assessed = assessed.union(neighbour_set)
            next_market = random.choice(list(neighbours))
            return self.nearest_white(next_market, bg_set, assessed)

    def cut_losses(self, prices):
        """Panic button function for the player to decide what part of his inventory to sell if goal is negative.
        This avoids any further interest charges, the player will first dump any excess stock. If this function is
        called without excess stock, the player will then choose which item that can be sold while maximising current
        assets"""
        # Price and inventory structure for reference
        # Prices = {product: (prices, amounts)}
        # Inventory = {product: (amount, cost)}
        # Determine which product to dump if it is in excess.
        excess_product = self.any_excess(set(prices.keys()))
        if excess_product:
            to_sell = excess_product
            sell_num = self.excess_stock(excess_product)

        # If there is no excess product, identify minimum asset loss
        else:
            final_assets = -math.inf
            to_sell = None
            sell_num = 0
            for product, info in self.inventory.items():
                # Calculate the number of the currently assessed product required to
                # offset the negative gold cost
                tmp_num = -int(self.gold // prices[product][0])
                # Only consider the items in inventory that can fully amortise the negative gold
                if info[0] >= tmp_num:
                    # Assess the situation by creating a faux inventory for analysis
                    tmp_inv = copy.deepcopy(self.inventory)
                    tmp_inv, _ = self.update_inv_gold(prices, tmp_inv, product, tmp_num, gold=0, action=1)
                    tmp_assets = sum([cost for amt, cost in tmp_inv.values()])
                    if tmp_assets >= final_assets:
                        final_assets = tmp_assets
                        to_sell = product
                        sell_num = tmp_num

        # If the player does not have enough in his inventory, he will decide to dump the most expensive of
        # any one of the player's inventory.
        if to_sell is None:
            to_sell = max(self.inventory, key=lambda x: self.inventory[x][0] * prices[x][0])
            sell_num = self.inventory[to_sell][0]

        # Return the command tuple for the stategy output
        return Command.SELL, (to_sell, sell_num)

    def excess_stock(self, product):
        """Function to determine the amount of excess stock of a given product.
        Args:
            product (str): Product currently assessed
        Output:
            (int): The number of items in the inventory of that product that is greater than the goal amount.
            """
        return max(int(self.inventory[product][0] - self.goal[product]), 0)

    def any_excess(self, sell_set):
        """Function to determine if any excess stock in sell set exists in player inventory.
        The player should already be in a position to determine if the current market has a set of items that are
        worthy of sale. This returns the product if the player has an excess of that product to sell for profit.
        Args:
            sell_set (set): The set of valid products to sell
        Output:
            product (str): the first product that is in excess
        """
        for product in sell_set:
            if self.excess_stock(product):
                return product
        return None

    def dump_stock(self, prices):
        """Function to dump inventory at the end game to maximise score.
        If the player has unsuccessfully reached goals, the player will sell all inventory
        of that product that the player has.
        Args:
            prices (dict): The prices and amounts of items being sold at this market
        Output:
            cmd (tup): A command tuple Command.COMMAND, and associated viable data
        """
        for product in prices.keys():
            # If a particular product in inventory does not meet the goal and occupies inventory space
            # Dump the item. Otherwise, sell any excess stock.
            if 0 < self.inventory[product][0] < self.goal[product]:
                to_dump = self.inventory[product][0]
            else:
                to_dump = self.excess_stock(product)

            if to_dump:
                return Command.SELL, (product, to_dump)
        return Command.PASS, None

    def wander(self, prices, bg_set):
        """Function for the player to wander relatively aimlessly in the map to collect more information in places that
        has not been previously researched. This is invoked especially when not enough market information is avaialble.
        Args:
            prices (dict): The prices and amounts of items being sold at this market
            bg_set (set): The set of black and grey markets in the game
        Output:
            cmd (tup): A command tuple Command.COMMAND, and associated viable data
        """
        # If the current market is neither researched nor in the set of black and grey markets,
        # research this market
        if self.loc not in self.researched.union(bg_set):
            self.researched.add(self.loc)
            return Command.RESEARCH, None
        else:
            # Otherwise, check if we have arrived at a previously defined target market
            # If the player has not reached his target, move to the next step towards that target
            if self.loc != self.target_loc and self.target_loc is not None:
                return Command.MOVE_TO, self.get_next_step(self.target_loc)
            
            # If the player has reached his target, choose a new location to wander to
            else:
                # If the player's only choice is the current node, the end game has been reached and
                # no market is available. The player should pass to prevent excess charges.
                new_choice = self.choose(bg_set, {self.loc})
                if self.target_loc == new_choice:
                    return Command.PASS, None

                # Otherwise, set a new course for wandering!
                self.target_loc = new_choice
                return self.wander(prices, bg_set)

    def choose(self, bg_set, ignore_set):
        """Function for the player to wander relatively aimlessly in the map to collect more information in places that
        has not been previously researched. This is invoked especially when not enough market information is avaialble.
        Args:
            bg_set (set): The set of black and grey markets in the game
            ignore_set (set): The set of locations to ignore when choosing where to go.
        Output:
            (str): A randomly chosen location subjected to the restraints of black and grey markets
        """
        markets = set(self.map.get_node_names())
        researched = self.researched
        # First check if there are any available markets that have not been researched
        # If there are any available markets, choose a random one to return
        avail = list(markets - researched - bg_set - ignore_set)
        if avail:
            return random.choice(avail)
        else:
            # Check if there are any markets that are researched to return
            avail = list(markets - bg_set - ignore_set)
            if avail:
                return random.choice(avail)

            # The only case where the above set is empty is if the player is in the ignore_set
            # In which case, just return a random location that is not in the black and grey set
            else:
                return random.choice(list(markets - bg_set))

    def update_stats(self, bg_set):
        """Function to update player knowledge on statistics of the market the only useful 
        information to the player is a target region where the player can actually do business.
        This function does not return anything as it is meant to update the class instances'
        attributes
        Args:
            bg_set (set): Set of black and grey markets
        Output: None
        """
        product_price = defaultdict(list)

        # The target region for the risk averse player is the region that does not include any
        # black or grey markets. For this reason, the player will only update the statistics within
        # this region.
        target_region = set(self.market_prices.keys()) - bg_set
        for market in target_region:
            for product in self.market_prices[market].keys():
                product_price[product].append(self.market_prices[market][product][0])

        # Store the statistical information of the products
        # price stats are: {product: (price variance, 75th percentile, 25th percentile)}
        self.price_stats = {product: (np.var(product_price[product]),
                                      np.percentile(product_price[product], 75),
                                      np.percentile(product_price[product], 25))
                            for product in product_price.keys()}

        # The player will then create a list in order of their variances to determine which item
        # will sell for the greatest profit. This is ordered in descending order to determine which
        # item is required to trade first
        target_list = sorted(self.price_stats.items(), key=lambda x: -x[1][0])[:5]
        self.profit_order = [product[0] for product in target_list]

        return None

    def buy_sell(self, prices):
        """ The purpose of selling is to maximise profit(buy low, sell high to take arbitrage).
        To deem a product worth trading, the player assesses the variances of the product previously
        calculated. Small variances implies the price of the product is stable, and there is no room
        for arbitrage.
        1. Make a target list consisting of the first 5 products as the products we aim to sell
        2. Check if the market sells the target list products. If yes, go to step 3
        3. Check if we are suppose to sell the products in this market, ie. is it the right place to sell?
                 Decision making:
                    If the price at this market is above eg. the 75th percentile of the all the prices 
                    for this product, it suggests it is the right place to sell
                    --- Implication: if it's below 25th percentile, possibly a right place to buy
                 If yes, go to step 4
        4. Check if our inventory contains the target products which the market has
                 If yes, go to step 5
        5. Sell the target products
        Args:
            prices (dict): the market prices at the player's current location.
        Output:
            buy_set, sell_set (tup): A tuple of set() objects that contain the products that are
            worthy of purchase (buy_set) or sale (sell_set)
        """
        # Check if the market sells the target list products
        to_trade = {target for target in self.profit_order if prices.get(target)}

        # if the market doesn't sell the target products, function ends
        if not to_trade:
            return None, None

        # check if it's the right market to sell
        # While the market is the right one to sell, we must have the an amount in our inventory to sell
        sell_set = {product for product in to_trade
                    if prices[product][0] >= self.price_stats[product][1]
                    and self.inventory[product][0] > 0}

        # The right market to buy MUST have non-zero items to buy
        buy_set = {product for product in to_trade
                   if prices[product][0] <= self.price_stats[product][2]
                   and prices[product][1] > 0}

        
        return buy_set, sell_set

    def search_market(self, bg_set, risk=0):
        """Given current location, inventory, gold, and goal, what is the best market to buy from?
           What market to choose if doesn't have any researched/rumoured information?
           The action the player takes for the market to search is dependent on several factors,
           most importantly if the player is risk taking or risk averse.
           
           If the player is risk taking, presumably the player will ignore the objective to reach
           the goal; the player buys and sells purely for profit maximisation.

           If the player is not, the player will achieve their goal and only buy and sell according
           to keep goal amounts to gatekeep the score.

        Args:
            bg_set (set): Set of black and grey markets
            risk (int): 0 if the player is attempting to buy and sell as much as possible
                        1 if the player is only buying and selling to achieve the goal
        Output:
            target_market (str): returns the target market from search. If all information on markets
                                 are black, returns None
        """
        if risk:
            # If the player is risk averse, the player wishes to first buy up to the goal amount
            action = 0
            product_targets = [product for product, amount in self.goal.items()
                               if self.inventory[product][0] < amount]
            # If this is empty, the player has reached the goal amount, and wishes to sell
            # The player will sell any excess stock
            if not product_targets:
                action = 1
                product_targets = [product for product in self.profit_order
                                   if self.excess_stock(product)]
                # If this is also empty, the player has only the minimum amount of goods
                # The player must then choose to buy
                if not product_targets:
                    action = 0
                    product_targets = self.profit_order

        # If the player is not risk averse, the player will choose to buy or sell according to
        # profit amounts
        else:
            action = 1
            product_targets = [product for product in self.profit_order
                               if self.inventory[product][0] > 0]
            for product, stats in self.price_stats.items():
                if self.gold > stats[2] and self.inventory[product][0] == 0:
                    action = 0
                    product_targets.append(product)
                    break

        # The player's target region is still one without black or grey markets, since the purchase
        # function will empty our gold coffers completely, and we must avoid going into the
        # negative.
        target_region = set(self.market_prices.keys()) - bg_set
        possible_targets = set()
        if product_targets:
            for market in target_region:
                for product in product_targets:
                    market_price = self.market_prices[market][product][0]
                    if action == 0:
                        # get the 25th percentile price of this product to buy
                        curr_price = self.price_stats[product][2]

                        # check if market is not blacklisted for this product
                        if market not in self.blacklist[product]:
                            if market_price < curr_price:
                                possible_targets.add(market)
                    else:
                        # get the 75th percentile price of this product to sell
                        curr_price = self.price_stats[product][1]
                        if market_price > curr_price:
                            possible_targets.add(market)

        # calculate the distances to these markets
        dist_to_target = {market: len(self.get_path_to(market))
                          for market in possible_targets if market}
        if dist_to_target:
            target_market = min(dist_to_target, key=dist_to_target.get)
        else:
            target_market = None

        return target_market

    def profit_max(self, target_market, buy, sell, prices, bg_set, risk=0):
        """Switch function for the player to maximise profit instead of following the goal.
        Args:
            target_market (str): The location of market of interest as a result of market searching.
            buy (set): The set of items to buy at the current location based on statistical knowledge
            sell (set): The set of items to sell at the current location based on statistical knowledge
            prices (dict): The market prices of the current location.
            bg_set (set): The set of black and grey markets.
            risk (int): 0 if the player is risk taking and purchasing for profit.
                        1 if the player is risk averse and selling only excess stock.
        Output:
            cmd (tup): This function outputs a Command.CMD, data for a given command according to
                       the function it calls.
        """
        # If the player knows the prices of the current market, the player proceeds with deciding what todo
        # If the player doesn't know, the player will research the market.
        if prices:
            # If the statistics of the player demands it, buy will be not empty
            # The player then checks if he can afford to buy anything at this market
            # If he can, he buys for profit.
            if buy and self.afford_anything(prices, buy):
                return self.profit_buy(prices, buy, bg_set)

            # Otherwise, the player then checks if he has any excess stock if 
            # the current market is statistically relevant to sell.
            # The player then chooses to sell according to the current risk taking
            # behaviour.
            elif sell and self.any_excess(sell):
                return self.profit_sell(prices, sell, bg_set, risk)

            # The player then decides if a target market has been acquired as a result
            # of a previous search, and moves to that market to make a purchase decision.
            elif target_market:
                self.target_loc = target_market
                return self.move_to_buy(prices, buy, bg_set)

            # Otherwise, the player needs more market information, and must therefore
            # wander the map
            else:
                return self.wander(prices, bg_set)

        return Command.RESEARCH, None

    def profit_buy(self, prices, buy_set, bg_set):
        """Function to decide how much to buy to maximise profit.
        Args:
            prices (dict): the current market prices
            buy_set (set): the set of products to buy in this market
            bg_set (set): the set of black and grey markets
        Output:
            cmd (tuple): Command.CMD, data tuple, depending on if a product is purchased or if more
                         information is required.
        """
        # If the player knows the prices of the current market, the player proceeds with deciding what todo
        # If the player doesn't know, the player will research the market.
        if not prices:
            return Command.RESEARCH, None

        # The player assesses the products in order of profit as previously decided.
        # These products must be within the buy_set, which confirms that this market is within the
        # 25th percentile of prices for buying purposes.
        for product in self.profit_order:
            if product in buy_set:
                buy_amount = self.afford_amount(prices, product)
                if buy_amount > 0:
                    return Command.BUY, (product, buy_amount)

        # If buy_set is empty, then the player needs to wander from the current location.
        return self.wander(prices, bg_set)

    def profit_sell(self, prices, sell_set, bg_set, risk=0):
        """Function to decide how much to sell to maximise profit.
        Args:
            prices (dict): the current market prices
            sell_set (set): the set of products to sell in this market
            bg_set (set): the set of black and grey markets
            risk (int): 0 if the player is risk taking and purchasing for profit.
                        1 if the player is risk averse and selling only excess stock.
        Output:
            cmd (tuple): Command.CMD, data tuple, depending on if a product is purchased or if more
                         information is required.
        """
        # If the player knows the prices of the current market, the player proceeds with deciding what todo
        # If the player doesn't know, the player will research the market.
        if not prices:
            return Command.RESEARCH, None

        # The player assesses the products in order of profit as previously decided.
        # These products must be within the buy_set, which confirms that this market is within the
        # 75th percentile of prices for buying purposes.
        for product in self.profit_order:
            if product in sell_set:
                if risk:
                    to_sell = self.excess_stock(product)
                else:
                    to_sell = self.inventory[product][0]
                if to_sell:
                    return Command.SELL, (product, to_sell)

        # If sell_set is empty, then the player needs to wander from the current location.
        return self.wander(prices, bg_set)

    def afford_anything(self, market_prices, buy_set):
        """Boolean function if the player can afford anything at the current market
        Args:
            market_prices (dict): {market:{product:[price, amount]}}
                                   dictionary of market and products and price they sell.
            buy_set (set): set of products that are statistically worth buying at this market
        
        Output:
            (bool): True - If anything is worth buying at this market
                    False - If nothing is worth buying at this market
        """
        if not buy_set:
            return False
        for product in buy_set:
            if self.afford_amount(market_prices, product) > 0:
                return True
        return False

    def opt_goal_achievement(self, target_market, buy, prices, bg_set):
        """Function to for the player to optimise to achieve the goal.
        Args:
            target_market (str): The target market for the player as a result of a market search.
            buy (set): The set of items to buy at this market
            prices (dict): The prices of this market
            bg_set (set): The set of black and grey markets
        Output:
            cmd (tup): The tuple of Command.CMD, data as a result of either the buy or wander
                       functions.
        """
        # If the search market returns a worthy market, the player goes to the market
        # with the aim to buy
        if target_market:
            self.target_loc = target_market
            return self.move_to_buy(prices, buy, bg_set)

        # Otherwise, the player must wander to gather more information.
        else:
            return self.wander(prices, bg_set)

    def move_to_buy(self, prices, buy_set, bg_set):
        """Function that allows the player to continue moving with purpose, instead of wandering.
        This function is normally called once a target market has been acquired and the player
        does not want to waste time by wandering around other markets. Note that the searched market
        changes dynamically every turn.
        Args:
            prices (dict): the prices of products at this market
            buy_set (set): the set of items to buy that are statistically worth buying, at this
                           market
            bg_set (set): the set of black and grey markets
        Output:
            cmd (tuple): The tuple of Command.CMD, data
        """
        # If the player has not arrived at the target location, move there with purpose.
        if self.loc != self.target_loc:
            return Command.MOVE_TO, self.get_next_step(self.target_loc)
        
        # otherwise, the player must have arrived at the location.
        elif self.loc == self.target_loc:
            # If the player knows the prices of the current market, the player proceeds with deciding what todo
            # If the player doesn't know, the player will research the market.
            if prices:
                # player now assesses to buy products to achieve the goal.
                # if the the goal has been achieved, purchase item returns None.
                # the player then should choose to buy to maximise profit.
                purchase_item = self.goal_purchase(prices)
                if purchase_item:
                    return Command.BUY, purchase_item
                else:
                    return self.profit_buy(prices, buy_set, bg_set)
            return Command.RESEARCH, None

    def goal_purchase(self, market_info):
        """Return the item and amount to buy when player is at a destination market, subjected to
        the goal condition of the player's inventory.
            1. Find required item to buy (item in goal and under target amount)
            2. Calculate amount to buy
            3. If there are multiple items to required select base on highest score
               after purchase

        Args:
            market_info (dict): the prices of this market.
        Output: 
            (product, amount) (tuple): The tuple of product and amount to buy of that product.
                                       If the goal has been achieved, returns None.
        """
        max_score = self.gold
        buy_amt = 0
        to_buy = None

        # find the best item to buy
        for product in market_info.keys():

            # initialize dummy variables used to record after purchase inventory and gold to compute score
            tmp_inventory = copy.deepcopy(self.inventory)
            tmp_gold = self.gold

            # if product is what we need
            if product in self.goal.keys() and self.inventory[product][0] < self.goal[product]:
                tmp_amt = min(int(self.afford_amount(market_info, product)),
                              self.goal[product] - self.inventory[product][0])

                # update dummy variables to reflect after purchase inventory and gold level
                tmp_inventory, tmp_gold = self.update_inv_gold(market_info, tmp_inventory, product, tmp_amt,
                                                               tmp_gold, action=0)

                # compute score and update best item to buy
                tmp_score = self.compute_score(tmp_inventory, tmp_gold, self.goal)
                if tmp_score > max_score:
                    to_buy = product
                    buy_amt = int(tmp_amt)
                    max_score = tmp_score
        if to_buy is not None:
            if buy_amt > 0:
                return to_buy, buy_amt
        else:
            return None

    def afford_amount(self, market_prices, product):
        """Compute the maximum amount the player can purchase of a particular product
        at the current market.
        Args:
            market_prices (dict): the prices of this market
            product (str): the product being assessed.
        Output:
            (int): The amount of the product that the player can afford to buy
        """
        return int(min(market_prices[product][1],
                       self.gold // market_prices[product][0]))

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

    def update_inv_gold(self, prices, inv, prod, prod_amt, gold, action=0):
        """Helper function to update a given inventory and gold depending on the player action.
        Args:
            prices (dict): market prices in the format {product: (price, amount)}
            inv (dict): inventory type in the format {product: (amount, asset cost)}
            prod (str): the product to update the inventory
            prod_amt (int): the amount of product to update the inventory
            gold (float): the amount of starting gold
            action (int): 0 if the player is buying
                          1 if the player is selling
        Output:
            inv (dict): Updated dictionary
            gold (float): Updated gold
        """
        # If the player is buying, reduce inventory and increase gold accordingly
        if action == 0:
            inv[prod] = (inv[prod][0] + prod_amt,
                         prod_amt * prices[prod][0] + inv[prod][1])
            gold -= prod_amt * prices[prod][0]

        # If the player is selling, do the reverse
        else:
            single_cost = inv[prod][1] / inv[prod][0]
            inv[prod] = (inv[prod][0] - prod_amt,
                         max(inv[prod][1] - prod_amt * single_cost, 0))
            gold += prod_amt * prices[prod][0]

        return inv, gold

    def get_next_step(self, target_location):
        """Returns the next step on the path required, since the player can only move to an adjacent
        market.
        Args:
            target_location (str): The target location to move to.
        Output:
            adjacent_market (str): The market to go to. If the player is already at the target,
                                   returns None
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


    def __repr__(self):
        """Define the representation of the Player as the state of
        current attributes.
        """
        s = str(self.__dict__)
        return s


# ========================= TESTS ===================================

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
    # test_suite.addTest(MapTestCase('test_search_market'))

    # Movement testing
    test_suite.addTest(MovementTestCase('test_move'))
    test_suite.addTest(MovementTestCase('test_stay'))

    # Knowledge testing
    test_suite.addTest(KnowledgeTestCase('test_check_goal'))
    test_suite.addTest(KnowledgeTestCase('test_rumours'))
    test_suite.addTest(KnowledgeTestCase('test_prices'))
    test_suite.addTest(KnowledgeTestCase('test_buy_sell'))

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

    # Superceded test
    # def test_search_market(self):
    #     p = Player()
    #     p.map = test_static_map()
    #     p.loc = "E"
    #     prod = ["Food", "Electronics", "Social", "Hardware"]
    #     goal = dict(zip(prod, [5]*len(prod)))
    #     p.set_goal(goal)
    #     nodes = p.map.get_node_names()
    #     temp = list(zip(cycle(prod), map(list, enumerate(range(len(prod) * len(nodes))))))
    #     temp2 = []
    #     for i in range(len(nodes)):
    #         temp2.append((nodes[i], dict(temp[(i*4):(4*(i+1))])))
    #     p.market_prices = dict(temp2)
    #     # p.market_prices should look like:
    #     # {'A': {'Food': [0, 0],
    #     #        'Electronics': [1, 1],
    #     #        'Social': [2, 2],
    #     #        'Hardware': [3, 3]},
    #     #  'B': {'Food': [4, 4],
    #     #        'Electronics': [5, 5],
    #     #        'Social': [6, 6],
    #     #        'Hardware': [7, 7]}}...
    #     # test when inventory be empty with no bm and gm
    #     target = p.search_market(set(), risk=1)
    #     self.assertEqual(target, "A")
    #     # test when black market is "A"
    #     target = p.search_market(set("A"), risk=1)
    #     self.assertEqual(target, 'B')
    #     # test when goal is reached
    #     p.inventory = dict(zip(prod, map(list, [(5, 0)] * len(prod))))
    #     target = p.search_market(set(), risk=1)
    #     self.assertIsNone(target)


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

    def test_buy_sell(self):
        p1 = Player()
        gold = 1000.0
        goal = {"Food": 10, "Social": 15}
        market_prices = {'A': {'Food': (109, 700),
                               'Electronics': (755, 210),
                               'Social': (47, 1400),
                               'Hardware': (881, 35)},
                         'B': {'Food': (95, 700),
                               'Electronics': (384, 210),
                               'Social': (49, 1400),
                               'Hardware': (633, 35)},
                         'C': {'Food': (80, 700),
                               'Electronics': (382, 210),
                               'Social': (46, 1400),
                               'Hardware': (432, 35)},
                         'D': {'Food': (113, 700),
                               'Electronics': (782, 210),
                               'Social': (73, 1400),
                               'Hardware': (537, 35)}}
        p1.set_gold(gold)
        p1.set_goal(goal)
        p1.inventory["Food"] = (5, 150)
        p1.market_prices = market_prices
        p1.update_stats(set())
        prices = {'Food': (113, 700),
                  'Electronics': (794, 210),
                  'Social': (64, 1400),
                  'Hardware': (597, 35)}
        buy, sell = p1.buy_sell(prices)
        self.assertFalse(buy)
        self.assertTrue(sell)


# Create a class for testing strategy.
class StrategyTestCase(unittest.TestCase):
    # Testing first turn strategy
    def test_first_turn(self):
        p = Player()
        p.map = test_map()
        p.loc = "V"
        goal = {'Food': 10,
                'Electronics': 10,
                'Social': 10,
                'Hardware': 10}
        p.set_goal(goal)

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
        self.assertIsNone(p.goal_purchase(prices))

        prices['Food'] = (100, 5)
        prod, amt = p.goal_purchase(prices)
        self.assertEqual(prod, 'Food')
        self.assertEqual(amt, 5)


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
    # # Print visual diagnostics
    # player = Player()
    # player.map = test_map()
    # player.loc = "A"
    # central_market = player.central_market()[0]
    # next_step = player.get_next_step(central_market)
    # next_path = player.get_path_to(central_market)
    # player.map.pretty_print_map()
    # print(f"From {player.loc}, the next step to {central_market} is {next_step}.")
    # print(f"The quickest path is {list(next_path)}. This takes {len(next_path)} turns.")
    # print(f"The central market is {central_market}")

    runner = unittest.TextTestRunner()
    runner.run(suite())

