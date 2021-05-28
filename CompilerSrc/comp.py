SPACE = ' '
DIGITS = '0123456789'
ALPHA = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
PLUS, MINUS = '+', '-'
MULT, FLOAT_DIV, INT_DIV = '*', '/', 'DIV'
PAREN_L, PAREN_R = '(', ')'
CURLY_L, CURLY_R = '{', '}'
EQUAL = '='
COLON = ':'
SEMICOLON = ';'
DOT = '.'
COMMA = ','
QUOTE = "'"
NEWLINE = '\n'


ID = 'ID'
ASSIGN = COLON + EQUAL
INT_CONST = 'INT_CONST'
FLOAT_CONST = 'FLOAT_CONST'

PROGRAM = 'PROGRAM'
VAR = 'VAR'
INTEGER = 'INTEGER'
REAL = 'REAL'
BEGIN = 'BEGIN'
END = 'END'
EOF = 'EOF'


is_digit = lambda char: char in DIGITS
is_alpha = lambda char: char in ALPHA
is_alphanum = lambda char: char in ALPHA + DIGITS
pop_next_token = lambda tokens: (tokens[0], tokens[1:])
put_back_token = lambda token, tokens: (token,) + tokens
nexttoken = lambda tokens: tokens[0]



class DictSerialiseBase:
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




class Token(DictSerialiseBase):
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value

    def __eq__(self, other):
        return (self.type_ == other.type_) and (self.value == other.value)

    def __repr__(self):
        return '<Token:{}:{}>'.format(self.type_, self.value)




PROGRAM_TOKEN = Token(PROGRAM, PROGRAM)
VAR_TOKEN = Token(VAR, VAR)
BEGIN_TOKEN = Token(BEGIN, BEGIN)
END_TOKEN = Token(END, END)
DOT_TOKEN = Token(DOT, DOT)
EOF_TOKEN = Token(EOF, EOF)

ASSIGN_TOKEN = Token(ASSIGN, ASSIGN)
INT_TOKEN = Token(INTEGER, INTEGER)
REAL_TOKEN = Token(REAL, REAL)

PLUS_TOKEN = Token(PLUS, PLUS)
MINUS_TOKEN = Token(MINUS, MINUS)
MULT_TOKEN = Token(MULT, MULT)
DIV_TOKEN = Token(FLOAT_DIV, FLOAT_DIV)
INT_DIV_TOKEN = Token(INT_DIV, INT_DIV)

PAREN_L_TOKEN = Token(PAREN_L, PAREN_L)
PAREN_R_TOKEN = Token(PAREN_R, PAREN_R)
COLON_TOKEN = Token(COLON, COLON)
SEMI_TOKEN = Token(SEMICOLON, SEMICOLON)
COMMA_TOKEN = Token(COMMA, COMMA)
QUOTE_TOKEN = Token(QUOTE, QUOTE)






def extract_number_token(src, index):
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
        token = Token(FLOAT_CONST, float(result))
    else:
        token = Token(INT_CONST, int(result))

    index -= 1

    return token, index





def extract_alphanumeric_token(src, index):
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
        token = INT_TOKEN
    elif result == REAL:
        token = REAL_TOKEN
    elif result == INT_DIV:
        token = INT_DIV_TOKEN
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
        elif char == FLOAT_DIV:
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
            token, index = extract_number_token(source, index)
        elif is_alpha(char):
            token, index = extract_alphanumeric_token(source, index)
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
    token, tokens = pop_next_token(tokens)

    if token.type_ == INT_CONST:
        node = NumNode(token)

    elif token == PAREN_L_TOKEN:
        tokens, node = expression(tokens)
        paren_r, tokens = pop_next_token(tokens)
        assert paren_r == PAREN_R_TOKEN, f'[factor] expected: {PAREN_R_TOKEN} got: {paren_r}'

    elif token in [MINUS_TOKEN, PLUS_TOKEN]:
        tokens, node = factor(tokens)
        node = UnaryOpNode(token, node)

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
        node = BinOpNode(node, operator, node_r)

    return tokens, node


def expression(tokens):
    tokens, node = term(tokens)

    while nexttoken(tokens) in (PLUS_TOKEN, MINUS_TOKEN):
        operator, tokens = pop_next_token(tokens)
        tokens, node_r = term(tokens)
        node = BinOpNode(node, operator, node_r)

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

    node = CompoundNode()
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
        node = NoOpNode()

    return tokens, node



def assign_statement(tokens):
    tokens, varnode = do_variable(tokens)
    assigntoken, tokens = pop_next_token(tokens)
    assert assigntoken == ASSIGN_TOKEN, (f'[assign_statement] expected:'
        f' {ASSIGN_TOKEN} got: {assigntoken}')
    tokens, expressionnode = expression(tokens)
    node = AssignNode(varnode, assigntoken, expressionnode)
    return tokens, node



def do_variable(tokens):
    token, tokens = pop_next_token(tokens)
    assert token.type_ == ID, f'[do_variable] expected: {ID}, got: {token}'
    node = VariableNode(token)

    return tokens, node



class ASTNodeBase:
    pass


class BinOpNode(ASTNodeBase):
    def __init__(self, node_l, operator, node_r):
        self.node_l = node_l
        self.operator = operator
        self.node_r = node_r


class UnaryOpNode(ASTNodeBase):
    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression


class NumNode(ASTNodeBase):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class CompoundNode(ASTNodeBase):
    def __init__(self):
        self.children = ()


class AssignNode(ASTNodeBase):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class VariableNode(ASTNodeBase, DictSerialiseBase):
    def __init__(self, name):
        self.name = name


class NoOpNode(ASTNodeBase):
    pass



class NodeVisitor:
    GLOBAL_SCOPE = {}


    def visit(self, node):
        nodeclassname = node.__class__.__name__
        visitormethodname = 'visit_{}'.format(nodeclassname)
        if not hasattr(self, visitormethodname):
            raise Exception(f'[NodeVisitor] Unknown node to visit: {nodeclassname}')
        visitormethod = getattr(self, visitormethodname)
        return visitormethod(node)

    def visit_NumNode(self, node):
        return node.value

    def visit_UnaryOpNode(self, node):
        if node.operator == PLUS_TOKEN:
            return self.visit(node.expression)
        elif node.operator == MINUS_TOKEN:
            return self.visit(node.expression) * -1
        else:
            raise Exception(f'[visit_UnaryOp] Bad unary op operator: {node.operator}')

    def visit_BinOpNode(self, node):
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

    def visit_CompoundNode(self, node):
        for child in node.children:
            self.visit(child)

    def visit_AssignNode(self, node):
        self.GLOBAL_SCOPE[node.left.name.value] = self.visit(node.right)

    def visit_VariableNode(self, node):
        return self.GLOBAL_SCOPE[node.name.value]

    def visit_NoOpNode(self, node):
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
