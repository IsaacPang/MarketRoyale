# MarketRoyale
Python implementation of a Market Royale game for the assignment of MBusA2020

## Rules of Market Royale

A game is made of 7 players.\
A game consists of a map graph G(V,E) where:
- V (called markets).
- E (called roads).

The game progresses in turns, comprising of simultaneous player actions.\
The game lasts 50 turns.

At the start of the game:
- All players will each start at a random node. str
- All players will receive the same amount of randomised gold. float
- All players will receive a map of the markets and roads connecting them. <map object>
- All players will receive a different, random goal, to purchase a required amount of a certain product (or products). dict

The objective of the game is to approach different markets and look to purchase products within the given gold budget to achieve the goal. Any bonus gold leftover will be added as bonus points.

### Static game conditions
1. There are a finite set of products, P in the game.
2. Prices of products are different at each market.
3. Each market only sells a subset of products.
4. Each market sells only a finite amount of each product.
5. All roads are equidistant (edges have no weight).
6. If a player's gold amount is < 0, an 10% overdraft fee is incurred every turn.
7. Players may only move to an neighbouring market.

### Dynamic game conditions
1. The total stock in-game is finite, therefore items can be bought out in certain markets.
2. Markets can become grey markets at any time, an indicator that they will become black markets the next turn.
3. If a market becomes black, any present players or players entering the market node will be charged a -100 gold for every turn.
4. A player will automatically receive information from other players that arrive, or are in the same market node at the start of the turn. A maximum of 5 pieces of information in the form {market: {product: price}} for each other player in the node will be received. This information is from the other player's own market research.

### Player Moves
Every turn, a player can make 1 of the following moves:
1. Do nothing.
2. Research the CURRENT market node.
3. Buy products from the CURRENT market node.
4. Sell products to the CURRENT market node. Markets have an infinite capacity to buy.

### Player choice conditions:
1. A player may not purchase if the current market node has not been personally researched.
2. A player may only take 1 action per turn.
3. If multiple players purchase the same item, there is a possibility of a wasted turn, i.e. sold out item before able to buy.
