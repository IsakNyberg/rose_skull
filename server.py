import time
from struct import unpack
from web_socket import *
import socket

from game import Game
from game_error import GameError

localIP = '85.229.19.61'
localPort = 63834
bufferSize = 1024

TCPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
TCPsocket.bind((socket.gethostname(), localPort))
TCPsocket.listen(10)
print("UDP server up and listening")


max_length = 1024
def flood(connections, game, message):
    try:
        for index in range(len(connections)):
            ip_address = connections[index]
            frame = encode_frame(b'1' + game.to_bytes(index))
            TCPsocket.sendto(frame, ip_address)
            frame = encode_frame(b'2' + message.to_bytes())
            TCPsocket.sendto(frame, ip_address)

    except IndexError:
        print('Index error in flood')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    GAME = Game()
    connections = []

    server_message = GameError('Waiting.')
    while len(connections) < 255:
        TCPsocket.listen(bufferSize)
        CONNECTION, address = TCPsocket.accept()
        with CONNECTION:
            print('Connected by', address)
            while True:
                MESSAGE = CONNECTION.recv(1024)
                if not MESSAGE:
                    break
        print(MESSAGE, address)
        if address not in connections:
            handshake(MESSAGE)
            connections.append(CONNECTION)
            GAME.join(MESSAGE.decode('utf-8'))
            flood(connections, GAME, server_message)
            continue

        index = connections.index(address)
        if len(MESSAGE) != 2 or GAME.current_player_index != index:
            continue

        #DELTE
        if MESSAGE == b'BB':
            print('start')
            GAME.start()
            flood(connections, GAME, server_message)
            continue

        command, arg = unpack('BB', MESSAGE)
        if command not in (0, 1, 2, 3):
            continue
        if arg not in range(4*len(connections)):
            continue

        try:
            GAME.next_player(command, arg)
        except GameError as e:
            server_message = e
        flood(connections, GAME, server_message)
