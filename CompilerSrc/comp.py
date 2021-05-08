INTEGER = 'INTEGER'
EOF = 'EOF'


is_digit = lambda x: x in '0123456789'


class Token:
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value
    def __eq__(self, other):
        return (self.type_ == other.type_) and (self.value == other.value)
    def __repr__(self):
        return '<Token:{}:{}>'.format(self.type_, self.value)




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

        index += 1

    tokens += (Token(EOF, EOF),)

    return tokens
