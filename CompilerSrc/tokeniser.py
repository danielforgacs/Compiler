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
            elif isinstance(value, list):
                values = []
                for item in value:
                    values.append(item.asdict)
                value = values
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
