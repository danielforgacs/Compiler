import pytest
import CompilerSrc.comp as cmp
import CompilerSrc.tokeniser as tok



def test_Token():
    token = tok.Token('INTEGER', 123)
    assert token

    token2 = tok.Token('INTEGER', 123)
    assert token == token2

    token3 = tok.Token('INTEGER', 1234)
    assert token != token3


@pytest.mark.parametrize('source, expected', [
    ['0', tok.Token(tok.INT_CONST, 0)],
    ['1', tok.Token(tok.INT_CONST, 1)],
    ['10', tok.Token(tok.INT_CONST, 10)],
    ['10198603', tok.Token(tok.INT_CONST, 10198603)],
    ['10198603    ', tok.Token(tok.INT_CONST, 10198603)],
    ['1   0198603    ', tok.Token(tok.INT_CONST, 1)],
    ['101\n98603    ', tok.Token(tok.INT_CONST, 101)],
])
def test_find_int_token(source, expected):
    token, _ = tok.extract_number_token(source, 0)
    assert  token == expected


@pytest.mark.parametrize('source, expected', [
    [
        (
            ''
        ),
        (
            tok.Token(tok.EOF, tok.EOF),
        )
    ],
    [
        (
            '1'
        ),
        (
            tok.Token(tok.INT_CONST, 1),
            tok.Token(tok.EOF, tok.EOF),
        )
    ],
    [
        (
            '1 22  333    654987     '
        ),
        (
            tok.Token(tok.INT_CONST, 1),
            tok.Token(tok.INT_CONST, 22),
            tok.Token(tok.INT_CONST, 333),
            tok.Token(tok.INT_CONST, 654987),
            tok.Token(tok.EOF, tok.EOF),
        )
    ],
    [
        (
            '+   +   ++    '
        ),
        (
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.EOF, tok.EOF),
        )
    ],
    [
        (
            '+   -   +--+    ++--++  */*//**   '
        ),
        (
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.MINUS, tok.MINUS),

            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.MINUS, tok.MINUS),
            tok.Token(tok.MINUS, tok.MINUS),
            tok.Token(tok.PLUS, tok.PLUS),

            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.MINUS, tok.MINUS),
            tok.Token(tok.MINUS, tok.MINUS),
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.PLUS, tok.PLUS),

            tok.Token(tok.MULT, tok.MULT),
            tok.Token(tok.FLOAT_DIV, tok.FLOAT_DIV),
            tok.Token(tok.MULT, tok.MULT),
            tok.Token(tok.FLOAT_DIV, tok.FLOAT_DIV),
            tok.Token(tok.FLOAT_DIV, tok.FLOAT_DIV),
            tok.Token(tok.MULT, tok.MULT),
            tok.Token(tok.MULT, tok.MULT),

            tok.Token(tok.EOF, tok.EOF),
        )
    ],
    [
        (
            '  1 + 22 -- 333   *   ** 456 //   /'
        ),
        (
            tok.Token(tok.INT_CONST, 1),
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.INT_CONST, 22),
            tok.Token(tok.MINUS, tok.MINUS),
            tok.Token(tok.MINUS, tok.MINUS),
            tok.Token(tok.INT_CONST, 333),
            tok.Token(tok.MULT, tok.MULT),
            tok.Token(tok.MULT, tok.MULT),
            tok.Token(tok.MULT, tok.MULT),
            tok.Token(tok.INT_CONST, 456),
            tok.Token(tok.FLOAT_DIV, tok.FLOAT_DIV),
            tok.Token(tok.FLOAT_DIV, tok.FLOAT_DIV),
            tok.Token(tok.FLOAT_DIV, tok.FLOAT_DIV),
            tok.Token(tok.EOF, tok.EOF),
        )
    ],
    [
        (
            '123+567'
        ),
        (
            tok.Token(tok.INT_CONST, 123),
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.INT_CONST, 567),
            tok.Token(tok.EOF, tok.EOF),
        )
    ],
    [
        (
            '123+'
        ),
        (
            tok.Token(tok.INT_CONST, 123),
            tok.Token(tok.PLUS, tok.PLUS),
            tok.Token(tok.EOF, tok.EOF),
        )
    ],
])
def test_tokenize(source, expected):
    tokens = tok.tokenise(source)
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
    ('BEGIN', (tok.BEGIN_TOKEN, tok.EOF_TOKEN)),
    ('END', (tok.END_TOKEN, tok.EOF_TOKEN)),
    ('.', (tok.DOT_TOKEN, tok.EOF_TOKEN)),
    (':=', (tok.ASSIGN_TOKEN, tok.EOF_TOKEN)),
    ('ubuntu', (tok.Token(tok.ID, 'ubuntu'), tok.EOF_TOKEN)),
    (
        'BEGIN END.',
        (
            tok.BEGIN_TOKEN,
            tok.END_TOKEN,
            tok.DOT_TOKEN,
            tok.EOF_TOKEN
        )
    ),
    (
        'BEGIN END   BEGIN    aaa  bbb  END END.BEGIN.END',
        (
            tok.BEGIN_TOKEN,
            tok.END_TOKEN,
            tok.BEGIN_TOKEN,
            tok.Token(tok.ID, 'aaa'),
            tok.Token(tok.ID, 'bbb'),
            tok.END_TOKEN,
            tok.END_TOKEN,
            tok.DOT_TOKEN,
            tok.BEGIN_TOKEN,
            tok.DOT_TOKEN,
            tok.END_TOKEN,
            tok.EOF_TOKEN
        )
    ),
    (
        'PROGRAM',
        (   tok.PROGRAM_TOKEN,
            tok.EOF_TOKEN,
        )
    ),
])
def test_new_tokens(source, expected):
    assert tok.tokenise(source) == expected


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
    cmp.program(tok.tokenise(source))
    cmp.run_program(source)




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
    cmp.program(tok.tokenise(source))
    cmp.run_program(source)



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
    cmp.program(tok.tokenise(source))
    cmp.run_program(source)


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



