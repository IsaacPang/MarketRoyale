import Game
from Player import Player
import time

start = time.time()
total_res = []
game_turns = Game.NUM_TURNS
games_run = 1000
for i in range(games_run):
    p1 = Player()
    p = [p1]
    g = Game.Game(p, verbose=False)
    res = g.run_game()
    if res[0] < 0:
        print(f"Player has negative score!")
        print(f"{p1}")
        break
    total_res += res

print(sum(total_res)/len(total_res))
end = time.time()
time_taken = start - end
print(f"Time taken for {games_run} games: {time_taken:.2f} seconds")
print(f"Average time for each turn: {time_taken / (games_run * game_turns):.6f} seconds")

