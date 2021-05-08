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
])
def test_tokenize(source, expected):
    tokens = cmp.tokenise(source)
    assert tokens == expected
