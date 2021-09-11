from itertools import product, groupby


def get_keys():
    products = product((0, 1), repeat=5)
    keys = {}

    for prod in products:
        key = tuple(map(len, [list(g) for k, g in groupby(prod) if k]))
        try:
            keys[key].add(prod)
        except KeyError:
            keys[key] = {prod}

    return keys


KEYS = get_keys()


class Nonogram:
    def __init__(self, clues):
        self.c_clues = clues[0]
        self.r_clues = clues[1]

        self.board = [tuple(0 for _ in range(5)) for _ in range(5)]
        self.curr_row = -1

    def solve(self):
        old_row = self.curr_row
        self.curr_row += 1

        if self.curr_row == 5:
            self.curr_row -= 1
            return self.check_valid()

        row_clue = self.r_clues[self.curr_row]
        row_num = self.curr_row

        for row in KEYS[row_clue]:
            self.board[row_num] = row

            if self.solve():
                return tuple(self.board)

        self.curr_row = old_row

    def check_valid(self):
        cols = [tuple(self.board[y][x] for y in range(5)) for x in range(5)]

        for i, col in enumerate(cols):
            clue = self.c_clues[i]
            if col not in KEYS[clue]:
                return False
        return True
