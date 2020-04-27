from Game import Game
from Player import Player


total_res = []
for i in range(1):
    p1 = Player()
    p = [p1]
    g = Game(p, verbose=True)
    res = g.run_game()
    print(res)
    total_res += res

print(sum(total_res)/len(total_res))

