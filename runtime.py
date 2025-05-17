from ast_nodes import *

class RuntimeError(Exception):
    pass
import os
from lexer import Lexer
from parser import Parser

class Executor:
    ...

    def exec_ImportStatement(self, node, env):
        filename = node.module_name
        if not filename.endswith(".iji"):
            filename += ".iji"
        if not os.path.exists(filename):
            raise RuntimeError(f"Import failed: File '{filename}' not found")

        # Load and parse the imported file
        with open(filename, "r") as f:
            source = f.read()

        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()

        # Execute in its own environment
        import_env = Environment(parent=env)
        self.execute(ast, import_env)

        # Optionally: copy public symbols into current env
        for name, value in import_env.vars.items():
            if not name.startswith("_"):  # convention: underscore = private
                env.define(name, value)


class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def define(self, name, value):
        self.vars[name] = value

    def assign(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise RuntimeError(f"Undefined variable '{name}'")

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise RuntimeError(f"Undefined variable '{name}'")


class Executor:
    def __init__(self):
        self.global_env = Environment()
        self.functions = {}
        self._register_builtins()

    def execute(self, node, env=None):
        method_name = f"exec_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_exec)
        return method(node, env or self.global_env)

    def generic_exec(self, node, env):
        raise RuntimeError(f"No exec method for {type(node).__name__}")

    def exec_Program(self, node, env):
        result = None
        for stmt in node.statements:
            result = self.execute(stmt, env)
        return result

    def exec_ImportStatement(self, node, env):
        # Optional: implement import execution here
        pass

    def exec_FunctionDef(self, node, env):
        self.functions[node.name] = (node.params, node.body)

    def exec_ReturnStatement(self, node, env):
        value = self.eval_expr(node.value, env)
        raise ReturnSignal(value)

    def exec_VariableDeclaration(self, node, env):
        value = self.eval_expr(node.initializer, env)
        env.define(node.name, value)

    def exec_Assignment(self, node, env):
        value = self.eval_expr(node.value, env)
        env.assign(node.name, value)

    def exec_IfStatement(self, node, env):
        cond = self.eval_expr(node.condition, env)
        if cond:
            for stmt in node.then_body:
                self.execute(stmt, env)
        else:
            for stmt in node.else_body:
                self.execute(stmt, env)

    def exec_WhileLoop(self, node, env):
        while self.eval_expr(node.condition, env):
            for stmt in node.body:
                self.execute(stmt, env)

    def exec_FunctionCall(self, node, env):
        return self.eval_expr(node, env)

    def eval_expr(self, expr, env):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, VariableReference):
            return env.get(expr.name)
        elif isinstance(expr, BinaryOperation):
            left = self.eval_expr(expr.left, env)
            right = self.eval_expr(expr.right, env)
            return self.apply_operator(expr.operator, left, right)
        elif isinstance(expr, FunctionCall):
            if expr.name == "print":
                args = [self.eval_expr(arg, env) for arg in expr.args]
                print(*args)
                return None
            elif expr.name == "input":
                prompt = self.eval_expr(expr.args[0], env)
                return input(prompt)
            elif expr.name in self.functions:
                params, body = self.functions[expr.name]
                new_env = Environment(parent=env)
                for (typ, name), arg in zip(params, expr.args):
                    new_env.define(name, self.eval_expr(arg, env))
                try:
                    for stmt in body:
                        self.execute(stmt, new_env)
                except ReturnSignal as rs:
                    return rs.value
                return None
            else:
                raise RuntimeError(f"Unknown function '{expr.name}'")
        else:
            raise RuntimeError(f"Unsupported expression type: {type(expr).__name__}")

    def apply_operator(self, op, left, right):
        if op == "+": return left + right
        if op == "-": return left - right
        if op == "*": return left * right
        if op == "/": return left / right
        if op == "==": return left == right
        if op == "!=": return left != right
        if op == "<": return left < right
        if op == "<=": return left <= right
        if op == ">": return left > right
        if op == ">=": return left >= right
        raise RuntimeError(f"Unknown operator '{op}'")

    def _register_builtins(self):
        self.global_env.define("true", True)
        self.global_env.define("false", False)


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value
