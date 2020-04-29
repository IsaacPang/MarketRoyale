"""
Generates a unique json file by using the inspect library
getsource() function on Player module.
"""
import json
import datetime
from time import time
from inspect import getsource
import Player2

DATA = getsource(Player2)

# DATE = datetime.date.isoformat(datetime.date.today())
# HASH = f"{time():.0f}"[-8:]
FILENAME = "Vacation_Setter"
FILE = f"submission_{FILENAME}.json"
PATH = f"../submissions/{FILE}"

COMMAND = "ADD" # "ADD", "DEL", "PING"
SYNDICATE = 8
TEAM_NAME = "Vacation_Setter"

INPUT = {"cmd": COMMAND, "syn": SYNDICATE, "name": TEAM_NAME, "data": DATA}

with open(PATH, 'a') as f:
    json.dump(INPUT, fp=f, indent=4)

