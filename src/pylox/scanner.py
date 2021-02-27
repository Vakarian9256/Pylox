import sys
import decimal
from token import Token
from token_type import TokenType as TT
from error_handler import ErrorHandler
from collections import namedtuple

DoubleToken = namedtuple("DoubleSingle", "single, double")


class Scanner:
    def __init__(self, error_handler: ErrorHandler, source: str):
        self.source = source
        self.error_handler = error_handler
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 1

        self.keywords = { 
            "and" : TT.AND,
            "class" : TT.CLASS,
            "else" : TT.ELSE,
            "false" : TT.FALSE,
            "for" : TT.FALSE,
            "fun" : TT.FUN,
            "if" : TT.IF,
            "nil" : TT.NIL,
            "or" : TT.OR,
            "print" : TT.PRINT,
            "return" : TT.RETURN,
            "super" : TT.SUPER,
            "this" : TT.THIS,
            "true" : TT.TRUE,
            "var" : TT.VAR,
            "while" : TT.WHILE
            }

        self.double_keys = {
            "!" : DoubleToken(TT.BANG, TT.BANG_EQUAL),
            "=" : DoubleToken(TT.EQUAL, TT.EQUAL_EQUAL),
            "<" : DoubleToken(TT.LESS, TT.LESS_EQUAL),
            ">" : DoubleToken(TT.GREATER, TT.GREATER_EQUAL)
            }

        self.single_keys = {
            "(" : TT.LEFT_PAREN,
            ")" : TT.RIGHT_PAREN,
            "{" : TT.LEFT_BRACE,
            "}" : TT.RIGHT_BRACE,
            "," : TT.COMMA,
            "." : TT.DOT,
            "-" : TT.MINUS,
            "+" : TT.PLUS,
            ";" : TT.SEMICOLON,
            "*" : TT.STAR
            }
    
    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TT.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def scan_token(self):
        char = self.advance()
        if char in self.single_keys:
            self.add_token(self.single_keys.get(char))
        elif char in self.double_keys:
            if(self.match('=')):
                self.add_token(self.double_keys[char].double)
            else:
                self.add_token(self.double_keys[char].single)
        elif char == '/':
            if self.peek() == '*':
                self.skip_comment()
            elif self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TT.SLASH)
        elif char == '?':
            self.add_conditional()
        elif char in ['', '\r', '\t', ' ']:
            pass
        elif char == '\n':
            self.line += 1
        elif char =='"':
            self.string()
        elif self.is_digit(char):
            self.number()
        elif self.is_alpha(char):
            self.identifier()
        else:
            self.error_handler.error(self.line, "Unexpected character.")

    def advance(self) -> chr:
        char = self.peek()
        self.current += 1
        return char
    
    def add_token(self, type_: TT, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type_, text, literal, self.line))

    def match(self, expected: chr) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True
    
    def peek(self) -> chr:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        if self.is_at_end():
            self.error_handler.error(line, "Unterminated String.")
            return None
        self.advance()
        value = self.source[self.start+1:self.current-1]
        self.add_token(TT.STRING, value)

    def is_digit(self, char: chr ) -> bool:
        return char >= '0' and char <= '9'

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        self.add_token(TT.NUMBER, decimal.Decimal(self.source[self.start:self.current]))

    def peek_next(self) -> chr:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current+1]
    
    def is_alpha(self, char: chr) -> chr:
        return (char >= 'a' and char <= 'z') or (char >='A' and char <= 'Z') or char == '_'
    
    def is_alpha_numeric(self,char: chr) -> chr:
        return self.is_digit(char) or self.is_alpha(char)

    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()
        
        text = self.source[self.start:self.current]
        type_ = TT.IDENTIFIER
        if text in self.keywords:
            type_ = self.keywords[text]
        self.add_token(type_)
    
    def skip_comment(self):
        comment_lines =[self.line]
        nesting = 1
        while nesting > 0:
            if self.is_at_end():
                for line in comment_lines:
                    self.error_handler.error(line, "Unterminated comment block.")
                return
            if self.peek() == '\n':
                self.line += 1
            if self.peek() == '/' and self.peek_next() == '*':
                comment_lines.append(self.line)
                nesting += 1
            if self.peek() =='*' and self.peek_next() =='/':
                nesting -= 1
                self.advance()
                self.advance()
            self.advance()

    def add_conditional(self):
        self.add_token(TT.QUESTION)
        while not self.match(':'):
            if self.is_at_end():
                self.error_handler.error(self.line, " Expect ':' seperator after then branch in ternary conditional.")
                return
            self.start = self.current
            self.scan_token()
        self.current -= 1
        self.add_token(TT.COLON)
        self.advance()
            
        
        
    
    

    
