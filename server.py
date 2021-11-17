import time
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
        time.sleep(5)
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
    waiting_frame = encode_frame(b'waiting' + str(id).encode('utf-8'))
    try:
        while not game.ongoing:
            socket.sendall(waiting_frame)
            time.sleep(5)
        while game.ongoing:
            if game.current_player_index != id:
                frame1 = encode_frame(b'1' + game.to_bytes(index))
                socket.sendall(frame1)
                frame2 = encode_frame(b'2' + game_messages[-1].to_bytes())
                socket.sendall(frame2)
                time.sleep(1)  # apparently this makes the thread yield
                continue

            socket.settimeout(30)
            message = socket.recv(1024)
            if message == b'BB':
                print('start')
                GAME.start()

            command, arg = unpack('BB', MESSAGE)
            try:
                GAME.next_player(command, arg)
            except GameError as message:
                game_messages.append(message)
                frame = encode_frame(b'2' + message.to_bytes())
                socket.sendall(frame)
    except BrokenPipeError:
        print('Pipe broke: ', id)
        return


if __name__ == '__main__':
    GAME = Game()
    THREADS = []
    GAME_MESSAGES = [GameError('Waiting.')]

    try:
        while len(THREADS) < 20:
            TCPsocket.listen(bufferSize)
            new_conn, address = TCPsocket.accept()
            print(f'New connection {len(THREADS)}: {address}', end=" ")
            socket_name = new_socket_handler(new_conn)
            if len(socket_name) > 0:
                print('Success')
                GAME.join(socket_name)
                th = threading.Thread(
                    target=socket_handler,
                    args=(new_conn, len(GAME.players)-1, GAME, GAME_MESSAGES)
                )
                th.start()
                THREADS.append(th)
            else:
                print('Fail')
        while GAME.ongoing:
            sleep(0)  # yield

    except Exception as e:
        print(e)
    finally:
        TCPsocket.close()
        for thread in THREADS:
            thread.join()
# TODO: remove dead threads from THREADS
