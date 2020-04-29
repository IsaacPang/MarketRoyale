import Game
from Player import Player as Player1
from Player2 import Player as Player2
import time

start = time.time()
total_res1 = []
total_res2 = []
game_turns = Game.NUM_TURNS
games_run = input("Number of games to run: ")

player_nums = input("Number of each player: ")

try:
    games_run = int(games_run)
except ValueError:
    assert(type(games_run) is int)

try:
    player_nums = int(player_nums)
except ValueError:
    assert(type(player_nums) is int)

if games_run and player_nums:
    for i in range(games_run):
        p1 = []
        p2 = []
        for j in range(player_nums):
            p1.append(Player1())
            p2.append(Player2())
        g = Game.Game(p1 + p2, verbose=True)
        res = g.run_game()
        print(res)
        if min(res) < 0:
            break
        total_res1 += res[:len(p1)]
        total_res2 += res[len(p1):]

    end = time.time()
    time_taken = end - start

    print(f"Number of players per game = {player_nums * 2}, {player_nums} Player 1s and {player_nums} Player 2s")
    print(f"Number of games run is {games_run}")
    print(f"Score Average for Player 1 = {sum(total_res1)/len(total_res1)}")
    print(f"Score Average for Player 2 = {sum(total_res2)/len(total_res2)}")
    print(f"Time taken for {games_run} games: {time_taken:.2f} seconds")
    print(f"Average time for each turn: {time_taken / (player_nums * games_run * game_turns):.6f} seconds")
    print(f"Range for Player 1= [{min(total_res1)}, {max(total_res1)}]")
    print(f"Range for Player 2= [{min(total_res2)}, {max(total_res2)}]")

