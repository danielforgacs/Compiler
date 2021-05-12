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


class AST:
    pass


class BinOp(AST):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


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


def factor(result, tokens):
    token, tokens = pop_next_token(tokens)
    if token.type_ == INTEGER:
        node = Num(token)
        pass
    elif token == PAREN_L_TOKEN:
        token, tokens, node = expression(result, tokens)
        paren_r, tokens = pop_next_token(tokens)

    return token, tokens, node


def term(result, tokens):
    token_left, tokens, node = factor(result, tokens)
    result = token_left.value

    while tokens[0] in (MULT_TOKEN, DIV_TOKEN):
        operator, tokens = pop_next_token(tokens)
        token_right, tokens, node_r = factor(result, tokens)

        if operator == MULT_TOKEN:
            result *= token_right.value
        elif operator == DIV_TOKEN:
            result /= token_right.value

        node = BinOp(node, operator, node_r)
    return Token(INTEGER, result), tokens, node


def expression(result, tokens):
    token_left, tokens, node = term(result, tokens)
    result = token_left.value

    while tokens[0] in (ADD_TOKEN, SUB_TOKEN):
        operator, tokens = pop_next_token(tokens)
        token_right, tokens, node_r = term(result, tokens)

        if operator == ADD_TOKEN:
            result += token_right.value
        elif operator == SUB_TOKEN:
            result -= token_right.value

        node = BinOp(node, operator, node_r)
    return Token(INTEGER, result), tokens, node


def run(source):
    tokens = tokenise(source)
    token, _, node = expression(0, tokens)

    print(NodeVisitor().visit(node))

    # return token.value
    return NodeVisitor().visit(node)


if __name__ == '__main__':
    code = '2*3*4*5'
    # code = '2+3'
    print(run(code), eval(code))
