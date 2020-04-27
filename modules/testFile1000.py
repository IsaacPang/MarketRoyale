from Game import Game
from Player import Player
import time

start = time.time()
total_res = []
games_run = 1000
for i in range(games_run):
    p1 = Player()
    p = [p1]
    g = Game(p, verbose=True)
    res = g.run_game()
    if res[0] < 0:
        print(f"Player has negative score!")
        print(f"{p1}")
        break
    total_res += res

print(sum(total_res)/len(total_res))
end = time.time()
print(f"Time taken for {games_run} games: {end - start:.2f} seconds")

