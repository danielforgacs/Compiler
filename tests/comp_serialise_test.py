import CompilerSrc.astnodes as astn
import CompilerSrc.tokeniser as tok


def test_Token_serialise():
    token = tok.EOF_TOKEN
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
    token = tok.Token.from_dict(data=data)
    assert token == tok.EOF_TOKEN



def test_Variable_node_serialise():
    varname = 'varname'
    token = tok.Token(tok.ID, varname)
    variable = astn.VariableNode(name=token)
    expected = {
        'name.Token': {
            'type_': tok.ID,
            'value': varname,
        }
    }
    assert variable.asdict == expected
