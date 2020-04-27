from Game import Game
from Player import Player


p1 = Player()
p = [p1]
g = Game(p, verbose=True)
res = g.run_game()
print(res)

