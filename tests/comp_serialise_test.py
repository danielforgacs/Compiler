import CompilerSrc.comp as comp


def test_Token_serialise():
    token = comp.EOF_TOKEN
    expected = {
        'type_': 'EOF',
        'value': 'EOF',
    }
    assert token.asdict == expected
