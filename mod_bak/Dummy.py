"""
DummyPlayer class.

A class of objects required to play the Market Royale game (Game.py).

The dummy player does not do anything. It does not modify the parent class.
The purpose of the dummy player is an initial test for Game and its output.
"""
import Command
from BasePlayer import BasePlayer


class DummyPlayer(BasePlayer):
    """Minimal player from spec"""
    def take_turn(self, location, prices, info, bm, gm):
        return Command.PASS, None

if __name__ == "__main__":
    
    from Game import Game

    g = Game([DummyPlayer()], verbose=True)
    res = g.run_game()
    print(res)


# dummy change