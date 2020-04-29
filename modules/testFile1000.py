import Game
from Player import Player as Player1
from Player2 import Player as Player2
from Player3 import Player as Player3
import time

start = time.time()
total_res1 = []
total_res2 = []
total_res3 = []
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
        p3 = []
        for j in range(player_nums):
            p1.append(Player1())
            p2.append(Player2())
            p3.append(Player3())
        g = Game.Game(p1 + p2 + p3, verbose=True)
        res = g.run_game()
        print(res)
        if min(res) < 0:
            break
        total_res1 += res[:len(p1)]
        total_res2 += res[len(p1):len(p1 + p2)]
        total_res3 += res[len(p1 + p2):]

    end = time.time()
    time_taken = end - start

    print(f"Number of players per game = {player_nums * 2}")
    print(f"Number of games run is {games_run}")
    print(f"Score Average for Player 1 = {sum(total_res1)/len(total_res1)}")
    print(f"Score Average for Player 2 = {sum(total_res2)/len(total_res2)}")
    print(f"Score Average for Player 3 = {sum(total_res3)/len(total_res3)}")
    print(f"Time taken for {games_run} games: {time_taken:.2f} seconds")
    print(f"Average time for each turn: {time_taken / (player_nums * games_run * game_turns):.6f} seconds")
    print(f"Range for Player 1 = [{min(total_res1)}, {max(total_res1)}]")
    print(f"Range for Player 2 = [{min(total_res2)}, {max(total_res2)}]")
    print(f"Range for Player 3 = [{min(total_res3)}, {max(total_res3)}]")

