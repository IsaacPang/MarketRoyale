import json
import datetime
from time import time
import socket
from inspect import getsource
import Player

DATA = getsource(Player)

DATE = datetime.date.isoformat(datetime.date.today())
HASH = f"{time():.0f}"[-8:]
FILE = f"submission_{DATE}_{HASH}.json"
PATH = f"../submissions/{FILE}"

COMMAND = "ADD" # "ADD", "DEL", "PING"
SYNDICATE = 8
TEAM_NAME = "The Rod Polishers"

INPUT = {}
INPUT["cmd"] = COMMAND
INPUT["syn"] = SYNDICATE
INPUT["name"] = TEAM_NAME
INPUT["data"] = DATA

print(PATH)
with open(PATH, 'w') as f:
    json.dump(INPUT, fp=f, indent=4)
