import pygame
from struct import pack
import socket
from threading import Thread

from grapics import *

server_ip = '85.229.19.61'  #'localhost'
server_port = 63834
name = b'Isak'

GAME = None
MESSAGE = None
def fetch_thread(socket):
    global GAME, MESSAGE
    while 1:
        received_byes = socket.recvfrom(1024)[0]
        #print(received_byes)
        if received_byes[0] == b'1'[0]:
            GAME = received_byes[1:]
        elif received_byes[0] == b'2'[0]:
            MESSAGE = received_byes[1:]
        else:
            print('Could not read server msg :( this is bad')
            print(received_byes)
            continue


def graphics_init():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN, SCREEN))
    font = pygame.font.SysFont('monotypecorsiva', 25)
    return font, screen


def draw_new_frame(screen, font, game, message):
    draw_frame(screen, font, game, message)
    screen.blit(screen, (0, 0))
    pygame.display.update()


if __name__ == '__main__':
    client_socket = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM
    )
    client_socket.settimeout(1000)
    serverAddressPort = (server_ip, server_port)
    client_socket.sendto(name, serverAddressPort)
    thread = Thread(target=fetch_thread, args=(client_socket,))
    thread.start()

    font, screen = graphics_init()
    send = False
    command = None
    arg = None
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                send = True
                if y < 425:
                    command = FLIP
                    if y < 95:
                        arg = 1
                    elif y < 145:
                        arg = 2
                    elif y < 195:
                        arg = 3
                    elif y < 245:
                        arg = 4
                    elif y < 295:
                        arg = 5
                    else:
                        arg = 0
                else:
                    command = PLACE
                    if x < 175:
                        arg = 0
                    elif x < 225:
                        arg = 1
                    elif x < 275:
                        arg = 2
                    else:
                        arg = 3

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    command = 2
                    arg = 1
                elif event.key == pygame.K_b:
                    command = 1
                    i = "a"
                    while not i.isdigit():
                        i = input('Bet: ')
                    arg = int(i)
                elif event.key == pygame.K_s:
                    command = 66
                    arg = 66

        if command is not None and arg is not None:
            client_socket.sendto(pack('BB', command, arg), serverAddressPort)
            command = None
            arg = None

        #command = int(input('command: '))
        #arg = int(input('arg: '))
        draw_new_frame(screen, font, GAME, MESSAGE)


