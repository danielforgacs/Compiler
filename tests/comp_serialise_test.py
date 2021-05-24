import CompilerSrc.comp as comp


def test_Token_serialise():
    token = comp.EOF_TOKEN
    expected = {
        'type_': 'EOF',
        'value': 'EOF',
    }
    assert token.asdict == expected



def test_Token_de_serialise():
    data = {
        'type_': 'EOF',
        'value': 'EOF',
    }
    token = comp.Token.from_dict(data=data)
    assert token == comp.EOF_TOKEN
