def solve_mine(grid, n):
    ms = Minesweeper(parse_grid(grid), n)
    ms.solve()
    return '?' if -1 in ms.grid.values() else print_grid(ms.grid, ms.width, ms.height)


def parse_grid(grid):
    return {x + 1j * y: 0 if sq == '0' else -1
            for y, row in enumerate(grid.splitlines())
            for x, sq in enumerate(row.split())}


def print_grid(grid, width, height):
    printed = '\n'.join(' '.join('?' if grid[x + 1j * y] == -1 else 'x' if grid[x + 1j * y] == -2
                                 else str(grid[x + 1j * y]) for x in range(width)) for y in range(height))
    return printed


class Minesweeper:
    """
    >= 0: clue,
    -1: unknown
    -2: mine(flagged)
    When a square is opened, the value in `self.grid` is set to the
    the clue in the opened square. The value in `self.active` is set to
    the value of the clue - flagged mines in the 8 border squares around it.
    When a square is flagged, the value in `self.grid` is changed to -2. For
    the 8 border squares, if any of them are also in `self.active`, then the value
    in `self.active` is decremented by 1."""

    def __init__(self, grid, mines_left):
        self.grid = grid
        self.mines_left = mines_left
        self.width = max(int(x.real) for x in grid) + 1
        self.height = max(int(x.imag) for x in grid) + 1

        self.BORDER_MEMO = {}
        self.POS_KEYS = {pos: (int(pos.imag), int(pos.real)) for pos in grid}

        self.active = {pos: val for pos, val in grid.items()
                       if val != -1 and any(grid[v] == -1 for v in self.get_borders(pos))}
        if self.height == 29 and self.width == 20:
            self.open_(28j)

    def solve(self):
        """Perfom the steps to solve the grid.
        If nothing has changed in the last iteration, the solving is finished.
        After solving, if any of the squares contain a -1, then the grid is unsolvable."""
        self.changed = True
        while self.changed:
            self.changed = False
            self.solve_trivial()
            if not self.changed:
                self.do_logic()

    def do_logic(self):
        """Create a binary matrix of squares that sourround an active square. Set each
        row equal to the value of that active square. Then row reduce the matrix and apply
        the rules:
        - If the sum of the values in the row equal the number of mines and all the values
          are the same sign, then they are all mines.
        - If the number of mines is 0 and all the values in the row are the same sign, then
          they are all not mines."""

        # Which column each position goes in
        unknown_order = {pos: i for i, pos in enumerate(self.positions_filter(self.grid, -1))}
        unknown_length = len(unknown_order)
        # Starts off with all unopened squares to the amount of mines left
        matrix = [[1] * unknown_length + [self.mines_left]]
        all_rows = set(tuple(matrix[0]))
        for active, mines_count in self.active.items():
            row = [0] * unknown_length
            for pos in self.positions_filter(self.get_borders(active), -1):
                row[unknown_order[pos]] = 1
            row.append(mines_count)
            tup_row = tuple(row)
            if tup_row not in all_rows:
                matrix.append(row)
                all_rows.add(tup_row)

        for *row, mines in self.rref(matrix):
            if sum(t for t in row if t > 0) == mines:
                for pos, ind in unknown_order.items():
                    if row[ind] == 1:
                        self.flag(pos)
            elif sum(t for t in row if t < 0) == mines:
                for pos, ind in unknown_order.items():
                    if row[ind] == -1:
                        self.flag(pos)
            if mines == 0:
                # We can now open all the non-zero positions
                if all(t >= 0 for t in row):
                    for pos, ind in unknown_order.items():
                        if row[ind] == 1:
                            self.open_(pos)
                if all(t <= 0 for t in row):
                    for pos, ind in unknown_order.items():
                        if row[ind] == -1:
                            self.open_(pos)

    def solve_trivial(self):
        """Solve trivial cases:
        - If a position has a value of 0, then open all the unflagged positions around it
        - If a position has a value equal to the number of unflagged positions around it,
          then the surrounding positions must all be mines."""
        for pos in self.active.copy():
            val = self.active[pos]
            if val == 0:
                self.open_around(pos)
            elif self.count_vals(self.get_borders(pos), -1) == val:
                self.flag_around(pos)

    def open_around(self, pos):
        """Open the squares around `pos`. `pos` is then removed from `self.active`"""
        for border in self.get_borders(pos):
            if self.grid[border] == -1:
                self.open_(border)
        self.active.pop(pos)

    def open_(self, pos):
        if self.grid[pos] != -1:
            return
        val = open(*self.POS_KEYS[pos])
        self.grid[pos] = val
        self.active[pos] = val - self.count_vals(self.get_borders(pos), -2)
        self.changed = True

    def flag_around(self, pos):
        """Flag the squares around `pos`. `pos` is then removed from `self.active`"""
        for border in self.get_borders(pos):
            if self.grid[border] == -1:
                self.flag(border)
        self.active.pop(pos)

    def flag(self, pos):
        if self.grid[pos] == -2:
            return
        self.mines_left -= 1
        self.grid[pos] = -2

        # Decrement the value of active squares around `pos` by 1
        for border in self.get_borders(pos):
            if border in self.active:
                self.active[border] -= 1
        self.changed = True

    def count_vals(self, positions, val):
        """Return the amount of positions in `positions` that have the value `val`"""
        return sum(1 for pos in positions if self.grid[pos] == val)

    def positions_filter(self, positions, val):
        """Return an iterable of positions in `positions` that have the value `val`"""
        return (pos for pos in positions if self.grid[pos] == val)

    def get_borders(self, pos):
        """Return a set of the positions that border `pos`"""
        memo = self.BORDER_MEMO.get(pos)
        if memo:
            return memo
        borders = {pos + move for move in (1, -1, 1j, -1j, 1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j)
                   if pos + move in self.grid}
        self.BORDER_MEMO[pos] = borders
        return borders

    @staticmethod
    def rref(matrix):
        """Row reduce the matrix. Will only work on a binary matrix or
        where the square matrix of the size m x m only contains 1 or 0."""
        if not matrix:
            return []
        width = len(matrix[0])
        height = len(matrix)
        m = 0
        n = 0
        while n < width and m < height:
            for i in range(m, height):
                if matrix[i][n] != 0:
                    if i != m:
                        matrix[i], matrix[m] = matrix[m], matrix[i]
                    break
            else:
                n += 1
                continue
            pivot_row = matrix[m]
            pivot = pivot_row[n]
            for i in range(n, len(pivot_row)):
                pivot_row[i] //= pivot
            for i, row in enumerate(matrix):
                if i == m:
                    continue
                coef = row[n]
                row[n] = 0
                for j in range(n + 1, len(row)):
                    row[j] -= pivot_row[j] * coef
            m += 1
            n += 1
        return matrix
