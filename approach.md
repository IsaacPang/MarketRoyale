# Our Approach

## Minimum Submission Requirements

1. Ensure every submission:
    - has descriptive variable names.
    - has a module description.
    - has function docstrings.
    - has minor in-line comments.
    - is modular. All code must be non-repeating.
2. Submit at least 1 working player.
3. Submit more than 1 player and delete at least 1 player.
4. Ensure that each submitted player keeps track of goals and gold.
5. Ensure that each submitted player accounts for black and grey markets (keeping track of gold)

If we do all of the above, we will achieve a maximum score of 26/32

## Optimisation and Strategies
1. Move first, research later. Rationale: assume other players will research on their first node. We will want to move asynchronously as much as possible.
2. What is the minimum number of nodes we have to travel to give us the most amount of information? ILP / Machine Learning may be needed here
3. Maximising gold: How can we achieve our product purchase goal and buy and sell until the end of the game to maintain a gold surplus?
    - Buy low, sell high. If we have done 1 and 2, as long as we know that somewhere else is selling the same item for a higher price, we can buy the stock to sell
    - Profit maximising
        - Determine if the turns required to sell can justify going into debt
        - Determine if the selling can justify traversing (or selling to) black markets
4. Pathfinding algorithms: what is the optimal path to our desired end node? Djikstra's Algorithm / Breadth-First Search, since all paths have no weight, or weight = 1

These optimisations and leaderboard positions account for 6 extra points.