@pytest.mark.parametrize('source', [
    """
BEGIN
{@@@@@@@@@@@}
END.
""",
    """
BEGIN
{@@@@@@}{@@@@@}
END.
""",
    """
BEGIN
{
    @@@@@@
    }
      {      @@@@@
            }
            BEGIN
    {                   }
        END
END.
""",
])
def test_comment(source):
    cmp.run_program(source)




@pytest.fixture
def fx_src_program():
    return 'PROGRAM', (tok.PROGRAM_TOKEN, tok.EOF_TOKEN)

@pytest.fixture
def fx_src_begin(fx_src_program):
    src = fx_src_program[0] + ' BEGIN'
    tokens = fx_src_program[1][:-1]
    tokens += (tok.BEGIN_TOKEN, tok.EOF_TOKEN)
    return src, tokens

def test_program_token(fx_src_program):
    assert tok.tokenise(fx_src_program[0]) == fx_src_program[1]

def test_begin_token(fx_src_begin):
    assert tok.tokenise(fx_src_begin[0]) == fx_src_begin[1]



def test_tokenise_full_program_chapter_10():
    source = (
        "PROGRAM Part10;\n"
        "VAR\n"
        "number     : INTEGER;\n"
        "a, b, c, x : INTEGER;\n"
        "y          : REAL;\n"
        "\n"
        "BEGIN {Part10}\n"
        "   BEGIN\n"
        "   number := 2;\n"
        "   a := number;\n"
        "   b := 10 * a + 10 * number DIV 4;\n"
        "   c := a - - b\n"
        "END;\n"
        "   x := 11;\n"
        "   y := 20 / 7 + 3.14;\n"
        "   { writeln('a = ', a); }\n"
        "   { writeln('b = ', b); }\n"
        "   { writeln('c = ', c); }\n"
        "   { writeln('number = ', number); }\n"
        "   { writeln('x = ', x); }\n"
        "   { writeln('y = ', y); }\n"
        "END. {Part10}"
    )

    expected = (
        tok.PROGRAM_TOKEN,
        tok.Token(tok.ID, 'Part10'),
        tok.SEMI_TOKEN,
        tok.VAR_TOKEN,

        tok.Token(tok.ID, 'number'),
        tok.COLON_TOKEN,
        tok.INT_TOKEN,
        tok.SEMI_TOKEN,

        tok.Token(tok.ID, 'a'),
        tok.COMMA_TOKEN,
        tok.Token(tok.ID, 'b'),
        tok.COMMA_TOKEN,
        tok.Token(tok.ID, 'c'),
        tok.COMMA_TOKEN,
        tok.Token(tok.ID, 'x'),
        tok.COLON_TOKEN,
        tok.INT_TOKEN,
        tok.SEMI_TOKEN,

        tok.Token(tok.ID, 'y'),
        tok.COLON_TOKEN,
        tok.REAL_TOKEN,
        tok.SEMI_TOKEN,

        tok.BEGIN_TOKEN,
        tok.BEGIN_TOKEN,

        tok.Token(tok.ID, 'number'),
        tok.ASSIGN_TOKEN,
        tok.Token(tok.INT_CONST, 2),
        tok.SEMI_TOKEN,

        tok.Token(tok.ID, 'a'),
        tok.ASSIGN_TOKEN,
        tok.Token(tok.ID, 'number'),
        tok.SEMI_TOKEN,

        tok.Token(tok.ID, 'b'),
        tok.ASSIGN_TOKEN,
        tok.Token(tok.INT_CONST, 10),
        tok.MULT_TOKEN,
        tok.Token(tok.ID, 'a'),
        tok.PLUS_TOKEN,
        tok.Token(tok.INT_CONST, 10),
        tok.MULT_TOKEN,
        tok.Token(tok.ID, 'number'),
        tok.INT_DIV_TOKEN,
        tok.Token(tok.INT_CONST, 4),
        tok.SEMI_TOKEN,

        tok.Token(tok.ID, 'c'),
        tok.ASSIGN_TOKEN,
        tok.Token(tok.ID, 'a'),
        tok.MINUS_TOKEN,
        tok.MINUS_TOKEN,
        tok.Token(tok.ID, 'b'),

        tok.END_TOKEN,
        tok.SEMI_TOKEN,

        tok.Token(tok.ID, 'x'),
        tok.ASSIGN_TOKEN,
        tok.Token(tok.INT_CONST, 11),
        tok.SEMI_TOKEN,

        tok.Token(tok.ID, 'y'),
        tok.ASSIGN_TOKEN,
        tok.Token(tok.INT_CONST, 20),
        tok.DIV_TOKEN,
        tok.Token(tok.INT_CONST, 7),
        tok.PLUS_TOKEN,
        tok.Token(tok.FLOAT_CONST, 3.14),
        tok.SEMI_TOKEN,

        tok.END_TOKEN,
        tok.DOT_TOKEN,

        tok.EOF_TOKEN,
    )
    assert tok.tokenise(source=source) == expected



@pytest.mark.skip('WIP fill program')
def test_program():
    source = """
        PROGRAM Part10;
        VAR
            number     : INTEGER;
            a, b, c, x : INTEGER;
            y          : REAL;

        BEGIN {Part10}
            BEGIN
                number := 2;
                a := number;
                b := 10 * a + 10 * number DIV 4;
                c := a - - b
            END;
            x := 11;
            y := 20 / 7 + 3.14;
            writeln('a = ', a);
            writeln('b = ', b);
            writeln('c = ', c);
            writeln('number = ', number);
            writeln('x = ', x);
            writeln('y = ', y);
        END.  {Part10}
    """
    cmp.run_program(source=source)
