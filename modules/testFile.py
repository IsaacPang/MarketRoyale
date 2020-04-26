from Game import Game
from Player import Player


p = Player()
g = Game([p], verbose=True)
res = g.run_game()
print(res)