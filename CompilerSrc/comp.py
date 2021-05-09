"""
expression:     term ((ADD | SUB) term) *
term:           factor ((MULT | DIV) factor) *
factor:         INTEGER | PAREN_L expression PAREN_R

ADD, SUB:           +, -
MULT, DIV:          *, /
PAREN_L, PAREN_R:   (, )
INTEGER:            0, 1, 2, 3, 4, 5, 6, 7, 8, 9
"""

EOF = 'EOF'

INTEGER = 'INTEGER'

ADD = 'ADD'
SUB = 'SUB'
MULT = 'MULT'
DIV = 'DIV'
PAREN_L, PAREN_R = 'PAREN_L', 'PAREN_R'


is_space = lambda x: x == ' '
is_digit = lambda x: x in '0123456789'
is_add = lambda x: x == '+'
is_sub = lambda x: x == '-'
is_mult = lambda x: x == '*'
is_div = lambda x: x == '/'
is_paren_l = lambda x: x == '('
is_paren_r = lambda x: x == ')'


class Token:
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value
    def __eq__(self, other):
        return (self.type_ == other.type_) and (self.value == other.value)
    def __repr__(self):
        return '<Token:{}:{}>'.format(self.type_, self.value)


EOF_TOKEN = Token(EOF, EOF)
ADD_TOKEN = Token(ADD, ADD)
SUB_TOKEN = Token(SUB, SUB)
MULT_TOKEN = Token(MULT, MULT)
DIV_TOKEN = Token(DIV, DIV)
PAREN_L_TOKEN = Token(PAREN_L, PAREN_L)
PAREN_R_TOKEN = Token(PAREN_R, PAREN_R)


def find_int_token(src, index):
    result = ''
    char = src[index]
    while is_digit(char):
        result += char
        index += 1
        if index == len(src):
            break
        char = src[index]
    token = Token(INTEGER, int(result))
    index -= 1
    return token, index


def tokenise(source):
    index = 0
    tokens = ()

    while index < len(source):
        char = source[index]

        if is_space(char):
            pass
        elif is_digit(char):
            token, index = find_int_token(source, index)
            tokens += (token,)
        elif is_add(char):
            tokens += (ADD_TOKEN,)
        elif is_sub(char):
            tokens += (SUB_TOKEN,)
        elif is_mult(char):
            tokens += (MULT_TOKEN,)
        elif is_div(char):
            tokens += (DIV_TOKEN,)
        elif is_paren_l(char):
            tokens += (PAREN_L_TOKEN,)
        elif is_paren_r(char):
            tokens += (PAREN_R_TOKEN,)
        else:
            raise Exception('[ERROR] Bad token', char)

        index += 1

    tokens += (EOF_TOKEN,)

    return tokens


pop_next_token = lambda x: (x[0], x[1:])


def factor(tokens):
    token, tokens = pop_next_token(tokens)
    return token, tokens


def term(result, tokens):
    token_left, tokens = factor(tokens)
    assert token_left.type_ == INTEGER
    result = token_left.value

    while tokens[0] in (MULT_TOKEN, DIV_TOKEN):
        operator, tokens = pop_next_token(tokens)
        assert operator in (MULT_TOKEN, DIV_TOKEN)
        token_right, tokens = factor(tokens)
        assert token_right.type_ == INTEGER

        if operator == MULT_TOKEN:
            result *= token_right.value
        elif operator == DIV_TOKEN:
            result /= token_right.value

    return Token(INTEGER, result), tokens


def expression(result, tokens):
    token_left, tokens = term(result, tokens)
    assert token_left.type_ == INTEGER
    result = token_left.value

    while tokens[0] in (ADD_TOKEN, SUB_TOKEN):
        operator, tokens = pop_next_token(tokens)
        assert operator in (ADD_TOKEN, SUB_TOKEN)
        token_right, tokens = term(result, tokens)
        assert token_right.type_ == INTEGER

        if operator == ADD_TOKEN:
            result += token_right.value
        elif operator == SUB_TOKEN:
            result -= token_right.value

    return result


def run(source):
    tokens = tokenise(source)
    result = expression(0, tokens)

    return result


if __name__ == '__main__':
    # code = '2*3*4*5'
    code = '2+3'
    print(run(code), eval(code))
