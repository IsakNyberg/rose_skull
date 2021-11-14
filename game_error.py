from struct import pack


class GameError(Exception):

    def to_bytes(self):
        return pack(f'{len(str(self))}s', str(self).encode('utf-8'))
