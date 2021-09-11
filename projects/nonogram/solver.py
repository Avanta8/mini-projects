from itertools import repeat, groupby, count, chain


def solve(*args):
    return tuple(map(tuple, Nonogram(*args).solve()))


class Memo:
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if args in self.cache:
            return self.cache[args]
        else:
            ans = self.func(*args)
            self.cache[args] = ans
            return ans


class Nonogram:

    __slots__ = [
        'W',
        'H',
        'no_of_lines',
        'col_clues',
        'row_clues',
        'grid',
        'to_linesolve',
        'grid_changed',
        'solved_lines',
        'prev_states',
    ]

    def __init__(self, clues, width, height):
        self.W, self.H = width, height
        self.no_of_lines = width + height
        self.col_clues, self.row_clues = clues

        self.grid = [[-1 for _ in range(width)] for _ in range(height)]

        self.to_linesolve = sorted(
            list(zip(repeat('C'), count(), self.col_clues))
            + list(zip(repeat('R'), count(), self.row_clues)),
            key=lambda x: sum(x[2]),
            reverse=True,
        )

        self.solved_lines = set()  # set of all the solved lines for lookup

        self.prev_states = []  # list of states in case it needs to guess and backtrack

    def solve(self):
        """Generates the furthest left, and furthest right possible permutation of a row
        and takes the intersection of the points that are the same (line-solving).
        If no more points can be deduced, then it takes a random guess and repeats.
        If the grid becomes invalid, it just backtracks to the last guess."""
        line_solve = self.line_solve
        while len(self.solved_lines) < self.no_of_lines:
            self.grid_changed = False

            try:
                line_solve()
            except InvalidGridError:
                # Resets the grid back to the old state.
                old_grid, old_guess, guess_pos, old_solved_lines = self.prev_states.pop()
                self.grid = [l[:] for l in old_grid]
                self.grid[guess_pos[0]][guess_pos[1]] = old_guess ^ 1  # Swaps the guess
                self.solved_lines = old_solved_lines.copy()
                continue

            if not self.grid_changed and len(self.solved_lines) < self.no_of_lines:
                # Guesses if no extra blocks/gaps have been deduced
                self.guess()
        return self.grid

    def line_solve(self):
        """This method should line solve all the clues in self.line_solve
        using the furthest left, and furthest right to compare which blocks are valid/invalid.
        It may miss a small amount though (limitations of alg), but 'should' be fast(ish)"""
        solved_lines = self.solved_lines
        get_line = self.get_line
        linesolve_helper = self.linesolve_helper
        change_grid = self.change_grid

        for vert, pos, clue in self.to_linesolve:

            if (vert, pos, clue) in solved_lines:
                # If the line is already solved
                continue

            line = get_line(vert, pos)  # The current line so far

            solved = linesolve_helper(line, clue)

            if solved is True:
                # The line must be solved
                solved_lines.add((vert, pos, clue))
            elif solved:
                # Changes the grid if the line changed
                change_grid(solved, vert, pos)
                self.grid_changed = True

    def guess(self):
        """Guesses a random choice if nothing can be deduced from linesolving"""
        target = self.find_guess_target()
        guess = 1

        # Incase the guess is wrong and needs to backtrack
        self.prev_states.append(
            ([l[:] for l in self.grid], guess, target, self.solved_lines.copy())
        )
        self.grid[target[0]][target[1]] = guess

    def find_guess_target(self):
        """Finds the first unknown square sorted by the length of the sum of the clue,
        and therefore should be more likely to lead to a guess with more impact"""
        for vert, pos, clue in self.to_linesolve:
            if (vert, pos, clue) not in self.solved_lines:
                if vert == 'R':
                    for i, b in enumerate(self.grid[pos]):
                        if b == -1:
                            return (pos, i)
                elif vert == 'C':
                    for i, r in enumerate(self.grid):
                        if r[pos] == -1:
                            return i, pos

    def get_line(self, vert, pos):
        """Gets the specified line"""
        if vert == 'R':
            return tuple(self.grid[pos])
        elif vert == 'C':
            return tuple(row[pos] for row in self.grid)

    def change_grid(self, line, vert, pos):
        """Changes the line in the grid"""
        if vert == 'R':
            self.grid[pos] = list(line)
        elif vert == 'C':
            for i, val in enumerate(line):
                self.grid[i][pos] = val

    @staticmethod
    @Memo
    def linesolve_helper(line, clue):
        """This method first calculates the leftmost and
        rightmost possible permutations of the line.
        Then it find the intersection where there is a overlap of the same colour."""
        length = len(line)

        leftmost = Nonogram.get_leftmost(clue, length, line)
        rightmost = Nonogram.get_leftmost(clue[::-1], length, line[::-1])[::-1]

        solved = Nonogram.find_intersection(leftmost, rightmost, line, length)

        return solved if solved != line else not -1 in line

    @staticmethod
    @Memo
    def get_leftmost(clue, length, filled_line):
        """This method should get the leftmost valid arrangement of all the clues."""

        # List of all blocks in order of clues given.
        # block is [start_pos, end_pos, length]
        blocks = tuple([0, c, c] for c in clue)

        for i, block in enumerate(blocks):
            # Moves the blocks up until they are all in valid positions,
            # but not necessarily covering all the blocked spots.
            if i != 0:
                # Teleports the block to the end of the previous block
                diff = blocks[i - 1][1] - block[0] + 1
                block[0] += diff
                block[1] += diff

            while 0 in filled_line[block[0] : block[1]]:
                # If the block is in an invalid position, then it moves it along 1 square
                block[0] += 1
                block[1] += 1

        while True:
            # Moves the blocks until all the blocked spots are covered.

            line = [0] * length
            # Fills in the line if a block is there.
            for block in blocks:
                line[block[0] : block[1]] = [1] * block[2]

            changed = False
            for i, c in enumerate(filled_line):
                # If a block should be covering a filled square but isn't
                if c == 1 and line[i] == 0:
                    changed = True
                    for block in reversed(blocks):
                        # Finds the first block to the left of the square,
                        # and teleports the right end of the block to the square
                        if block[1] <= i:
                            diff = i - block[1] + 1
                            block[0] += diff
                            block[1] += diff
                            break
                    else:
                        # If no block was found, then the grid must be invalid.
                        raise InvalidGridError('Invalid grid')

            if not changed:
                break

            for i, block in enumerate(blocks):
                # Moves the blocks up until they are not covering any zeros,
                # but not necessarily covering all the blocked spots,
                while 0 in filled_line[block[0] : block[1]]:
                    # If the block is in an invalid spot
                    block[0] += 1
                    block[1] += 1

                if i != 0:
                    # If any block is in an invalid position compared to the previous block
                    if block[0] <= blocks[i - 1][1]:
                        # Teleports the block to 1 square past the end of the previous block
                        diff = blocks[i - 1][1] - block[0] + 1
                        block[0] += diff
                        block[1] += diff

        return tuple(line)

    @staticmethod
    def find_intersection(left, right, line, length):
        """Groups the same blocks together then takes the intersection."""
        leftmost = list(
            chain.from_iterable(
                [i] * len(list(g[1])) for i, g in enumerate(groupby((0,) + left))
            )
        )[1:]
        rightmost = list(
            chain.from_iterable(
                [i] * len(list(g[1])) for i, g in enumerate(groupby((0,) + right))
            )
        )[1:]

        solved = tuple(
            line[i]
            if line[i] != -1
            else -1
            if leftmost[i] != rightmost[i]
            else leftmost[i] % 2
            for i in range(length)
        )

        return solved


