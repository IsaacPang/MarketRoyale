"""
Generates a unique json file by using the inspect library
getsource() function on Player module.
TODO: change the team name
TODO: add the socket function and a __main__ call
"""
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
TEAM_NAME = "Insert Name Here"

INPUT = {"cmd": COMMAND, "syn": SYNDICATE, "name": TEAM_NAME, "data": DATA}


def send_to_server5002(js):
    """ Open socket and send the json string js to server with EOM appended, and wait
        for \n terminated reply.
        js - json object to send to server
    """
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Port 5002: 5s turns
    # Port 5003: 0.1s turns
    clientsocket.connect(('128.250.106.25', 5002))

    clientsocket.send("""{}EOM""".format(js).encode('utf-8'))

    data = ''
    while data == '' or data[-1] != "\n":
        data += clientsocket.recv(1024).decode('utf-8')
    print(data)


# def send_to_server5003(js):
#     """ Open socket and send the json string js to server with EOM appended, and wait
#         for \n terminated reply.
#         js - json object to send to server
#     """
#     clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # Port 5003: 0.1s turns
#     clientsocket.connect(('128.250.106.25', 5003))
#
#     clientsocket.send("""{}EOM""".format(js).encode('utf-8'))
#
#     data = ''
#     while data == '' or data[-1] != "\n":
#         data += clientsocket.recv(1024).decode('utf-8')
#     print(data)


with open(PATH, 'w') as f:
    json.dump(INPUT, fp=f, indent=4)

js = json.dumps(INPUT, indent=4)
send_to_server5002(js)
# send_to_server5003(js)
