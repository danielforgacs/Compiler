"""
expression:     term ((ADD | SUB) term) *
term:           factor ((MULT | DIV) factor) *

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

pop_next_token = lambda x: (x[0], x[1:])


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


class AST:
    pass


class BinOp(AST):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class UnaryOp(AST):
    def __init__(self, operator, expression):
        self.token = operator
        self.expression = expression


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NodeVisitor:
    def visit(self, node):
        visitor = getattr(self, node.__class__.__name__)
        return visitor(node)

    def Num(self, node):
        return node.value

    def BinOp(self, node):
        if node.operator == ADD_TOKEN:
            return self.visit(node.left) + self.visit(node.right)
        elif node.operator == SUB_TOKEN:
            return self.visit(node.left) - self.visit(node.right)
        elif node.operator == MULT_TOKEN:
            return self.visit(node.left) * self.visit(node.right)
        elif node.operator == DIV_TOKEN:
            return self.visit(node.left) / self.visit(node.right)
        else:
            raise Exception(f'[ERROR] Unexpected BinOp node: {node.operator}')


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
            raise Exception(f'[ERROR] Bad char: {char}')

        index += 1

    tokens += (EOF_TOKEN,)

    return tokens


def factor(tokens):
    """
    factor: (PLUS | MINUS) factor | INTEGER | PAREN_L expression PAREN_R
    """
    token, tokens = pop_next_token(tokens)
    if token.type_ == INTEGER:
        node = Num(token)

    elif token == PAREN_L_TOKEN:
        token, tokens, node = expression(tokens)
        paren_r, tokens = pop_next_token(tokens)

    # elif token in [SUB_TOKEN, ADD_TOKEN, MULT_TOKEN, DIV_TOKEN]:


    else:
        raise Exception(f'[ERROR] Unecpeted token: {token}')

    return token, tokens, node


def term(tokens):
    token_left, tokens, node = factor(tokens)
    result = token_left.value

    while tokens[0] in (MULT_TOKEN, DIV_TOKEN):
        operator, tokens = pop_next_token(tokens)
        token_right, tokens, node_r = factor(tokens)
        node = BinOp(node, operator, node_r)

    return Token(INTEGER, result), tokens, node


def expression(tokens):
    token_left, tokens, node = term(tokens)
    result = token_left.value

    while tokens[0] in (ADD_TOKEN, SUB_TOKEN):
        operator, tokens = pop_next_token(tokens)
        token_right, tokens, node_r = term(tokens)
        node = BinOp(node, operator, node_r)

    return Token(INTEGER, result), tokens, node


def run(source):
    tokens = tokenise(source)
    _, _, node = expression(tokens)

    return NodeVisitor().visit(node)


if __name__ == '__main__':
    code = '2+3'
    code = '-1'
    # code = '#'
    print(
        run(code),
        eval(code)
    )
