from game import Game
from game_error import GameError
from random import randint


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    GAME = Game()
    for i in range(4):
        GAME.join('BOT' + str(i))
    GAME.start()

    while GAME.ongoing:
        print(GAME.to_bytes(2))
        command = int(input('command: '))
        arg = int(input('arg: '))
        #command = randint(0,3)
        #arg = randint(0,4)
        try:
            GAME.next_player(command, arg)
        except GameError as e:
            if not GAME.ongoing:
                print(e)
