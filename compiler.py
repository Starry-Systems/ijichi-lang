# compiler.py

# === AST Node Classes ===
class Program:
    def __init__(self, statements):
        self.statements = statements

class Function:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params  # list of (type, name) tuples
        self.body = body

class VarDecl:
    def __init__(self, name, type_, expr):
        self.name = name
        self.type_ = type_
        self.expr = expr

class ReturnStmt:
    def __init__(self, expr):
        self.expr = expr

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class CallExpr:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Literal:
    def __init__(self, value):
        self.value = value

class Variable:
    def __init__(self, name):
        self.name = name


# === Compiler Class with Error Handling ===
class CompileError(Exception):
    pass

class Compiler:
    def __init__(self):
        self.instructions = []
        self.constants = []
        self.functions = {}
        self.var_indices = {}
        self.local_count = 0
        self.current_func = None

    def compile(self, node):
        try:
            if isinstance(node, Program):
                for stmt in node.statements:
                    self.compile(stmt)
            elif isinstance(node, Function):
                if node.name in self.functions:
                    raise CompileError(f"Function '{node.name}' already defined")
                self.functions[node.name] = len(self.instructions)
                self.current_func = node.name
                self.var_indices = {name: idx for idx, (typ, name) in enumerate(node.params)}
                self.local_count = len(node.params)
                for stmt in node.body:
                    self.compile(stmt)
                self.emit("LOAD_CONST", self.add_constant(None))
                self.emit("RETURN_VALUE")
                self.current_func = None
                self.var_indices = {}
                self.local_count = 0
            elif isinstance(node, VarDecl):
                if node.name in self.var_indices:
                    raise CompileError(f"Variable '{node.name}' already declared")
                self.compile(node.expr)
                idx = self.local_count
                self.var_indices[node.name] = idx
                self.local_count += 1
                self.emit("STORE_VAR", idx)
            elif isinstance(node, ReturnStmt):
                self.compile(node.expr)
                self.emit("RETURN_VALUE")
            elif isinstance(node, BinaryOp):
                self.compile(node.left)
                self.compile(node.right)
                if node.op == "+":
                    self.emit("BINARY_ADD")
                elif node.op == "-":
                    self.emit("BINARY_SUBTRACT")
                elif node.op == "*":
                    self.emit("BINARY_MULTIPLY")
                elif node.op == "/":
                    self.emit("BINARY_DIVIDE")
                else:
                    raise CompileError(f"Unknown binary operator '{node.op}'")
            elif isinstance(node, CallExpr):
                if node.name not in self.functions:
                    raise CompileError(f"Call to undefined function '{node.name}'")
                for arg in node.args:
                    self.compile(arg)
                self.emit("CALL_FUNCTION", node.name, len(node.args))
            elif isinstance(node, Literal):
                idx = self.add_constant(node.value)
                self.emit("LOAD_CONST", idx)
            elif isinstance(node, Variable):
                idx = self.var_indices.get(node.name)
                if idx is None:
                    raise CompileError(f"Undefined variable '{node.name}'")
                self.emit("LOAD_VAR", idx)
            else:
                raise CompileError(f"Unknown node type '{type(node).__name__}'")
        except CompileError:
            raise
        except Exception as e:
            raise CompileError(f"Compilation error: {e}")

    def emit(self, op, *args):
        self.instructions.append((op, *args))

    def add_constant(self, value):
        if value in self.constants:
            return self.constants.index(value)
        self.constants.append(value)
        return len(self.constants) - 1
