import pygame
from struct import unpack
import socket

SCREEN = 500
HIDE = True

ROSE_COLOUR = '#5c0618'
SKULL_COLOUR = '#35686e'
HIDDEN_COLOUR = '#d3d3d3'
BACKGROUND = '#292929'

PLACE = 0
BET = 1
PASS = 2
FLIP = 3
SKULL = 0
ROSE = 1
HIDDEN = 2

CARD_SIZE = 50

TEXT = '#ffffff'
TEXT_RED = '#9c3648'  #'#ff9351'
TEXT_GREY = '#393939'


def draw_card(screen, colour, position):
    pygame.draw.circle(screen, '#1a1a1a', position, 25)
    pygame.draw.circle(screen, colour, position, 23)


def draw_player(screen, font, index, current_index, player_bytes):
    (
        name,
        score,
        has_passed,
        hand_len,
        board_len
    ) = unpack('4sB?BB', player_bytes)

    x = 50
    y = 20 + CARD_SIZE * (index + 1)
    text_colour = TEXT_RED if index == current_index else TEXT
    text_colour = TEXT_GREY if has_passed else text_colour
    display_name = name.decode('utf-8') + ' ' + '*' * score
    text = font.render(display_name, True, text_colour)
    screen.blit(text, (10, y - 10))

    for card in range(hand_len)[::-1]:
        x += CARD_SIZE
        draw_card(screen, HIDDEN_COLOUR, (x, y))

    x = 300
    for card in range(board_len):
        x += CARD_SIZE * 0.6
        draw_card(screen, HIDDEN_COLOUR, (x, y))


def draw_flipped(screen, font, bet, flipped_byte):
    cards = unpack('B' * len(flipped_byte), flipped_byte)

    if not bet:
        return

    text = font.render(f'Current Bet: {bet}', True, TEXT)
    screen.blit(text, (150, SCREEN - 250))

    #text = font.render('Flipped:', True, TEXT)
    #screen.blit(text, (10, SCREEN - 200))
    x = 100
    for card in cards:
        x += CARD_SIZE
        colour = ROSE_COLOUR if card else SKULL_COLOUR
        draw_card(screen, colour, (x, SCREEN - 200))


def draw_own_player(screen, font, own_turn, player_bytes):
    (
        name,
        score,
        has_passed,
        hand_len,
        board_len
    ) = unpack('4sB?BB', player_bytes[0:8])
    hand = unpack(f'{hand_len}B', player_bytes[8:8 + hand_len])
    board = unpack(f'{board_len}B', player_bytes[8 + hand_len:])

    x = 150
    text = font.render('Board:', True, TEXT)
    screen.blit(text, (10, SCREEN - (100 + CARD_SIZE // 4)))
    for card in board[::-1]:
        colour = ROSE_COLOUR if card == ROSE else SKULL_COLOUR
        draw_card(screen, colour, (x, SCREEN - 100))
        x += int(CARD_SIZE * 0.6)

    text = font.render('Hand:', True, TEXT)
    screen.blit(text, (10, SCREEN - (50 + CARD_SIZE // 4)))
    x = 150
    for card in hand:
        colour = ROSE_COLOUR if card == ROSE else SKULL_COLOUR
        draw_card(screen, colour, (x, SCREEN - 50))
        x += CARD_SIZE

    text_colour = TEXT_RED if own_turn else TEXT
    text_colour = TEXT_GREY if has_passed else text_colour
    display_name = name.decode('utf-8') + ' ' + '*' * score
    text = font.render(display_name, True, text_colour)
    screen.blit(text, (200, SCREEN - 160))


def draw_message(screen, font, ongoing,  message_bytes):
    ongoing_text = 'Game has started' if ongoing else 'Game is not ongoing'
    text = font.render(ongoing_text, True, TEXT)
    screen.blit(text, (10, 2))

    if message_bytes:
        message = unpack(f'{len(message_bytes)}s', message_bytes)[0]
        display_message = message.decode('utf-8')
        text = font.render(display_message, True, TEXT)
        screen.blit(text, (10, 30))


def draw_frame(screen, font, byte_stream, message=None):
    if byte_stream is None:
        return
    screen.fill(BACKGROUND)

    start = 0
    end = 5
    game_info_bytes = byte_stream[start:end]
    (
        ongoing,
        current_player_index,
        current_bet,
        num_players,
        num_flipped
    ) = unpack('?BBBB', game_info_bytes)

    for player_index in range(num_players):
        start = end
        end += 8
        draw_player(
            screen,
            font,
            player_index,
            current_player_index,
            byte_stream[start:end])

    start = end
    end += num_flipped
    draw_flipped(screen, font, current_bet, byte_stream[start:end])

    own_turn = num_players == current_player_index
    draw_own_player(screen, font, own_turn, byte_stream[end:])

    draw_message(screen, font, ongoing, message)
