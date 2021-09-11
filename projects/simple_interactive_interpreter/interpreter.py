import re
from itertools import takewhile, dropwhile
from operator import add, sub, mod, mul, truediv


OPERS = {'+': add, '-': sub, '*': mul, '/': truediv, '%': mod}


def type_token(token):
    if token.isdigit() or re.match(r'\d*\.\d+', token):
        return 'num'
    elif token == 'fn':
        return 'fn'
    elif token.isalpha():
        return 'vf'
    elif token == '(':
        return 'ob'
    elif token == ')':
        return 'cb'
    elif token in '+-*/%':
        return 'op'
    elif token == '=':
        return 'asv'
    elif token == '=>':
        return 'asf'
    else:
        raise ValueError('Invalid token:', token)


def match_brack(code, ind):
    depth = 0
    wanted_depth = -1
    for i, c in enumerate(code):
        if c[0] == '(':
            depth += 1
            if i == ind:
                wanted_depth = depth
        elif c[0] == ')':
            if depth == wanted_depth:
                return i
            depth -= 1


def tokenize(expression):
    if expression == "":
        return []

    regex = re.compile("\s*(=>|[-+*\/\%=\(\)]|[A-Za-z_][A-Za-z0-9_]*|[0-9]*\.?[0-9]+)\s*")
    tokens = regex.findall(expression)
    tokens = [(s, type_token(s)) for s in tokens if not s.isspace()]
    return tokens


def oper(op, n1, n2):
    try:
        n1 = int(n1)
    except ValueError:
        n1 = float(n1)
    try:
        n2 = int(n2)
    except ValueError:
        n2 = float(n2)

    val = OPERS[op](n1, n2)
    if isinstance(val, float) and val.is_integer():
        return (str(int(val)), 'num')
    else:
        return (str(val), 'num')


def is_more_powerful(op1, op2):
    return op1 in ['+', '-'] and op2 in ['*', '/', '%']


class Interpreter:
    def __init__(self):
        self.vars = {}
        self.funcs = {}

    def input(self, expression):
        self.latest_expression = expression
        tokens = tokenize(expression)
        if not tokens:
            return ''
        ans = self.parse(tokens)
        return float(ans[0][0]) if ans != 'def_func' else ''

    def parse(self, tokens):
        first_val, first_type = tokens[0]
        if first_type in ('num', 'ob'):
            return self.calculate(tokens[:])
        elif first_type == 'vf':
            if len(tokens) > 1:
                snd_val, snd_type = tokens[1]
                if snd_type == 'asv':
                    return self.def_var(tokens[:])
                elif first_val in self.vars:
                    val = self.vars[first_val]
                    return self.parse(val + tokens[1:])
                elif first_val in self.funcs:
                    return self.do_func(tokens[:])
            else:
                if first_val in self.vars:
                    return self.vars[first_val]
                elif first_val in self.funcs:
                    return self.do_func(tokens[:])
        elif first_type == 'fn':
            return self.def_func(tokens[:])

    def calculate(self, tokens):
        first_val, first_type = tokens[0]
        if first_type == 'ob':
            match = match_brack(tokens, 0)
            val = self.parse(tokens[1:match])
            return self.parse(val + tokens[match + 1 :])
        elif first_type == 'num':
            if len(tokens) > 1:
                snd_val, snd_type = tokens[1]
                if snd_type == 'op':
                    if len(tokens) > 3:
                        if tokens[2][1] == 'ob' or is_more_powerful(
                            snd_val, tokens[3][0]
                        ):
                            val = self.parse(tokens[2:])
                            return self.parse(tokens[:2] + val)
                    return self.parse(
                        [oper(snd_val, first_val, tokens[2][0])] + tokens[3:]
                    )
            else:
                return tokens

    def do_func(self, tokens):
        val, i = self.parse_func(tokens)
        return self.parse(tokenize(val) + tokens[i:])

    def parse_func(self, tokens):
        func_args, func_code = self.funcs[tokens[0][0]]
        arg_count = len(func_args)

        args = []
        i = 1
        for _ in range(arg_count):
            nxt_val, nxt_type = tokens[i]
            if nxt_type == 'num':
                args.append(nxt_val)
            elif nxt_type == 'vf':
                if nxt_val in self.vars:
                    args.append(nxt_val)
                elif nxt_val in self.funcs:
                    val, end = self.parse_func(tokens[i:])
                    args.append('( ' + val + ' )')
                    i += end - 1
                else:
                    raise Exception('Var / func is not defined:', nxt_val)
            else:
                raise Exception('Invalid argument for function:', tokens[i])
            i += 1

        for old, new in zip(func_args, args):
            func_code = func_code.replace(old, new)
        return func_code, i

    def def_func(self, tokens):
        func_name = tokens[1][0]
        assert (
            func_name not in self.vars
        ), 'Cannot declare function that is already a variable'
        args = tuple(t[0] for t in takewhile(lambda x: x[1] != 'asf', tokens[2:]))
        assert len(args) == len(set(args)), 'Function arguments contain duplicate values'
        source_code = ' '.join(
            [t[0] for t in dropwhile(lambda x: x[1] != 'asf', tokens)][1:]
        )
        for val, type_ in tokenize(source_code):
            if type_ == 'vf':
                assert val in args, 'Function expression contains invalid variable names'
        self.funcs[func_name] = (args, source_code)
        return 'def_func'

    def def_var(self, tokens):
        var_name = tokens[0][0]
        assert (
            var_name not in self.funcs
        ), 'Cannot declare variable that is already a function'
        val = self.parse(tokens[2:])
        self.vars[var_name] = val
        return val
