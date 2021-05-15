import pytest
import CompilerSrc.comp as cmp


def test_Token():
    token = cmp.Token('INTEGER', 123)
    assert token

    token2 = cmp.Token('INTEGER', 123)
    assert token == token2

    token3 = cmp.Token('INTEGER', 1234)
    assert token != token3


@pytest.mark.parametrize('source, expected', [
    ['0', cmp.Token(cmp.INTEGER, 0)],
    ['1', cmp.Token(cmp.INTEGER, 1)],
    ['10', cmp.Token(cmp.INTEGER, 10)],
    ['10198603', cmp.Token(cmp.INTEGER, 10198603)],
    ['10198603    ', cmp.Token(cmp.INTEGER, 10198603)],
    ['1   0198603    ', cmp.Token(cmp.INTEGER, 1)],
    ['101\n98603    ', cmp.Token(cmp.INTEGER, 101)],
])
def test_find_int_token(source, expected):
    token, _ = cmp.find_int_token(source, 0)
    assert  token == expected


@pytest.mark.parametrize('source, expected', [
    [
        (
            ''
        ),
        (
            cmp.Token(cmp.EOF, cmp.EOF),
        )
    ],
    [
        (
            '1'
        ),
        (
            cmp.Token(cmp.INTEGER, 1),
            cmp.Token(cmp.EOF, cmp.EOF),
        )
    ],
    [
        (
            '1 22  333    654987     '
        ),
        (
            cmp.Token(cmp.INTEGER, 1),
            cmp.Token(cmp.INTEGER, 22),
            cmp.Token(cmp.INTEGER, 333),
            cmp.Token(cmp.INTEGER, 654987),
            cmp.Token(cmp.EOF, cmp.EOF),
        )
    ],
    [
        (
            '+   +   ++    '
        ),
        (
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.EOF, cmp.EOF),
        )
    ],
    [
        (
            '+   -   +--+    ++--++  */*//**   '
        ),
        (
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.SUB, cmp.SUB),

            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.SUB, cmp.SUB),
            cmp.Token(cmp.SUB, cmp.SUB),
            cmp.Token(cmp.ADD, cmp.ADD),

            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.SUB, cmp.SUB),
            cmp.Token(cmp.SUB, cmp.SUB),
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.ADD, cmp.ADD),

            cmp.Token(cmp.MULT, cmp.MULT),
            cmp.Token(cmp.DIV, cmp.DIV),
            cmp.Token(cmp.MULT, cmp.MULT),
            cmp.Token(cmp.DIV, cmp.DIV),
            cmp.Token(cmp.DIV, cmp.DIV),
            cmp.Token(cmp.MULT, cmp.MULT),
            cmp.Token(cmp.MULT, cmp.MULT),

            cmp.Token(cmp.EOF, cmp.EOF),
        )
    ],
    [
        (
            '  1 + 22 -- 333   *   ** 456 //   /'
        ),
        (
            cmp.Token(cmp.INTEGER, 1),
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.INTEGER, 22),
            cmp.Token(cmp.SUB, cmp.SUB),
            cmp.Token(cmp.SUB, cmp.SUB),
            cmp.Token(cmp.INTEGER, 333),
            cmp.Token(cmp.MULT, cmp.MULT),
            cmp.Token(cmp.MULT, cmp.MULT),
            cmp.Token(cmp.MULT, cmp.MULT),
            cmp.Token(cmp.INTEGER, 456),
            cmp.Token(cmp.DIV, cmp.DIV),
            cmp.Token(cmp.DIV, cmp.DIV),
            cmp.Token(cmp.DIV, cmp.DIV),
            cmp.Token(cmp.EOF, cmp.EOF),
        )
    ],
    [
        (
            '123+567'
        ),
        (
            cmp.Token(cmp.INTEGER, 123),
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.INTEGER, 567),
            cmp.Token(cmp.EOF, cmp.EOF),
        )
    ],
    [
        (
            '123+'
        ),
        (
            cmp.Token(cmp.INTEGER, 123),
            cmp.Token(cmp.ADD, cmp.ADD),
            cmp.Token(cmp.EOF, cmp.EOF),
        )
    ],
])
def test_tokenize(source, expected):
    tokens = cmp.tokenise(source)
    assert tokens == expected


@pytest.mark.parametrize('source', [
    '1+2',
    '1234  +    8765    ',
    '1234  -    8765    ',

    '1+2+3',
    '11   + 222   - 44   + 5555',
    '11   + 222   - 44   + 5555    +  11   - 222   + 44   + 13243',
])
def test_expression(source):
    assert cmp.run(source) == eval(source)


@pytest.mark.parametrize('source', [
    '2*3*4',
    '    23 *   31  *    5  ',
])
def test_term(source):
    assert cmp.run(source) == eval(source)


@pytest.mark.parametrize('source', [
    '(0)',
    '(123)',
    '(123+456)',
    '((((5))))',
    '((((5  +  56))))',
    '2+(3*4)-5',
    '2+((3*4)-5) * 2+(3*4)-5',
    '10 / 5 / 2',
    '10 / (5 / 2)',
])
def test_parenthesis(source):
    assert cmp.run(source) == eval(source)


@pytest.mark.parametrize('source', [
    '-1',
    '--1',
    '----1',
    '-+-+-+-1',

    '+--+-+123  --++--++-+-++ 432',
    '+-(-+-+123)  --++--+(+-+-++ 432)',
    '+-(-+-+123)  --++--+(+-+-++ 432)',

    '+-(-+-+123) * --++--+(+-+-++ 432)',
])
def test_unary_op(source):
    assert cmp.run(source) == eval(source)


@pytest.mark.parametrize('source, expected', [
    ('BEGIN', (cmp.BEGIN_TOKEN, cmp.EOF_TOKEN)),
    ('END', (cmp.END_TOKEN, cmp.EOF_TOKEN)),
])
def test_new_tokens(source, expected):
    assert cmp.tokenise(source) == expected
