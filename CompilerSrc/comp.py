EOF = 'EOF'

INTEGER = '0123456789'

ADD = '+'
SUB = '-'
MULT = '*'
DIV = '/'


is_digit = lambda x: x in INTEGER
is_add = lambda x: x == ADD
is_sub = lambda x: x == SUB
is_mult = lambda x: x == MULT
is_div = lambda x: x == DIV


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
    return token, index


def tokenise(source):
    index = 0
    tokens = ()

    while index < len(source):
        char = source[index]

        if is_digit(char):
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

        index += 1

    tokens += (EOF_TOKEN,)

    return tokens


def expression(source, index):
    tokens = tokenise(source)
    result = 0

    while tokens[0] != EOF:
        pass

    return result
