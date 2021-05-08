import CompilerSrc.comp as cmp


def test_Token():
    token = cmp.Token('INTEGER', 123)
    assert token

    token2 = cmp.Token('INTEGER', 123)
    assert token == token2

    token3 = cmp.Token('INTEGER', 1234)
    assert token != token3
