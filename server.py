from time import sleep
from struct import unpack
from web_socket import *
import socket
import threading

from game import Game
from game_error import GameError

localIP = '192.168.10.150'
localPort = 63834
bufferSize = 1024

TCPsocket = None
while True:
    try:
        TCPsocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        TCPsocket.bind((socket.gethostname(), localPort))
        break
    except OSError as e:
        print(e)
        sleep(5)
print("Server up and listening")


def new_socket_handler(new_connection):
    new_message = new_connection.recv(1024)
    if b'GET /ws/' in new_message:
        hs = handshake(new_message)
        new_connection.sendall(hs)
        if b'HTTP/1.1 101' in hs:
            return str(new_message).split('/ws/')[-1].split(' ')[0]
        else:
            return ''
    else:
        print('No hs', end=' ')
        return ''


def socket_handler(socket, id, game, game_messages):
    waiting_frame = encode_frame(b'2waiting')
    try:
        while game.turn == 0:
            socket.sendall(waiting_frame)
            sleep(1)
        while True:
            turn = game.turn
            frame1 = encode_frame(b'1' + game.to_bytes(id))
            socket.sendall(frame1)
            frame2 = encode_frame(b'2' + game_messages[-1].to_bytes())
            socket.sendall(frame2)

            if game.current_player_index != id:
                while game.ongoing and game.turn == turn:
                    sleep(1)  # apparently this makes the thread yield
                continue

            socket.setblocking(False)
            try:  # ugly way of clearing buffer
                socket.recv(1024)
            except OSError:
                pass
                # this error is system depended so it may need to be changed
                # [Errno 35] Resource temporarily unavailable
            socket.setblocking(True)

            socket.settimeout(60*10)
            message = decode_frame(socket.recv(1024))
            print(id, message, game_messages[-1])
            if message == b'BB':
                print('start')
                GAME.start()
            if len(message) != 2:
                frame = encode_frame(b'2' + b'Invalid bet')
                socket.sendall(frame)
                print('Message too long')
                continue

            command, arg = unpack('BB', message)
            try:
                GAME.next_player(command, arg)
            except GameError as message:
                game_messages.append(message)
                frame = encode_frame(b'2' + message.to_bytes())
                socket.sendall(frame)
    except IndexError:
        print(
            'Index error, this can mean somebody rejoined the game and'
            'this is a thread that should terminate. THREAD: ', id
        )
        return
    except BrokenPipeError:
        print('Pipe broke. THREAD: ', id)
        return


if __name__ == '__main__':
    GAME = Game()
    THREADS = []
    NAMES = []
    GAME_MESSAGES = [GameError('Waiting for game to start.')]
    try:
        while len(THREADS) < 20:
            TCPsocket.listen(bufferSize)
            new_conn, address = TCPsocket.accept()
            print(f'New connection {len(THREADS)}: {address}', end=" ")
            socket_name = new_socket_handler(new_conn)
            if socket_name in NAMES:
                print('Rejoin')
                index = socket_name.index(socket_name)
                th = threading.Thread(
                    target=socket_handler,
                    args=(new_conn, index, GAME, GAME_MESSAGES)
                )
                th.start()
                THREADS[index].join()
                THREADS[index] = th
                print(THREADS)
            elif len(socket_name) > 0:
                print('Success')
                GAME.join(socket_name)
                NAMES.append(socket_name)
                th = threading.Thread(
                    target=socket_handler,
                    args=(new_conn, len(GAME.players)-1, GAME, GAME_MESSAGES)
                )
                th.start()
                THREADS.append(th)
                if len(THREADS) == 4:
                    GAME_MESSAGES.append(GameError('Game started!'))
                    GAME.start()
            else:
                print('Fail')
        while GAME.ongoing:
            sleep(0)  # yield
        sleep(10)

    except Exception as e:
        print(e)
    finally:
        for thread in THREADS:
            thread.join()
        TCPsocket.close()
# TODO: remove dead threads from THREADS
