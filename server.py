import time
from struct import unpack
import asyncio
import websockets

from game import Game
from game_error import GameError

ip = '85.229.19.61'
port = 63834
bufferSize = 1024

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
UDPServerSocket.bind((localIP, localPort))
print("Web server up and listening")


max_length = 1024
def flood(connections, game, message):
    try:
        for index in range(len(connections)):
            ip_address = connections[index]
            UDPServerSocket.sendto(b'1'+game.to_bytes(index), ip_address)
            UDPServerSocket.sendto(b'2'+message.to_bytes(), ip_address)

    except IndexError:
        print('Index error in flood')


async def receive(websocket):
    async for message in websocket:
        message, address = UDPServerSocket.recvfrom(bufferSize)
        print(MESSAGE, address)
        if address not in connections:
            connections.append(address)
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
        if arg not in range(4 * len(connections)):
            continue

        try:
            GAME.next_player(command, arg)
        except GameError as e:
            server_message = e
        flood(connections, GAME, server_message)


async def main():
    async with websockets.serve(receive, ip, port):
        await asyncio.Future()  # run forever



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    GAME = Game()
    connections = []

    server_message = GameError('Waiting.')

