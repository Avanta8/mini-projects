# Loopover Solver

Solution for the [Loopover](https://www.codewars.com/kata/5c1d796370fee68b1e000611) Codewars kata.

### Problem Detail

Given a loopover puzzle as a 2D array, and the final (solved) position, calculate the moves required to solve the puzzle.

```python
[16, 17,  5]        [ 1,  2,  3]
[ 1,  8, 11]        [ 4,  5,  6]
[ 4,  2,  6]   ->   [ 7,  8,  9]
[ 9, 14,  7]        [10, 11, 12]
[18, 10, 12]        [13, 14, 15]
[13,  3, 15]        [16, 17, 18]
```

Loopover puzzles can be played on this site: https://loopover.xyz


### Implementation

The grid is solved row by row from top to bottom, with each item of a row being put in the right place by moving the respective column down, inserting the square, then moving the column back up.

The final row is solved differently as parity and edge cases can occur with some certain sized grids.