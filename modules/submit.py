import json
import socket


def send_to_server5002(js):
    """ Open socket and send the json string js to server with EOM appended, and wait
        for \n terminated reply.
        js - json object to send to server
    """
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('128.250.106.25', 5002))      # 5s per turn
    # clientsocket.connect(('128.250.106.25', 5003))    # 0.1s per turn

    clientsocket.send("""{}EOM""".format(js).encode('utf-8'))

    data = ''
    while data == '' or data[-1] != "\n":
        data += clientsocket.recv(1024).decode('utf-8')
    print(data)


filedict = {
    1: "OldShitPlayer",
    2: "ShitPlayerReupload",
    3: "Holiday_Maker",
    4: "Vacation_Setter",
    5: "OldShitPlayer_DEL",
    6: "ShitPlayerReupload_DEL"
}

FILENAME = filedict[6]

with open(f"../submissions/submission_{FILENAME}.json") as f:
    json_data = json.load(f)

js = json.dumps(json_data, indent=4)
send_to_server5002(js)
