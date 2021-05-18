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
NEWLINE = '\n'

ASSIGN = COLON + EQUAL
ID = 'ID'
INTEGER = 'INTEGER'
BEGIN = 'BEGIN'
END = 'END'
EOF = 'EOF'


is_digit = lambda char: char in DIGITS
is_alpha = lambda char: char in ALPHA
pop_next_token = lambda tokens: (tokens[0], tokens[1:])
put_back_token = lambda token, tokens: (token,) + tokens
nexttoken = lambda tokens: tokens[0]





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
SEMI_TOKEN = Token(SEMICOLON, SEMICOLON)

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
        nextchar = ''

        if index < len(source) - 1:
            nextchar = source[index+1]

        if char in [SPACE, NEWLINE]:
            token = None
        elif char == PLUS:
            token = PLUS_TOKEN
        elif char == MINUS:
            token = MINUS_TOKEN
        elif char == MULT:
            token = MULT_TOKEN
        elif char == DIV:
            token = DIV_TOKEN
        elif char == PAREN_L:
            token = PAREN_L_TOKEN
        elif char == PAREN_R:
            token = PAREN_R_TOKEN
        elif char == SEMICOLON:
            token = SEMI_TOKEN
        elif char == DOT:
            token = DOT_TOKEN
        elif char + nextchar == ASSIGN:
            index += 1
            token = ASSIGN_TOKEN
        elif is_digit(char):
            token, index = find_int_token(source, index)
        elif is_alpha(char):
            token, index = find_alpha_token(source, index)
        else:
            raise Exception(f'[ERROR][tokenise] Bad char: "{char}", ord: {ord(char)}')

        if token:
            tokens += (token,)

        index += 1

    token = EOF_TOKEN
    tokens += (token,)

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
        assert paren_r == PAREN_R_TOKEN, f'[ERROR][factor] expected: {PAREN_R_TOKEN} got: {paren_r}'

    elif token in [MINUS_TOKEN, PLUS_TOKEN]:
        tokens, node = factor(tokens)
        node = UnaryOp(token, node)

    elif token.type_ == 'ID':
        tokens = put_back_token(token, tokens)
        tokens, node = do_variable(tokens)

    else:
        raise Exception(f'[ERROR][factor] Unecpeted token: {token}')

    return tokens, node


def term(tokens):
    tokens, node = factor(tokens)

    while nexttoken(tokens) in (MULT_TOKEN, DIV_TOKEN):
        operator, tokens = pop_next_token(tokens)
        tokens, node_r = factor(tokens)
        node = BinOp(node, operator, node_r)

    return tokens, node


def expression(tokens):
    tokens, node = term(tokens)

    while nexttoken(tokens) in (PLUS_TOKEN, MINUS_TOKEN):
        operator, tokens = pop_next_token(tokens)
        tokens, node_r = term(tokens)
        node = BinOp(node, operator, node_r)

    return tokens, node






def program(tokens):
    tokens, node = compound_statement(tokens)

    token, tokens = pop_next_token(tokens)
    assert token == DOT_TOKEN, f'[ERROR][Program] expected: {DOT_TOKEN} got: {token}'

    token, tokens = pop_next_token(tokens)
    assert token == EOF_TOKEN, f'[ERROR][Program] expected: {EOF_TOKEN} got: {token}'

    return tokens, node



def compound_statement(tokens):
    node = Compound()

    token, tokens = pop_next_token(tokens)
    assert token == BEGIN_TOKEN, f'[ERROR][compound_statement] expected: {BEGIN_TOKEN} got: {token}'

    tokens, node.children = statement_list(tokens)

    token, tokens = pop_next_token(tokens)
    assert token == END_TOKEN, f'[ERROR][compound_statement] expected: {END_TOKEN} got: {token}'

    return tokens, node



def statement_list(tokens):
    tokens, node = statement(tokens)
    nodelist = [node]

    while nexttoken(tokens) == SEMI_TOKEN:
        _, tokens = pop_next_token(tokens)
        tokens, node = statement(tokens)
        nodelist += [node]

    return tokens, nodelist



def statement(tokens):
    if nexttoken(tokens) == BEGIN_TOKEN:
        tokens, node = compound_statement(tokens)
    elif nexttoken(tokens).type_ == ID:
        tokens, node = assign_statement(tokens)
    else:
        node = NoOp()

    return tokens, node



def assign_statement(tokens):
    tokens, varnode = do_variable(tokens)
    assigntoken, tokens = pop_next_token(tokens)
    assert assigntoken == ASSIGN_TOKEN, (f'[ERROR][assign_statement] expected:'
        f' {ASSIGN_TOKEN} got: {assigntoken}')
    tokens, expressionnode = expression(tokens)
    node = Assign(varnode, assigntoken, expressionnode)
    return tokens, None



def do_variable(tokens):
    token, tokens = pop_next_token(tokens)
    assert token.type_ == ID, f'[do_variable] expected: {ID}, got: {token}'
    node = Variable(token)

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


class Compound(AST):
    def __init__(self):
        self.children = ()


class Assign(AST):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class Variable(AST):
    def __init__(self, name):
        self.name = name


class NoOp(AST):
    pass



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
    code = """
BEGIN
    BEGIN
        number := 2;
        a := number;
        b := 10 * a + 10 * number / 4;
        c := a - - b
    END;
    x := 11;
END.
"""
    tokens = tokenise(code)
    for token in tokens:
        print(token)
    program(tokens)
