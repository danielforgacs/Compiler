import CompilerSrc.tokeniser as tok



class ASTNodeBase(tok.DictSerialiseBase):
    pass


class BinOpNode(ASTNodeBase):
    def __init__(self, node_l, operator, node_r):
        self.node_l = node_l
        self.operator = operator
        self.node_r = node_r


class UnaryOpNode(ASTNodeBase):
    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression


class NumNode(ASTNodeBase):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class CompoundNode(ASTNodeBase):
    def __init__(self):
        self.children = ()


class AssignNode(ASTNodeBase):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class VariableNode(ASTNodeBase, tok.DictSerialiseBase):
    def __init__(self, name):
        self.name = name


class NoOpNode(ASTNodeBase):
    pass
