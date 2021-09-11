"""
1 - If the target square is in the target row, move the column down and the resulting row right.
    Then move the column back
2 - If the target square is in the target column, move the row of the target square right
3 - Move the target column down the number of steps in the y direction so that the target
    square is on the same row as the square it should end up in. Then move the row left the
    amount of steps difference in the x direction so that it matches the correct square,
    then move that column back.
"""


class Loopover:
    def __init__(self, grid, end, width=None, height=None):
        self.grid = grid
        self.end = end
        self.height = height if height else len(grid)
        self.width = width if width else len(grid[0])

        self.parse_positions()

        self.moves_made = []

    def solve(self):
        for y in range(self.height - 1):
            for x in range(self.width):
                self.solve_position((x, y))
        self.solve_final()
        return self.moves_made if self.grid == self.end else None

    def solve_position(self, correct_pos):
        current_num = self.correct_num_at[correct_pos]
        correct_x, correct_y = correct_pos

        cx, cy = self.current_position_of[current_num]
        if cy == correct_y:
            self.move('C', cx, 1)
            self.move('R', cy + 1, 1)
            self.move('C', cx, -1)
            cx, cy = self.current_position_of[current_num]

        if cx == correct_x:
            self.move('R', cy, 1)
            cx += 1

        self.move('C', correct_x, cy - correct_y)
        self.move('R', cy, -(cx - correct_x))
        self.move('C', correct_x, correct_y - cy)

    def solve_final(self):
        correct_y = self.height - 1

        for correct_x in range(self.width - 2):
            current_num = self.end[correct_y][correct_x]
            cx, cy = self.current_position_of[current_num]
            dx = cx - correct_x

            if cx == correct_x:
                continue

            move = 2 if abs(dx) == 1 else 1

            self.move('C', cx, -1)
            self.move('R', correct_y - 1, -dx)
            self.move('C', correct_x, 1)
            self.move('R', correct_y, -move)
            self.move('C', correct_x, -1)
            self.move('R', correct_y, move)
            self.move('R', correct_y - 1, dx)
            self.move('C', cx, 1)

        last_num = self.end[-1][-1]
        if self.current_position_of[last_num][0] != self.width - 1:
            self.solve_parity()

    def solve_parity(self):
        self.parity1() if self.height % 2 == 0 else self.parity2()

    def parity1(self):
        for _ in range(self.height // 2):
            self.move('C', self.width - 1, -1)
            self.move('R', self.height - 1, 1)
            self.move('C', self.width - 1, -1)
            self.move('R', self.height - 1, -1)
        self.move('C', self.width - 1, -1)

    def parity2(self):
        self.move('C', self.width - 1, -1)
        self.move('R', self.height - 1, 1)
        self.move('C', self.width - 1, 1)
        self.move('R', self.height - 1, -1)

        for _ in range(self.width // 2):
            self.move('R', self.height - 1, -1)
            self.move('C', self.width - 1, -1)
            self.move('R', self.height - 1, -1)
            self.move('C', self.width - 1, 1)
        self.move('R', self.height - 1, -1)

    def move(self, line, number, times):
        if line == 'R':
            for px in range(self.width):
                num = self.grid[number][px]
                self.current_position_of[num] = ((px + times) % self.width, number)
            self.grid[number] = self.rotate_line(self.grid[number], times % self.width)
            move_made = f"{'R' if times > 0 else 'L'}{number}"
        elif line == 'C':
            for py in range(self.height):
                num = self.grid[py][number]
                self.current_position_of[num] = (number, (py + times) % self.height)
            column = [self.grid[y][number] for y in range(self.height)]
            rotated = self.rotate_line(column, times % self.height)
            for y in range(self.height):
                self.grid[y][number] = rotated[y]
            move_made = f"{'D' if times > 0 else 'U'}{number}"

        self.moves_made.extend([move_made] * abs(times))

    def rotate_line(self, line, times):
        return line[-times:] + line[:-times]

    def parse_positions(self):
        self.correct_num_at = {}
        self.current_position_of = {}
        for y, row in enumerate(self.grid):
            for x, sq in enumerate(row):
                pos = (x, y)
                self.correct_num_at[pos] = self.end[y][x]
                self.current_position_of[sq] = pos

    def print_grid(self):
        print()
        for row in self.grid:
            print(row)


if __name__ == '__main__':
    start = [[16, 17, 5], [1, 8, 11], [4, 2, 6], [9, 14, 7], [18, 10, 12], [13, 3, 15]]
    end = [[i * 3 + j + 1 for j in range(3)] for i in range(6)]
    for a in start, end:
        for row in a:
            print(row)
    print(Loopover(start, end).solve())


    start = [
        ['W', 'C', 'M', 'D', 'J', '0'],
        ['O', 'R', 'F', 'B', 'A', '1'],
        ['K', 'N', 'G', 'L', 'Y', '2'],
        ['P', 'H', 'V', 'S', 'E', '3'],
        ['T', 'X', 'Q', 'U', 'I', '4'],
        ['Z', '5', '6', '7', '8', '9'],
    ]
    end = [
        ['A', 'B', 'C', 'D', 'E', 'F'],
        ['G', 'H', 'I', 'J', 'K', 'L'],
        ['M', 'N', 'O', 'P', 'Q', 'R'],
        ['S', 'T', 'U', 'V', 'W', 'X'],
        ['Y', 'Z', '0', '1', '2', '3'],
        ['4', '5', '6', '7', '8', '9'],
    ]
    print(Loopover(start, end).solve())
