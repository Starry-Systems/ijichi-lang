import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

class LexerError(Exception):
    pass

class Lexer:
    KEYWORDS = {
        'func', 'if', 'else', 'while', 'return',
        'try', 'catch', 'raise', 'import', 'from', 'as'
    }
    BOOL_LITERALS = {'true', 'false'}

    TOKEN_SPECIFICATION = [
        ('TRIPLE_STRING', r'"""(?:.|\n)*?"""'),   # Multiline string (non-greedy)
        ('NUMBER',       r'\d+(\.\d*)?'),         # Integer or decimal number
        ('STRING',       r'"([^"\\]|\\.)*"'),     # Double quoted string
        ('ID',           r'[A-Za-z_][A-Za-z0-9_]*'),  # Identifiers
        ('OP',           r'==|!=|<=|>=|[+\-*/<>]'),  # Operators
        ('NEWLINE',      r'\n'),                   # Line endings
        ('SKIP',         r'[ \t]+'),               # Skip spaces and tabs
        ('COMMENT',      r'\#.*'),                  # Comments
        ('SEMICOLON',    r';'),                     # Semicolon separator
        ('LPAREN',       r'\('),
        ('RPAREN',       r'\)'),
        ('COMMA',        r','),
        ('COLON',        r':'),
        ('UNKNOWN',      r'.'), 
      
        LBRACKET = 'LEFT_BRACKET'   # [
        RBRACKET = 'RIGHT_BRACKET'  # ]
        LBRACE = 'LEFT_BRACE'       # {
        RBRACE = 'RIGHT_BRACE'      # }
        COLON = 'COLON'             # :
        COMMA = 'COMMA'             # ,
# Any other character
    ]
    

    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.indents = [0]
        self.line = 1
        self.column = 1
        self.regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKEN_SPECIFICATION), re.MULTILINE)
        self.current_pos = 0
        self.length = len(code)
        self.token_index = 0

    def tokenize(self):
        lines = self.code.splitlines(keepends=True)
        for line in lines:
            stripped = line.lstrip('\r\n')
            indent = len(line) - len(stripped)
            if stripped == '' or stripped.startswith('#'):
                self.line += 1
                self.column = 1
                continue
            
            if indent > self.indents[-1]:
                self.indents.append(indent)
                self.tokens.append(Token('INDENT', '', self.line, self.column))
            while indent < self.indents[-1]:
                self.indents.pop()
                self.tokens.append(Token('DEDENT', '', self.line, self.column))

            self._tokenize_line(stripped)
            self.line += 1
            self.column = 1

        while len(self.indents) > 1:
            self.indents.pop()
            self.tokens.append(Token('DEDENT', '', self.line, self.column))

        self.tokens.append(Token('EOF', '', self.line, self.column))
        return self.tokens

    def _tokenize_line(self, line):
        pos = 0
        while pos < len(line):
            match = self.regex.match(line, pos)
            if not match:
                raise LexerError(f'Unexpected character {line[pos]} at line {self.line} col {self.column}')
            kind = match.lastgroup
            value = match.group(kind)
            start_col = pos + 1

            if kind == 'NEWLINE':
                self.tokens.append(Token('NEWLINE', '', self.line, start_col))
            elif kind == 'SKIP':
                pass
            elif kind == 'COMMENT':
                # ignore comment till line end
                break
            elif kind == 'ID':
                lowered = value.lower()
                if lowered in self.KEYWORDS:
                    self.tokens.append(Token(lowered.upper(), value, self.line, start_col))
                elif lowered in self.BOOL_LITERALS:
                    self.tokens.append(Token('BOOL', lowered == 'true', self.line, start_col))
                else:
                    self.tokens.append(Token('ID', value, self.line, start_col))
            elif kind == 'STRING' or kind == 'TRIPLE_STRING':
                # Strip quotes and unescape
                if kind == 'STRING':
                    val = bytes(value[1:-1], "utf-8").decode("unicode_escape")
                else:
                    val = bytes(value[3:-3], "utf-8").decode("unicode_escape")
                self.tokens.append(Token('STRING', val, self.line, start_col))
            elif kind == 'NUMBER':
                if '.' in value:
                    self.tokens.append(Token('FLOAT', float(value), self.line, start_col))
                else:
                    self.tokens.append(Token('INT', int(value), self.line, start_col))
            elif kind == 'SEMICOLON':
                self.tokens.append(Token('SEMICOLON', value, self.line, start_col))
            elif kind == 'UNKNOWN':
                raise LexerError(f'Unknown token {value} at line {self.line} col {start_col}')
            else:
                self.tokens.append(Token(kind, value, self.line, start_col))
            pos = match.end()

    def peek(self):
        if self.token_index < len(self.tokens):
            return self.tokens[self.token_index]
        return None

    def next_token(self):
        if self.token_index < len(self.tokens):
            tok = self.tokens[self.token_index]
            self.token_index += 1
            return tok
        return None
