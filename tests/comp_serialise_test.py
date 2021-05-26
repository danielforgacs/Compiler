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



def test_Variable_node_serialise():
    varname = 'varname'
    token = comp.Token(comp.ID, varname)
    variable = comp.Variable(name=token)
    expected = {
        'name.Token': {
            'type_': comp.ID,
            'value': varname,
        }
    }
    assert variable.asdict == expected