class InvalidGridError(Exception):
    """Custom Exception for an invalid grid."""


if __name__ == '__main__':
    clues = (
        (
            (1, 2),
            (8,),
            (1, 2, 2),
            (3, 2, 1, 1),
            (2, 2, 6),
            (3,),
            (2, 1),
            (1, 1, 1),
            (1, 1, 2),
            (2, 2),
            (1, 1, 1),
            (3, 5),
            (1, 1, 3),
            (2, 2),
            (3,),
        ),
        (
            (1,),
            (5,),
            (1, 2, 1),
            (4, 2, 1),
            (3, 2, 2, 2),
            (1, 1, 1, 1, 3, 1),
            (1, 3, 1, 2, 1),
            (1, 1, 1, 1),
            (1, 2),
            (1, 1, 1, 1, 1),
            (2, 3, 2),
            (1, 3),
            (1, 1),
            (1, 1),
            (2, 2),
        ),
    )
    args = clues, 15, 15

    ans = solve(*args)

    sol = (
        (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        (0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0),
        (1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0),
        (1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1),
        (0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1),
        (0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1),
        (0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0),
        (0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0),
        (0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0),
        (0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0),
        (0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0),
        (0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0),
        (0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0),
        (0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0),
    )

    print('ans:')
    [print(r) for r in ans]
    print('is it correct?', ans == sol)
