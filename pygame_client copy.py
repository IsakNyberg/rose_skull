
import time
import pygame
from game import Game
from game_error import GameError
from player import SKULL, ROSE, HIDDEN
from random import randint

SCREEN = 500
HIDE = True

ROSE_COLOUR = '#5c0618'
SKULL_COLOUR = '#35686e'
BACKGROUND = '#292929'


def draw_player(screen, font, index, highlight=False):
    line_dist = 50
    x = line_dist
    y = line_dist * (index + 1)

    text_colour = '#efa351' if highlight else '#ffffff'

    text = font.render(GAME.players[index].name, True, text_colour)
    screen.blit(text, (line_dist//4, y-(line_dist//4)))

    for card in GAME.players[index].hand:
        colour = ROSE_COLOUR if card == ROSE else SKULL_COLOUR
        x += line_dist
        pygame.draw.circle(screen, '#1a1a1a', (x, y), 25)
        pygame.draw.circle(screen, colour, (x, y), 23)

    x += line_dist * 2
    for card in GAME.players[index].board:
        colour = ROSE_COLOUR if card == ROSE else SKULL_COLOUR
        x += line_dist
        pygame.draw.circle(screen, '#1a1a1a', (x, y), 25)
        pygame.draw.circle(screen, colour, (x, y), 23)


def draw_hud(surface, font, player_bytes):
    pass


def draw_frame(surface, font, byte_stream):
    surface.fill(BACKGROUND)
    player_byte_size = 14
    pointer = 0

    ongoing = bool(byte_stream[0])
    current_player = byte_stream[1]
    current_bet = byte_stream[2]
    draw_hud(surface, font, byte_stream[3:3+player_byte_size])

    for i in range(byte_stream[3+player_byte_size]):
        start = 3+player_byte_size + player_byte_size*i
        end = 3+player_byte_size + player_byte_size*(i+1)
        draw_player(surface, font, byte_stream[start:end])

    for i in range(byte_stream[3 + player_byte_size]):



if __name__ == '__main__':
    GAME = Game()
    PLAYER_INDEX = 2
    for i in range(4):
        GAME.join('ABCDE ' + str(i))
    GAME.start()
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN, SCREEN))
    font = pygame.font.SysFont('monotypecorsiva', 25)

    while GAME.ongoing:
        draw_frame(screen, font, GAME)
        screen.blit(screen, (0, 0))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        command = int(input('command: '))
        arg = int(input('arg: '))
        #command = randint(0, 3)
        #arg = randint(0, 4)

        try:
            print(GAME)
            GAME.next_player(command, arg)
        except GameError as e:
            print(e)


        #time.sleep(20)






