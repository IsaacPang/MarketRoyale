"""
Generates a unique json file by using the standard python
library, with file.read()
TODO: change the team name
TODO: add the socket function and a __main__ call
"""
import json
import datetime
from time import time
import socket
from inspect import getsource

DATE = datetime.date.isoformat(datetime.date.today())
HASH = f"{time():.0f}"[-8:]
FILE = f"submission_{DATE}_{HASH}.json"
PATH = f"../submissions/{FILE}"

COMMAND = "ADD" # "ADD", "DEL", "PING"
SYNDICATE = 8
TEAM_NAME = "The Rod Polishers"

with open("Player.py", 'r') as f:
    DATA = f.read()

INPUT = {}
INPUT["cmd"] = COMMAND
INPUT["syn"] = SYNDICATE
INPUT["name"] = TEAM_NAME
INPUT["data"] = DATA

print(PATH)
with open(PATH, 'w') as f:
    json.dump(INPUT, fp=f, indent=4)
