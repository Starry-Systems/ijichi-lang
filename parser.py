class Parser:
    PRECEDENCE = {
        'or': 1,
        'and': 2,
        '==': 3, '!=': 3, '<': 3, '<=': 3, '>': 3, '>=': 3,
        '+': 4, '-': 4,
        '*': 5, '/': 5,
    }
def parse_list_literal(self):
    # assumes current token is '['
    elements = []
    self.advance()  # consume '['
    while self.current_token.type != 'RIGHT_BRACKET':
        elements.append(self.parse_expression())
        if self.current_token.type == 'COMMA':
            self.advance()
        else:
            break
    self.expect('RIGHT_BRACKET')
    return ListLiteralNode(elements)
    
def parse_index_access(self, base_expr):
    while self.current_token.type == 'LEFT_BRACKET':
        self.advance()
        index_expr = self.parse_expression()
        self.expect('RIGHT_BRACKET')
        base_expr = IndexAccessNode(base_expr, index_expr)
    return base_expr


def parse_dict_literal(self):
    # assumes current token is '{'
    pairs = []
    self.advance()  # consume '{'
    while self.current_token.type != 'RIGHT_BRACE':
        key = self.parse_expression()
        self.expect('COLON')
        value = self.parse_expression()
        pairs.append((key, value))
        if self.current_token.type == 'COMMA':
            self.advance()
        else:
            break
    self.expect('RIGHT_BRACE')
    return DictLiteralNode(pairs)


    UNARY_OPS = {'-', 'not', '!'}

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        self.errors = []
        self.advance()

    def advance(self):
        self.current_token = self.lexer.next_token()

    def expect(self, token_type):
        if self.current_token.type != token_type:
            raise SyntaxError(f'Expected {token_type}, got {self.current_token.type}')
        self.advance()

    def parse(self):
        statements = []
        while self.current_token.type != 'EOF':
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except SyntaxError as e:
                self.errors.append(str(e))
                self.synchronize()
        return Program(statements)

    def synchronize(self):
        # Basic error recovery:
        # skip tokens until we find one that can start a statement
        sync_tokens = {'FUNC', 'IF', 'WHILE', 'RETURN', 'ID', 'DEDENT', 'EOF'}
        while self.current_token.type not in sync_tokens:
            self.advance()

    def parse_statement(self):
        t = self.current_token.type

        if t == 'FUNC':
            return self.parse_function()
        elif t == 'IF':
            return self.parse_if()
        elif t == 'WHILE':
            return self.parse_while()
        elif t == 'RETURN':
            self.advance()
            expr = self.parse_expression()
            return ReturnStmt(expr)
        else:
            expr = self.parse_expression()
            return ExprStmt(expr)

    def parse_expression(self, precedence=0):
        token = self.current_token

        # Unary operator
        if token.type == 'OP' and token.value in self.UNARY_OPS:
            op = token.value
            self.advance()
            right = self.parse_expression(self.PRECEDENCE.get(op, 6))
            return UnaryOp(op, right)
        elif token.type == 'KEYWORD' and token.value == 'not':
            op = token.value
            self.advance()
            right = self.parse_expression(self.PRECEDENCE.get(op, 6))
            return UnaryOp(op, right)

        # Primary expressions: literals, variables, parenthesis, function calls
        if token.type in ('INT', 'FLOAT', 'STRING', 'BOOL'):
            self.advance()
            left = Literal(token.value)
        elif token.type == 'ID':
            self.advance()
            left = Variable(token.value)
            # Possible function call
            if self.current_token.type == 'LPAREN':
                left = self.parse_call(left)
        elif token.type == 'LPAREN':
            self.advance()
            left = self.parse_expression()
            self.expect('RPAREN')
        else:
            raise SyntaxError(f"Unexpected token in expression: {token.type}")

        # Binary operators using precedence climbing
        while True:
            tok = self.current_token
            if tok.type == 'OP' or (tok.type == 'KEYWORD' and tok.value in ('and', 'or')):
                op_val = tok.value
                op_prec = self.PRECEDENCE.get(op_val, 0)
                if op_prec <= precedence:
                    break
                self.advance()
                right = self.parse_expression(op_prec)
                left = BinaryOp(left, op_val, right)
            else:
                break

        return left

    def parse_call(self, func_expr):
        self.expect('LPAREN')
        args = []
        if self.current_token.type != 'RPAREN':
            while True:
                arg = self.parse_expression()
                args.append(arg)
                if self.current_token.type == 'COMMA':
                    self.advance()
                else:
                    break
        self.expect('RPAREN')
        return CallExpr(func_expr.name, args)


# AST node for UnaryOp
class UnaryOp:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
