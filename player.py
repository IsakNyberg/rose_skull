import random
from game_error import GameError
from struct import pack

SKULL = 0
ROSE = 1
HIDDEN = 2
EMPTY_CARD = 3

WIN_SCORE = 2


class Player:
    def __init__(self, name, spectator=False):
        self.name = f"{name.ljust(4)}"[:4]
        self.hand = [ROSE, ROSE, ROSE, SKULL]
        random.shuffle(self.hand)
        self.board = []
        self.score = 0
        self.hidden_card = []
        self.has_passed = False

        if spectator:
            self.hand = []
            self.has_passed = True

    def __str__(self):
        return f'{self.name} S: {self.score} ' \
               f'H: {self.hand} B: {self.board} ' \
               f'Pass: {self.has_passed}'

    @property
    def alive(self):
        return bool(len(self.hand) + len(self.board))

    @property
    def has_won(self):
        return self.score >= WIN_SCORE

    def give_point(self):
        self.score += 1
        return self.has_won

    def place(self, index):
        if len(self.hand) == 0:
            raise GameError(f'Your hand is empty you must bet.')
        try:
            self.board.insert(0, self.hand.pop(index))
        except IndexError:
            raise GameError(f'No card in that position.')

    def reset(self):
        for _ in range(len(self.board)):
            self.hand.append(self.board.pop())
        for _ in range(len(self.hidden_card)):
            self.hand.append(self.hidden_card.pop())
        random.shuffle(self.hand)

        self.has_passed = len(self.hand) == 0  # if player has no cards remove

    def flip(self):
        try:
            card = self.board.pop(0)
            self.hidden_card.append(card)
            return card
        except IndexError:
            raise GameError(f'{self.name} has no on board.')

    def penalty(self):
        if len(self.board) != 0:
            raise GameError(f'BAD ERROR, used penalty before reset')
        if len(self.hand) == 0:
            raise GameError(f'BAD ERROR, penalty on eliminated player')

        random.shuffle(self.hand)
        self.hand.pop()
        random.shuffle(self.hand)

        if len(self.hand) == 0:
            self.has_passed = True

    def to_bytes(self, hidden):
        # 8 bytes for other player
        # 8 + (0 to 4) for self player
        res = bytearray()
        res += pack(
            '4sB?BB',
            self.name[:4].encode('utf-8'),
            self.score,
            self.has_passed,
            len(self.hand),
            len(self.board)
        )  # 8 bytes

        if not hidden:
            res += pack(
                f'{len(self.hand)}B',
                *self.hand
            )
            res += pack(
                f'{len(self.board)}B',
                *self.board
            )
        return res
