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
            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.EOF, cmp.EOF),
        )
    ],
    [
        (
            '+   -   +--+    ++--++  */*//**   '
        ),
        (
            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.MINUS, cmp.MINUS),

            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.MINUS, cmp.MINUS),
            cmp.Token(cmp.MINUS, cmp.MINUS),
            cmp.Token(cmp.PLUS, cmp.PLUS),

            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.MINUS, cmp.MINUS),
            cmp.Token(cmp.MINUS, cmp.MINUS),
            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.PLUS, cmp.PLUS),

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
            cmp.Token(cmp.PLUS, cmp.PLUS),
            cmp.Token(cmp.INTEGER, 22),
            cmp.Token(cmp.MINUS, cmp.MINUS),
            cmp.Token(cmp.MINUS, cmp.MINUS),
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
            cmp.Token(cmp.PLUS, cmp.PLUS),
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
            cmp.Token(cmp.PLUS, cmp.PLUS),
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
    ('.', (cmp.DOT_TOKEN, cmp.EOF_TOKEN)),
    (':=', (cmp.ASSIGN_TOKEN, cmp.EOF_TOKEN)),
    ('ubuntu', (cmp.Token(cmp.ID, 'ubuntu'), cmp.EOF_TOKEN)),
    (
        'BEGIN END.',
        (
            cmp.BEGIN_TOKEN,
            cmp.END_TOKEN,
            cmp.DOT_TOKEN,
            cmp.EOF_TOKEN
        )
    ),
    (
        'BEGIN END   BEGIN    aaa  bbb  END END.BEGIN.END',
        (
            cmp.BEGIN_TOKEN,
            cmp.END_TOKEN,
            cmp.BEGIN_TOKEN,
            cmp.Token(cmp.ID, 'aaa'),
            cmp.Token(cmp.ID, 'bbb'),
            cmp.END_TOKEN,
            cmp.END_TOKEN,
            cmp.DOT_TOKEN,
            cmp.BEGIN_TOKEN,
            cmp.DOT_TOKEN,
            cmp.END_TOKEN,
            cmp.EOF_TOKEN
        )
    ),
])
def test_new_tokens(source, expected):
    assert cmp.tokenise(source) == expected


@pytest.mark.parametrize('source, expected', [
    (
        'BEGIN END.',
        '',
    ),
    ("""
BEGIN END.""",
        '',
    ),
    ("""
BEGIN
    BEGIN
        BEGIN
            BEGIN
                BEGIN
                    BEGIN
                    END;
                END;
            END;
        END;
    END;
END
.
""",
        '',
    ),
    ("""
BEGIN
    BEGIN
        BEGIN
        END;
    END;
    BEGIN
        BEGIN
        END;
    END;
    BEGIN
        BEGIN
        END;
    END;
END
.
""",
        '',
    ),
])
def test_begin_end(source, expected):
    cmp.program(cmp.tokenise(source))


def test_begin_end():
    source = """
BEGIN
    varone := 1;
    vartwo := 2+3;
    BEGIN
        varthree := (4+5)*6;
        varthree := (4+5)*6;
        varthree := (4+5)*6
    END;
BEGIN
    varone := 1;
    vartwo := 2+3;
    BEGIN
        varthree := (4+5)*6;
        varthree := (4+5)*6;
        varthree := (4+5)*6
    END
END
END.
"""
    cmp.program(cmp.tokenise(source))



def test_program_ID_variable_Assignment_NoOp():
    source = """
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
    cmp.program(cmp.tokenise(source))


def test_program_ID_variable_Assignment_NoOp_program_run():
    source = """
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
    cmp.run_program(source=source)



def test_comments():
    source = """
{PROGRAM Part10;}
{VAR}
{   number     : INTEGER;}
{   a, b, c, x : INTEGER;}
{   y          : REAL;}

BEGIN {Part10}
   BEGIN
      number := 2;
      a := number;
      b := 10 * a + 10 * number DIV 4;
      c := a - - b
   END;
   x := 11;
   y := 20 / 7 + 3.14;
   { writeln('a = ', a); }
   { writeln('b = ', b); }
   { writeln('c = ', c); }
   { writeln('number = ', number); }
   { writeln('x = ', x); }
   { writeln('y = ', y); }
END.  {Part10}
"""
    cmp.run_program(source=source)


# def test_program():
#     source = """
# PROGRAM Part10;
# VAR
#    number     : INTEGER;
#    a, b, c, x : INTEGER;
#    y          : REAL;
#
# BEGIN {Part10}
#    BEGIN
#       number := 2;
#       a := number;
#       b := 10 * a + 10 * number DIV 4;
#       c := a - - b
#    END;
#    x := 11;
#    y := 20 / 7 + 3.14;
#    { writeln('a = ', a); }
#    { writeln('b = ', b); }
#    { writeln('c = ', c); }
#    { writeln('number = ', number); }
#    { writeln('x = ', x); }
#    { writeln('y = ', y); }
# END.  {Part10}
# """
#     cmp.run_program(source=source)
