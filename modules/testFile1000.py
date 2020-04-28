import Game
from Player import Player
import time

start = time.time()
total_res = []
game_turns = Game.NUM_TURNS
games_run = 200

player_nums = 7

for i in range(games_run):
    p = []
    for j in range(player_nums):
        p.append(Player())
    g = Game.Game(p, verbose=True)
    res = g.run_game()
    print(res)
    if min(res) < 0:
        break
    total_res += res

end = time.time()
time_taken = end - start

print(f"Number of players per game = {len(p)}")
print(f"Score Average of {games_run} games = {sum(total_res)/len(total_res)}")
print(f"Time taken for {games_run} games: {time_taken:.2f} seconds")
print(f"Average time for each turn: {time_taken / (len(p) * games_run * game_turns):.6f} seconds")
print(f"Range = [{min(total_res)}, {max(total_res)}]")

