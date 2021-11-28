from time import sleep
from struct import unpack
from web_socket import *
import socket
import threading
import sys

from game import Game
from game_error import GameError


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


def socket_handler(socket, id, game, game_messages, hard_reset):
    while not hard_reset[0]:
        try:
            turn = game.turn
            frame1 = encode_frame(b'1' + game.to_bytes(id))
            socket.sendall(frame1)
            frame2 = encode_frame(b'2' + game_messages[-1].to_bytes())
            socket.sendall(frame2)

            sleep(0.5)  # apparently this makes the thread yield
            if game.current_player_index != id:
                while game.turn == turn and game.turn != 0:
                    sleep(0.5)  # apparently this makes the thread yield
                continue

            socket.setblocking(False)
            try:  # ugly way of clearing buffer
                socket.recv(1024)
            except OSError:
                pass
                # this error is system depended so it may need to be changed
                # [Errno 35] Resource temporarily unavailable
            socket.setblocking(True)

            socket.settimeout(45)
            message = decode_frame(socket.recv(1024))
            print(id, message, game_messages[-1])
            if len(message) != 2:
                frame = encode_frame(b'2' + b'Invalid command')
                socket.sendall(frame)
                print(f'{id} Message too long')

            elif message == b'dd':  # message == 100 100
                print('start')
                game.start()
            elif message == b'ee':  # message == 101 101
                hard_reset[0] = True
                print('hard reset')
            else:
                command, arg = unpack('BB', message)
                game.next_player(command, arg)

        except GameError as message:
            game_messages.append(message)
            continue

        except OSError:
            if game.turn == 0:
                continue
            elif game.current_player_index == id:
                game_messages.append(
                    GameError(
                        f'Random move played by {game.current_player.name}'
                    )
                )
                command, arg = game.make_random_move()
                print(f'random move {id} cmd{command} arg{arg}')
            else:
                print(f'socket {id} timeout when it was not allowed to.')
                return

        except IndexError:
            print(
                'Index error, this can mean somebody rejoined the game and'
                'this is a thread that should terminate. THREAD: ', id
            )
            return
        except (BrokenPipeError, ConnectionResetError):
            print('Pipe broke. THREAD: ', id)
            return


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: python3 server.py local_ip port')
        sys.exit()
    localIP = sys.argv[1]
    localPort = int(sys.argv[2])
    bufferSize = 1024

    TCPsocket = None
    while True:
        try:
            TCPsocket = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM
            )
            TCPsocket.bind((localIP, localPort))
            break
        except OSError as e:
            print(e)
            print('Trying again in 5 seconds')
            sleep(5)
    print("Server up and listening")

    try:
        while True:
            HARD_RESET = [False]
            GAME = Game()
            THREADS = []
            NAMES = []
            GAME_MESSAGES = [GameError('Waiting for game to start.')]
            print('New game instance')
            while True:
                TCPsocket.listen(bufferSize)
                new_conn, address = TCPsocket.accept()
                if not HARD_RESET[0]:
                    print('clearing all threads')
                    for thread in THREADS:
                        thread.join()
                    break
                print(f'New connection {len(THREADS)}: {address}', end=" ")
                socket_name = new_socket_handler(new_conn)
                if socket_name in NAMES:
                    print('Rejoin')
                    index = socket_name.index(socket_name)
                    th = threading.Thread(
                        target=socket_handler,
                        args=(new_conn, index, GAME, GAME_MESSAGES, HARD_RESET)
                    )
                    th.start()
                    THREADS[index].join()
                    THREADS[index] = th
                elif len(socket_name) > 0:
                    print('Success')
                    GAME.join(socket_name)
                    NAMES.append(socket_name)
                    th = threading.Thread(
                        target=socket_handler,
                        args=(
                            new_conn,
                            len(GAME.players)-1,
                            GAME,
                            GAME_MESSAGES,
                            HARD_RESET
                        )
                    )
                    th.start()
                    THREADS.append(th)
                else:
                    print('Fail')

            for thread in THREADS:
                thread.join()

    except Exception as e:
        print(e)
    finally:
        for thread in THREADS:
            thread.join()
        TCPsocket.close()
