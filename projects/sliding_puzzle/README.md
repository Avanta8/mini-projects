# Sliding Puzzle Solver

Solution for the [Sliding Puzzle Solver](https://www.codewars.com/kata/5a20eeccee1aae3cbc000090) Codewars kata.

### Problem Detail

Given a sliding puzzle such as, for example:

![img](https://i.imgur.com/AUVWFOn.png)

Output a list of all the numbers that should be moved in the correct order to solve the puzzle.

For example, given the puzzle:
```python
simple_example = [
    [ 1, 2, 3, 4],
    [ 5, 0, 6, 8],
    [ 9,10, 7,11],
    [13,14,15,12]
]

# TRANSITION SEQUENCE:
[ 1, 2, 3, 4]    [ 1, 2, 3, 4]    [ 1, 2, 3, 4]    [ 1, 2, 3, 4]    [ 1, 2, 3, 4]
[ 5, 0, 6, 8]    [ 5, 6, 0, 8]    [ 5, 6, 7, 8]    [ 5, 6, 7, 8]    [ 5, 6, 7, 8]
[ 9,10, 7,11] -> [ 9,10, 7,11] -> [ 9,10, 0,11] -> [ 9,10,11, 0] -> [ 9,10,11,12]
[13,14,15,12]    [13,14,15,12]    [13,14,15,12]    [13,14,15,12]    [13,14,15, 0]

slide_puzzle(simple_example) == [6,7,11,12]
```