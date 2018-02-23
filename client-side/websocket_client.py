from websocket import create_connection
import signal
import sys

def signal_handler(signal, frame):
    global die
    print('Killing connection')
    die = True

ws = create_connection("ws://192.168.0.101:8080")
while(True):
    result = ws.recv()
    print("Received: '%s'" % result)
ws.close()
