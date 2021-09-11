# Minesweeper Solver

Solution for the [Simple Interactive Interpreter](https://www.codewars.com/kata/52ffcfa4aff455b3c2000750) Codewars kata.

### Problem Detail

Create an interpreter which takes inputs described below and produces outputs, storing state in between each input.

The grammar for the interpreter language in EBNF syntax:
```
function        ::= fn-keyword fn-name { identifier } fn-operator expression
fn-name         ::= identifier
fn-operator     ::= '=>'
fn-keyword      ::= 'fn'

expression      ::= factor | expression operator expression
factor          ::= number | identifier | assignment | '(' expression ')' | function-call
assignment      ::= identifier '=' expression
function-call   ::= fn-name { expression }

operator        ::= '+' | '-' | '*' | '/' | '%'

identifier      ::= letter | '_' { identifier-char }
identifier-char ::= '_' | letter | digit

number          ::= { digit } [ '.' digit { digit } ]

letter          ::= 'a' | 'b' | ... | 'y' | 'z' | 'A' | 'B' | ... | 'Y' | 'Z'
digit           ::= '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
```

### Implementation

The implementation is based on [Dijkstra's shunting-yard algorithm](https://en.wikipedia.org/wiki/Shunting-yard_algorithm).