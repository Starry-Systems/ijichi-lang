class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements  # list of ASTNode


class ImportStatement(ASTNode):
    def __init__(self, path):
        self.path = path  # string


class FunctionDef(ASTNode):
    def __init__(self, name, params, body):
        self.name = name  # str
        self.params = params  # list of (type, name) tuples
        self.body = body  # list of ASTNode


class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value  # Expression


class VariableDeclaration(ASTNode):
    def __init__(self, var_type, name, initializer):
        self.var_type = var_type  # str
        self.name = name  # str
        self.initializer = initializer  # Expression


class Assignment(ASTNode):
    def __init__(self, name, value):
        self.name = name  # str
        self.value = value  # Expression


class IfStatement(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition  # Expression
        self.then_body = then_body  # list of ASTNode
        self.else_body = else_body or []  # list of ASTNode


class WhileLoop(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition  # Expression
        self.body = body  # list of ASTNode


class BinaryOperation(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left  # Expression
        self.operator = operator  # str
        self.right = right  # Expression


class Literal(ASTNode):
    def __init__(self, value):
        self.value = value


class VariableReference(ASTNode):
    def __init__(self, name):
        self.name = name  # str


class FunctionCall(ASTNode):
    def __init__(self, name, args):
        self.name = name  # str
        self.args = args  # list of Expression
