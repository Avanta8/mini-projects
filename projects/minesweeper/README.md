# Minesweeper Solver

Solution for the [Mine Sweeper](https://www.codewars.com/kata/57ff9d3b8f7dda23130015fa/) Codewars kata.

### Problem Detail

Given a puzzle, such as:
```
1 x x 1 0 0 0
2 3 3 1 0 1 1
1 x 1 0 0 1 x
1 1 1 0 0 1 1
0 1 1 1 0 0 0
0 1 x 1 0 0 0
0 1 1 1 0 1 1
0 0 0 0 0 1 x
0 0 0 0 0 1 1
```
and a function, `open`, which can be called to open reveal unknown squares, return the solved grid as a string.

If a square containing a mine is opened, the game is lost automatically.

If the grid is unsolvable, then return `'?'`

### Implementation

A possible brute force solution is to generate every permutation of possible solutions, and mark the squares which are the same in all of them. Then repeat this every iteration until either the grid is solved, or nothing more can be reduced.

However this solution uses linear algebra, and is much faster than the brute force approach.