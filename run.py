from lexer.py import Lexer         
from parser.py import Parser       
from compiler.py import Compiler, Program  # Compiler and AST classes from compiler.py
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <source_file>")
        exit(1)

    with open(sys.argv[1], "r") as f:
        source = f.read()

    main(source)


def main(source_code):
    # Lexing
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()

    # Parsing
    parser = Parser(tokens)
    ast = parser.parse_program()  # returns a Program node

    # Compiling
    compiler = Compiler()
    compiler.compile(ast)

    # Run VM
    vm = VirtualMachine(compiler.instructions, compiler.constants, compiler.functions)
    vm.run()

if __name__ == "__main__":
    source = """
    func add(int a, int b)
        return a + b

    func main()
        int x = 5
        int y = 10
        print(add(x, y))

    main()
    """
    main(source)


