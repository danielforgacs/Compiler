SPACE = ' '
DIGITS = '0123456789'
ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
PLUS, MINUS = '+', '-'
MULT, DIV = '*', '/'
PAREN_L, PAREN_R = '(', ')'
CURLY_L, CURLY_R = '{', '}'
EQUAL = '='
COLON = ':'
SEMICOLON = ';'
DOT = '.'
COMMA = ','
QUOTE = "'"
NEWLINE = '\n'

ASSIGN = COLON + EQUAL

ID = 'ID'
INTEGER = 'INTEGER'
BEGIN = 'BEGIN'
END = 'END'
EOF = 'EOF'
PROGRAM = 'PROGRAM'
VAR = 'VAR'
INT_TYPE = 'INT_TYPE'
REAL_TYPE = 'REAL'
F_DIV = 'DIV'
FLOAT = 'FLOAT'


is_digit = lambda char: char in DIGITS
is_alpha = lambda char: char in ALPHA
is_alphanum = lambda char: char in ALPHA + DIGITS
pop_next_token = lambda tokens: (tokens[0], tokens[1:])
put_back_token = lambda token, tokens: (token,) + tokens
nexttoken = lambda tokens: tokens[0]



class MakeDict:
    @property
    def asdict(self):
        data = {}
        for attrname, value in self.__dict__.items():
            if hasattr(value, 'asdict'):
                attrname = '{}.{}'.format(attrname, value.__class__.__name__)
                value = value.asdict
            data[attrname] = value
        return data


    @classmethod
    def from_dict(cls, data):
        kwargs = {}
        for idx in range(1, cls.__init__.__code__.co_argcount):
            key = cls.__init__.__code__.co_varnames[idx]
            kwargs[key] = data[key]
        newinstance = cls(**kwargs)
        for attrname, value in data.items():
            setattr(newinstance, attrname, value)
        return newinstance




class Token(MakeDict):
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
COLON_TOKEN = Token(COLON, COLON)
SEMI_TOKEN = Token(SEMICOLON, SEMICOLON)
COMMA_TOKEN = Token(COMMA, COMMA)
QUOTE_TOKEN = Token(QUOTE, QUOTE)

BEGIN_TOKEN = Token(BEGIN, BEGIN)
END_TOKEN = Token(END, END)
DOT_TOKEN = Token(DOT, DOT)
ASSIGN_TOKEN = Token(ASSIGN, ASSIGN)
PROGRAM_TOKEN = Token(PROGRAM, PROGRAM)
VAR_TOKEN = Token(VAR, VAR)
INT_TYPE_TOKEN = Token(INT_TYPE, INT_TYPE)
REAL_TYPE_TOKEN = Token(REAL_TYPE, REAL_TYPE)
F_DIV_TOKEN = Token(F_DIV, F_DIV)





def find_int_token(src, index):
    result = ''
    is_float = False
    char = src[index]

    while is_digit(char):
        result += char
        index += 1

        if index == len(src):
            break

        char = src[index]

        if char == DOT:
            is_float = True
            result += char
            index += 1
            char = src[index]

    if is_float:
        token = Token(FLOAT, float(result))
    else:
        token = Token(INTEGER, int(result))

    index -= 1

    return token, index





def find_alpha_token(src, index):
    result = ''
    char = src[index]

    while is_alphanum(char):
        result += char
        index += 1

        if index == len(src):
            break

        char = src[index]

    if result == BEGIN:
        token = BEGIN_TOKEN
    elif result == END:
        token = END_TOKEN
    elif result == PROGRAM:
        token = PROGRAM_TOKEN
    elif result == VAR:
        token = VAR_TOKEN
    elif result == INTEGER:
        token = INT_TYPE_TOKEN
    elif result == REAL_TYPE:
        token = REAL_TYPE_TOKEN
    elif result == F_DIV:
        token = F_DIV_TOKEN
    else:
        token = Token(ID, result)

    index -= 1

    return token, index




def tokenise(source):
    index = 0
    tokens = ()

    while index < len(source):
        if source[index] == CURLY_L:
            index += 1
            while source[index] != CURLY_R:
                index += 1
            index += 1

            continue

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
        elif char == COLON:
            token = COLON_TOKEN
            if nextchar == EQUAL:
                index += 1
                token = ASSIGN_TOKEN
        elif char == COMMA:
            token = COMMA_TOKEN
        elif char == QUOTE:
            token = QUOTE_TOKEN
        elif is_digit(char):
            token, index = find_int_token(source, index)
        elif is_alpha(char):
            token, index = find_alpha_token(source, index)
        else:
            raise Exception(
                f'[tokenise] Bad char: "{char}", ord: {ord(char)}'
                f' index: {index}')

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
        assert paren_r == PAREN_R_TOKEN, f'[factor] expected: {PAREN_R_TOKEN} got: {paren_r}'

    elif token in [MINUS_TOKEN, PLUS_TOKEN]:
        tokens, node = factor(tokens)
        node = UnaryOp(token, node)

    elif token.type_ == 'ID':
        tokens = put_back_token(token, tokens)
        tokens, node = do_variable(tokens)

    else:
        raise Exception(f'[factor] Unecpeted token: {token}')

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
    assert token == DOT_TOKEN, f'[Program] expected: {DOT_TOKEN} got: {token}'

    token, tokens = pop_next_token(tokens)
    assert token == EOF_TOKEN, f'[Program] expected: {EOF_TOKEN} got: {token}'

    return tokens, node



def compound_statement(tokens):
    token, tokens = pop_next_token(tokens)
    assert token == BEGIN_TOKEN, f'[compound_statement] expected: {BEGIN_TOKEN} got: {token}'

    node = Compound()
    tokens, node.children = statement_list(tokens)

    token, tokens = pop_next_token(tokens)
    assert token == END_TOKEN, f'[compound_statement] expected: {END_TOKEN} got: {token}'

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
    assert assigntoken == ASSIGN_TOKEN, (f'[assign_statement] expected:'
        f' {ASSIGN_TOKEN} got: {assigntoken}')
    tokens, expressionnode = expression(tokens)
    node = Assign(varnode, assigntoken, expressionnode)
    return tokens, node



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


class Variable(AST, MakeDict):
    def __init__(self, name):
        self.name = name


class NoOp(AST):
    pass



class NodeVisitor:
    GLOBAL_SCOPE = {}


    def visit(self, node):
        nodeclassname = node.__class__.__name__
        if not hasattr(self, nodeclassname):
            raise Exception(f'[NodeVisitor] Unknown node to visit: {nodeclassname}')
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
            raise Exception(f'[visit_UnaryOp] Bad unary op operator: {node.operator}')

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
            raise Exception(f'[visit_BinOp Unexpected BinOp node: {node.operator}')

    def Compound(self, node):
        for child in node.children:
            self.visit(child)

    def Assign(self, node):
        self.GLOBAL_SCOPE[node.left.name.value] = self.visit(node.right)

    def Variable(self, node):
        return self.GLOBAL_SCOPE[node.name.value]

    def NoOp(self, node):
        pass


def run(source):
    tokens = tokenise(source)
    _, node = expression(tokens)

    return NodeVisitor().visit(node)


def run_program(source):
    tokens = tokenise(source)
    _, node = program(tokens)

    nodevisitor =  NodeVisitor()
    result = nodevisitor.visit(node)
    print('GLOBAL_SCOPE:', nodevisitor.GLOBAL_SCOPE)
    return result
