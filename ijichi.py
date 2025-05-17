import sys
from lexer import Lexer
from parser import Parser
from runtime import Executor

def run_file(path):
    with open(path, "r") as f:
        source = f.read()
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    executor = Executor()
    executor.execute(ast)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ijichi.py <script.iji>")
        sys.exit(1)
    run_file(sys.argv[1])
