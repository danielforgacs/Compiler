import CompilerSrc.tokeniser as tok
import CompilerSrc.astnodes as astn



def factor(tokens):
    token, tokens = tok.pop_next_token(tokens)

    if token.type_ == tok.INT_CONST:
        node = astn.NumNode(token)

    elif token == tok.PAREN_L_TOKEN:
        tokens, node = expression(tokens)
        paren_r, tokens = tok.pop_next_token(tokens)
        assert paren_r == tok.PAREN_R_TOKEN, f'[factor] expected: {tok.PAREN_R_TOKEN} got: {paren_r}'

    elif token in [tok.MINUS_TOKEN, tok.PLUS_TOKEN]:
        tokens, node = factor(tokens)
        node = astn.UnaryOpNode(token, node)

    elif token.type_ == 'ID':
        tokens = tok.put_back_token(token, tokens)
        tokens, node = do_variable(tokens)

    else:
        raise Exception(f'[factor] Unecpeted token: {token}')

    return tokens, node


def term(tokens):
    tokens, node = factor(tokens)

    while tok.nexttoken(tokens) in (tok.MULT_TOKEN, tok.DIV_TOKEN):
        operator, tokens = tok.pop_next_token(tokens)
        tokens, node_r = factor(tokens)
        node = astn.BinOpNode(node, operator, node_r)

    return tokens, node


def expression(tokens):
    tokens, node = term(tokens)

    while tok.nexttoken(tokens) in (tok.PLUS_TOKEN, tok.MINUS_TOKEN):
        operator, tokens = tok.pop_next_token(tokens)
        tokens, node_r = term(tokens)
        node = astn.BinOpNode(node, operator, node_r)

    return tokens, node






def program(tokens):
    tokens, node = compound_statement(tokens)

    token, tokens = tok.pop_next_token(tokens)
    assert token == tok.DOT_TOKEN, f'[Program] expected: {tok.DOT_TOKEN} got: {token}'

    token, tokens = tok.pop_next_token(tokens)
    assert token == tok.EOF_TOKEN, f'[Program] expected: {tok.EOF_TOKEN} got: {token}'

    return tokens, node



def compound_statement(tokens):
    token, tokens = tok.pop_next_token(tokens)
    assert token == tok.BEGIN_TOKEN, f'[compound_statement] expected: {tok.BEGIN_TOKEN} got: {token}'

    node = astn.CompoundNode()
    tokens, node.children = statement_list(tokens)

    token, tokens = tok.pop_next_token(tokens)
    assert token == tok.END_TOKEN, f'[compound_statement] expected: {tok.END_TOKEN} got: {token}'

    return tokens, node



def statement_list(tokens):
    tokens, node = statement(tokens)
    nodelist = [node]

    while tok.nexttoken(tokens) == tok.SEMI_TOKEN:
        _, tokens = tok.pop_next_token(tokens)
        tokens, node = statement(tokens)
        nodelist += [node]

    return tokens, nodelist



def statement(tokens):
    if tok.nexttoken(tokens) == tok.BEGIN_TOKEN:
        tokens, node = compound_statement(tokens)
    elif tok.nexttoken(tokens).type_ == tok.ID:
        tokens, node = assign_statement(tokens)
    else:
        node = astn.NoOpNode()

    return tokens, node



def assign_statement(tokens):
    tokens, varnode = do_variable(tokens)
    assigntoken, tokens = tok.pop_next_token(tokens)
    assert assigntoken == tok.ASSIGN_TOKEN, (f'[assign_statement] expected:'
        f' {tok.ASSIGN_TOKEN} got: {assigntoken}')
    tokens, expressionnode = expression(tokens)
    node = astn.AssignNode(varnode, assigntoken, expressionnode)
    return tokens, node



def do_variable(tokens):
    token, tokens = tok.pop_next_token(tokens)
    assert token.type_ == tok.ID, f'[do_variable] expected: {tok.ID}, got: {token}'
    node = astn.VariableNode(token)

    return tokens, node



def get_block(tokens):
    declaration_nodes = get_declarations(tokens)
    compound_statement_node = get_compound_statement(tokens)
    node = astn.BlockNode(declaration_nodes, compound_statement_node)

    return tokens, node


def get_declarations(tokens):
    declarations = []



def get_compound_statement(tokens):
    pass



class NodeVisitor:
    GLOBAL_SCOPE = {}


    def dispatch_visit(self, node):
        nodeclassname = node.__class__.__name__
        visitormethodname = 'visit_{}'.format(nodeclassname)
        if not hasattr(self, visitormethodname):
            raise Exception(f'[NodeVisitor] Unknown node to visit: {nodeclassname}')
        visitormethod = getattr(self, visitormethodname)
        return visitormethod(node)

    def visit_NumNode(self, node):
        return node.value

    def visit_UnaryOpNode(self, node):
        if node.operator == tok.PLUS_TOKEN:
            return self.dispatch_visit(node.expression)
        elif node.operator == tok.MINUS_TOKEN:
            return self.dispatch_visit(node.expression) * -1
        else:
            raise Exception(f'[visit_UnaryOp] Bad unary op operator: {node.operator}')

    def visit_BinOpNode(self, node):
        if node.operator == tok.PLUS_TOKEN:
            return self.dispatch_visit(node.node_l) + self.dispatch_visit(node.node_r)
        elif node.operator == tok.MINUS_TOKEN:
            return self.dispatch_visit(node.node_l) - self.dispatch_visit(node.node_r)
        elif node.operator == tok.MULT_TOKEN:
            return self.dispatch_visit(node.node_l) * self.dispatch_visit(node.node_r)
        elif node.operator == tok.DIV_TOKEN:
            return self.dispatch_visit(node.node_l) / self.dispatch_visit(node.node_r)
        else:
            raise Exception(f'[visit_BinOp Unexpected BinOp node: {node.operator}')

    def visit_CompoundNode(self, node):
        for child in node.children:
            self.dispatch_visit(child)

    def visit_AssignNode(self, node):
        self.GLOBAL_SCOPE[node.left.name.value] = self.dispatch_visit(node.right)

    def visit_VariableNode(self, node):
        return self.GLOBAL_SCOPE[node.name.value]

    def visit_NoOpNode(self, node):
        pass


def run(source):
    tokens = tok.tokenise(source)
    _, node = expression(tokens)

    return NodeVisitor().dispatch_visit(node)


def run_program(source):
    tokens = tok.tokenise(source)
    _, node = program(tokens)

    nodevisitor =  NodeVisitor()
    result = nodevisitor.dispatch_visit(node)

    return result





if __name__ == '__main__':
    source = """
BEGIN
    x := 123;
END.
"""
    # run_program(source=source)
    import json
    tokens = tokenise(source)
    print(tokens)
    _, node = program(tokens)
    print(node.asdict)
    print(json.dumps(node.asdict, indent=4))
