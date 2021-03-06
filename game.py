from player import Player, SKULL, ROSE
from game_error import GameError
from struct import pack
import random

PLACE = 0
BET = 1
PASS = 2
FLIP = 3
NONE = -1  # select new player without doing anything


class Game:
    def __init__(self):
        self.ongoing = False
        self.players = []
        self._current_player = 0

        self.current_bet = 0
        self.flipped = 0
        self.last_better = -1
        self.flipped_cards = []
        self.intermission = 0

        self.turn = 0
        self.action_count = 0

    def __str__(self):
        res = f'Ongoing: {self.ongoing}\n'
        for player in self.players:
            res += str(player)
            if player is self.current_player:
                res += '  <-'
            res += '\n'
        if self.current_bet:
            res += f'Current bet: {self.current_bet}\n'
            res += f'flipped cards: {self.flipped_cards}\n'
        return res

    @property
    def current_player(self):
        return self.players[self._current_player]

    @property
    def current_player_index(self):
        return self._current_player

    def check_win(self):
        for player in self.players:
            if player.has_won:
                return True
        return False

    def not_passed_players(self):
        amount = 0
        for player in self.players:
            amount += not player.has_passed
        return amount

    def alive_players(self):
        amount = 0
        for player in self.players:
            amount += player.alive
        return amount

    def number_placed_cards(self):
        amount = 0
        for player in self.players:
            amount += len(player.board)
        return amount

    def round_reset(self):
        for player in self.players:
            player.reset()
        self.current_bet = 0
        self.flipped = 0
        self.flipped_cards = []
        self.last_better = -1

    def join(self, name):
        # adds player, if GAME is ongoing player is added as a spectator
        self.players.append(Player(name, spectator=self.ongoing))

    def start(self):
        self.ongoing = True
        self._current_player = 0
        self.current_bet = 0
        self.flipped = 0
        self.last_better = -1
        self.flipped_cards = []
        self.intermission = 0
        self.turn = 1
        raise GameError(
            f'Game started current player: {self.current_player.name}'
        )

    def bet(self, amount):
        if amount <= self.current_bet:
            raise GameError(f'Bet higher than {self.current_bet}')
        if amount > self.number_placed_cards():
            raise GameError(f'Bet lower than {self.number_placed_cards()+1}')
        self.current_bet = amount

        if amount == self.number_placed_cards():
            for player in self.players:
                if player is not self.current_player:
                    player.has_passed = True

    def flip(self, index):
        index = (self._current_player + index) % len(self.players)

        if self.flipped == 0 and self._current_player != index:
            raise GameError('First flipped card must be own card.')
        try:
            card = self.players[index].flip()
        except IndexError:
            raise GameError(f'Player {self.players[index].name} has no cards')

        self.flipped += 1
        self.flipped_cards.append(card)

        if card == SKULL:
            self.intermission = -1
            raise GameError(f'Skull flipped by {self.current_player.name}')
        else:
            if self.flipped == self.current_bet:
                self.current_player.give_point()  # give point & checks win
                self.intermission = 1
                raise GameError(f'Point scored by {self.current_player.name}')

    def next_player(self, command, command_argument):
        if command not in (PLACE, BET, PASS, FLIP):
            raise GameError('BAD ERROR, invalid command')
        if not self.ongoing:
            raise GameError('Game has not started yet')

        self.turn += 1
        if self.intermission:
            self.round_reset()
            if self.intermission == -1:
                self.current_player.penalty()
            self.intermission = 0
            command = NONE

        if self.alive_players() == 1 or self.check_win():
            command = NONE

        if command == PLACE:
            if self.current_bet > 0:
                raise GameError('Cannot place new card if a bet has begun.')
            self.current_player.place(command_argument)

        elif command == BET:
            if len(self.current_player.board) == 0:
                raise GameError('Cannot bet before you have placed a card.')
            self.bet(command_argument)

        elif command == PASS:
            if self.current_bet == 0:
                raise GameError('Cannot pass before a bet has begun.')
            if self.not_passed_players() == 1:
                raise GameError('Cannot pass after a bet has finished.')
            if self._current_player == self.last_better:
                raise GameError('Cannot pass if you have placed highest bet')
            self.current_player.has_passed = True

        elif command == FLIP:
            if self.current_bet == 0:
                raise GameError('Place a bet before flipping')
            if self.not_passed_players() != 1:
                raise GameError('Cannot flip unless a bet has finished.')
            self.flip(command_argument)

        while True:
            self._current_player += 1
            self._current_player %= len(self.players)
            if not self.current_player.has_passed:
                break
        self.action_count += 1
        if self.alive_players() == 1 and command == NONE:
            raise GameError(f'Last player standing {self.current_player.name}')
        elif self.check_win() and command == NONE:
            raise GameError(f'Game won by {self.current_player.name}')

    def make_random_move(self):
        action_count = self.action_count
        command, arg = 0, 0
        while self.action_count == action_count:
            try:
                command = random.randint(0, 3)
                if command == 0:
                    arg = random.randint(0, len(self.players))
                elif command == 1:
                    arg = random.randint(0, self.number_placed_cards())
                elif command == 2:
                    arg = 0
                else:
                    arg = random.randint(0, len(self.players))
                self.next_player(command, arg)
            except GameError:
                pass
        return command, arg

    def to_bytes(self, caller_index):
        # 5 bytes of GAME info
        # 8 * (number of players -1) bytes of players
        # 1 * (number of flipped cards)
        # 8 + (0 to 4) bytes os own player
        # rest is own player
        res = bytearray()
        res += pack(
            '?BBBB',  # docs.python.org/3/library/struct.html#format-characters
            self.ongoing,
            (self._current_player - (caller_index + 1)) % len(self.players),
            self.current_bet,
            len(self.players) - 1,
            len(self.flipped_cards),
        )
        for player in self.players[caller_index+1:]+self.players[:caller_index]:
            res += player.to_bytes(True)  # hidden

        for card in self.flipped_cards:
            res += pack('B', card)

        res += self.players[caller_index].to_bytes(False)  # not hidden
        return res
