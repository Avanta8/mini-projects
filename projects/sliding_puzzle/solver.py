from heapq import heappop, heappush


def slide_puzzle(puzzle):
    solver = SlidingSolver(puzzle)
    try:
        solver.solve()
        return solver.moves
    except Exception:
        return None


class SlidingSolver:
    def __init__(self, grid):
        size = len(grid)

        self.neighbours = ((-1, 0), (1, 0), (0, -1), (0, 1))

        self.grid = grid
        self.size = size
        # {number: the correct position in the final solution}
        self.correct_pos_of = {
            (i + 1) % (size * size): (i % size, i // size) for i in range(size * size)
        }
        # {position: the correct number that should end up there}
        self.correct_num_at = {
            (i % size, i // size): (i + 1) % (size * size) for i in range(size * size)
        }

        # {number: current location (position) of that number}
        self.location_of = {}
        for y, row in enumerate(grid):
            for x, sq in enumerate(row):
                self.location_of[sq] = (x, y)

        # Squares that are in the correct position and shouldn't be disturbed
        self.fixed = set()
        self.current_border = 0

        self.moves = []

    def solve(self):
        """The upmost and leftmost lines (borders) are solved.
        Then the next inner borders are solved. This is repeated
        until only a 2x2 grid remains unsolved. Then finally,
        the 2x2 grid is solved. `self.current_border` is the
        current border to be solved."""

        while self.current_border < self.size - 2:
            self.solve_border()
            self.current_border += 1

        size = self.size
        for num in ((size - 1) * size - 1, (size - 1) * size, size * size - 1):
            self.move_num_to_position(num, self.correct_pos_of[num])
            self.fixed.add(num)

    def solve_border(self):
        """The border of the grid is solved by solving the
        upmost and leftmost lines until there are just two
        squares on the end of each line left unsolved. Then,
        the last two squares are solved. The start of the lines
        are solved just by moving the squares to the correct positions.
        However, solving the last two squares of each line are a
        bit more tricky. The 2nd to last square is moved to the corner
        square (where the last square should end up going) and the last square
        is lined up right behind it. Then, they are just inserted as normal
        (with the 2nd last square going first)."""

        current_border = self.current_border
        correct_num_at = self.correct_num_at
        location_of = self.location_of
        fixed = self.fixed
        move_num_to_position = self.move_num_to_position

        row_positions = [(i, current_border) for i in range(self.size)]
        column_positions = [(current_border, i) for i in range(self.size)]

        # Solves each line of the border until there are just two unsolved squares
        # left on each line
        for position in row_positions[:-2] + column_positions[:-2]:
            num = correct_num_at[position]
            move_num_to_position(num, position)

            fixed.add(num)

        # Now solve the last two pieces of the row and column
        for i, positions in enumerate((row_positions, column_positions)):

            # The position of the square that lines up before the corner
            before_last_pos = (
                positions[-1][0] if i == 0 else positions[-1][0] + 1,
                positions[-1][1] if i == 1 else positions[-1][1] + 1,
            )

            # num of the last position
            last = correct_num_at[positions[-1]]
            last_x, last_y = location_of[last]

            # num of the 2nd last position
            l2st = correct_num_at[positions[-2]]

            # Makes sure the corner piece is at least 2 places away from
            # the corner so the 2nd to last piece doesn't get stuck
            # when being manipulated
            if i == 0 and last_y - current_border < 2:
                move_num_to_position(last, (last_x, current_border + 2))
            elif i == 1 and last_x - current_border < 2:
                move_num_to_position(last, (current_border + 2, last_y))

            # move 2nd last square to corner
            move_num_to_position(l2st, positions[-1], fixed_out={last})
            # line last square up behind 2nd last
            move_num_to_position(last, before_last_pos, keep_fixed={l2st})
            # move 2nd last square to correct position
            move_num_to_position(l2st, positions[-2], keep_fixed={last})
            fixed.add(l2st)
            # move last square to correct position
            move_num_to_position(last, positions[-1])
            fixed.add(last)

    def find_path(self, start, end):
        """A* pathfinding. Uses Manhatten distance for the heuristic.
        Returns the positions that the path took from `start` to `end`"""

        grid = self.grid
        neighbours = self.neighbours
        fixed = self.fixed

        squares = {}
        for y, row in enumerate(grid):
            for x, sq in enumerate(row):
                squares[(x, y)] = sq not in fixed

        end_x, end_y = end

        inf = float("inf")
        open_ = [(0, 0, start)]  # [F cost, count, node]
        dists = {start: 0}
        paths = {}
        count = 0

        while open_:
            current = heappop(open_)[2]
            cx, cy = current
            if current == end:
                break

            current_dist = dists[current]
            for nx, ny in neighbours:
                new_pos = (cx + nx, cy + ny)
                new_dist = current_dist + 1

                if squares.get(new_pos, False) and new_dist < dists.get(new_pos, inf):
                    count -= 1
                    heappush(
                        open_,
                        (
                            current_dist
                            + abs(end_x - new_pos[0])
                            + abs(end_y - new_pos[1]),
                            count,
                            new_pos,
                        ),
                    )
                    dists[new_pos] = new_dist
                    paths[new_pos] = current

        if current != end:
            raise Exception("Invalid grid")

        moves = []
        pos = end
        while pos in paths:
            moves.append(pos)
            pos = paths[pos]
        return moves[::-1]

    def make_moves(self, start, end):
        """Moves the item at the `start` postition to the `end` postition
        by swapping adjacent squares. One of the adjacent squares being
        swapped should always be a 0 (empty square)."""
        grid = self.grid
        current_moves = self.moves
        location_of = self.location_of

        moves = self.find_path(start, end)  # `moves` are actually postitions
        for mx, my in moves:
            ex, ey = location_of[0]
            num = grid[my][mx]

            # References to the location of the squares are updated
            location_of[0], location_of[num] = location_of[num], location_of[0]

            current_moves.append(num)

            # The squares are now swapped on the grid
            grid[ey][ex], grid[my][mx] = grid[my][mx], grid[ey][ex]

    def move_num_to_position(
        self, num, position, keep_fixed=set(), fixed_out=set(), fixed_in=set()
    ):
        """The square containing the number `num` is moved to `position`.
        Fixed squares are not disturbed.
        `num` is moved by repetedly moving the zero square to the target `position`
        then moving it back to current position of `num`. This moves `num`
        closer to `position` by one square every repetition. `num` is not
        disturbed when the 0 square is moved back to `position`
        (Otherwise it may just repetedly just move forwards then backwards).
        `keep_fixed` are numbers that should be kept fixed during the moving sequences,
        but shouldn't remain in `self.fixed`. `fixed_in` and `fixed_out` are numbers
        that are fixed only when the 0 square is moving towards the target postition,
        or towards the target number repectively."""
        grid = self.grid
        make_moves = self.make_moves
        fixed = self.fixed
        location_of = self.location_of

        fixed |= keep_fixed
        pos_x, pos_y = position
        while grid[pos_y][pos_x] != num:

            # 0 in moving back into the target position
            fixed |= fixed_in
            fixed -= fixed_out
            fixed.add(num)
            make_moves(location_of[0], position)

            # 0 in moving out to the target number
            fixed |= fixed_out
            fixed -= fixed_in
            fixed.remove(num)
            make_moves(position, location_of[num])
        fixed -= fixed_out
        fixed -= keep_fixed

    def print_grid(self):
        """Prints the grid with each row on a new line."""
        print()
        for row in self.grid:
            print(row)
