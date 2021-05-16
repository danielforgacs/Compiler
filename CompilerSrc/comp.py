SPACE = ' '
DIGITS = '0123456789'
ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
PLUS, MINUS = '+', '-'
MULT, DIV = '*', '/'
PAREN_L, PAREN_R = '(', ')'
EQUAL = '='
COLON = ':'
SEMICOLON = ';'
DOT = '.'

ASSIGN = COLON + EQUAL
ID = 'ID'
INTEGER = 'INTEGER'
BEGIN = 'BEGIN'
END = 'END'
EOF = 'EOF'


is_digit = lambda char: char in DIGITS
is_alpha = lambda char: char in ALPHA
pop_next_token = lambda tokens: (tokens[0], tokens[1:])





class Token:
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value

    def __eq__(self, other):
        return (self.type_ == other.type_) and (self.value == other.value)

    def __repr__(self):
        return '<Token:{}:{}>'.format(self.type_, self.value)




EOF_TOKEN = Token(EOF, EOF)
PLUS_TOKEN = Token(PLUS, PLUS)
MINUS_TOKEN = Token(MINUS, MINUS)
MULT_TOKEN = Token(MULT, MULT)
DIV_TOKEN = Token(DIV, DIV)
PAREN_L_TOKEN = Token(PAREN_L, PAREN_L)
PAREN_R_TOKEN = Token(PAREN_R, PAREN_R)

BEGIN_TOKEN = Token(BEGIN, BEGIN)
END_TOKEN = Token(END, END)
DOT_TOKEN = Token(DOT, DOT)
ASSIGN_TOKEN = Token(ASSIGN, ASSIGN)





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





def find_alpha_token(src, index):
    result = ''
    char = src[index]

    while is_alpha(char):
        result += char
        index += 1

        if index == len(src):
            break

        char = src[index]

    if result == BEGIN:
        token = BEGIN_TOKEN
    elif result == END:
        token = END_TOKEN
    else:
        token = Token(ID, result)

    index -= 1

    return token, index





def tokenise(source):
    index = 0
    tokens = ()

    while index < len(source):
        char = source[index]
        nextchar = None

        if index + 1 < len(source):
            nextchar = source[index+1]

        if char == SPACE:
            pass
        elif is_digit(char):
            token, index = find_int_token(source, index)
            tokens += (token,)
        elif char == PLUS:
            tokens += (PLUS_TOKEN,)
        elif char == MINUS:
            tokens += (MINUS_TOKEN,)
        elif char == MULT:
            tokens += (MULT_TOKEN,)
        elif char == DIV:
            tokens += (DIV_TOKEN,)
        elif char == PAREN_L:
            tokens += (PAREN_L_TOKEN,)
        elif char == PAREN_R:
            tokens += (PAREN_R_TOKEN,)
        elif is_alpha(char):
            token, index = find_alpha_token(source, index)
            tokens += (token,)
        elif char == DOT:
            tokens += (DOT_TOKEN,)
        elif char + nextchar == ASSIGN:
            index += 1
            tokens += (ASSIGN_TOKEN,)
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
        tokens, node = expression(tokens)
        paren_r, tokens = pop_next_token(tokens)

        if paren_r != PAREN_R_TOKEN:
            raise Exception(f'[ERROR] Expected token: {PAREN_R_TOKEN}')

    elif token in [MINUS_TOKEN, PLUS_TOKEN]:
        tokens, node = factor(tokens)
        node = UnaryOp(token, node)

    else:
        raise Exception(f'[ERROR] Unecpeted token: {token}')

    return tokens, node


def term(tokens):
    tokens, node = factor(tokens)

    while tokens[0] in (MULT_TOKEN, DIV_TOKEN):
        operator, tokens = pop_next_token(tokens)
        tokens, node_r = factor(tokens)
        node = BinOp(node, operator, node_r)

    return tokens, node


def expression(tokens):
    tokens, node = term(tokens)

    while tokens[0] in (PLUS_TOKEN, MINUS_TOKEN):
        operator, tokens = pop_next_token(tokens)
        tokens, node_r = term(tokens)
        node = BinOp(node, operator, node_r)

    return tokens, node


class AST:
    pass


class BinOp(AST):
    def __init__(self, node_l, operator, node_r):
        self.node_l = node_l
        self.operator = operator
        self.node_r = node_r


class UnaryOp(AST):
    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class NodeVisitor:
    def visit(self, node):
        nodeclassname = node.__class__.__name__
        if not hasattr(self, nodeclassname):
            raise Exception(f'[ERROR] Unknown node to visit: {nodeclassname}')
        visitor = getattr(self, nodeclassname)
        return visitor(node)

    def Num(self, node):
        return node.value

    def UnaryOp(self, node):
        if node.operator == PLUS_TOKEN:
            return self.visit(node.expression)
        elif node.operator == MINUS_TOKEN:
            return self.visit(node.expression) * -1
        else:
            raise Exception(f'[ERROR] Bad unary op operator: {node.operator}')

    def BinOp(self, node):
        if node.operator == PLUS_TOKEN:
            return self.visit(node.node_l) + self.visit(node.node_r)
        elif node.operator == MINUS_TOKEN:
            return self.visit(node.node_l) - self.visit(node.node_r)
        elif node.operator == MULT_TOKEN:
            return self.visit(node.node_l) * self.visit(node.node_r)
        elif node.operator == DIV_TOKEN:
            return self.visit(node.node_l) / self.visit(node.node_r)
        else:
            raise Exception(f'[ERROR] Unexpected BinOp node: {node.operator}')


def run(source):
    tokens = tokenise(source)
    _, node = expression(tokens)

    return NodeVisitor().visit(node)


if __name__ == '__main__':
    code = '2+3'
    code = '-1'
    # code = '#'
    print(
        run(code),
        eval(code)
    )
