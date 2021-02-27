import sys
from token_type import TokenType as TT
from token import Token
from expr import *
from error_handler import ErrorHandler

class Parser:

    class ParseError(RuntimeError):
        def __init__(self, message):
            super().__init__(message)

    def __init__(self, tokens: list[Token], error_handler: ErrorHandler):
        self.tokens = tokens
        self.error_handler = error_handler
        self.current = 0    
    
    def parse(self) -> Expr:
        try:
            return self.expression()
        except Parser.ParseError:
            return None


    def expression(self) -> Expr:
        return self.comma_op()

    ''' In C, the comma operator has the lowest precedence,
     and therefore it will be the first "level" in the descent
     '''
    def comma_op(self) -> Expr:
        expr = self.conditional()
        while self.match(TT.COMMA):
            operator = self.previous()
            right = self.conditional()
            expr = Binary(expr, operator, right)
        return expr

    def conditional(self) -> Expr:
        expr = self.equality()
        if self.match(TT.QUESTION):
            then_branch = self.equality()
            self.consume(TT.COLON, " Expect ':' seperator after then branch in ternary conditional.")
            else_branch = self.equality()
            expr = Conditional(expr, then_branch, else_branch)
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match(TT.BANG_EQUAL, TT.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr = self.term()
        while self.match(TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self.match(TT.PLUS, TT.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr
    
    def factor(self) -> Expr:
        expr = self.unary()
        while self.match(TT.SLASH, TT.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        if self.match(TT.BANG, TT.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()

    def primary(self) -> Expr:
        if self.match(TT.TRUE):
            return Literal(True)
        if self.match(TT.FALSE):
            return Literal(False)
        if self.match(TT.NIL):
            return Literal(None)
        if self.match(TT.NUMBER, TT.STRING):
            return Literal(self.previous().literal)
        if self.match(TT.LEFT_PAREN):
            expr = self.expression()
            self.consume(TT.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        # The following if clauses are productions for missing left operands - "error productions"
        if self.match(TT.COMMA):
            self.error(self.previous(), "Missing left-hand operand.")
            self.comma_op()
            return None
        if self.match(TT.BANG_EQUAL, TT.EQUAL_EQUAL):
            self.error(self.previous(), "Missing left-hand operand.")
            self.equality()
            return None
        if self.match(TT.QUESTION):
            self.error(self.previous(), "Missing condition expression for ternary conditional.")
            self.conditional()
            return None
        if self.match(TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL):
            self.error(self.previous(), "Missing left-hand operand.")
            self.comparison()
            return None
        if self.match(TT.PLUS):
            self.error(self.previous(), "Missing left-hand operand.")
            self.term()
            return None
        if self.match(TT.SLASH, TT.STAR):
            self.error(self.previous(), "Missing left-hand operand.")
            self.factor()
            return None
        self.error_handler.error_on_token(self.peek(), "Expect expression.")

    def match(self, *types) -> bool:
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False
    
    def check(self, type_: TT) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type_ == type_
    
    def is_at_end(self) -> bool:
        return self.peek().type_ == TT.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self) -> Token:
        return self.tokens[self.current-1]
    
    def consume(self, type_: TT, message: str) -> Token:
        if self.check(type_):
            return self.advance()
        self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        self.error_handler.error_on_token(token, message)
        return Parser.ParseError("")

    def synchronize(self):
        self.advance()
        keywords = {TT.CLASS, TT.FUN, TT.VAR, TT.FOR, TT.IF, TT.WHILE,  TT.PRINT, TT.RETURN}
        while not self.is_at_end():
            if self.previous().type_ == TT.SEMICOLON:
                return
            if self.peek().type_ in keywords:
                return
            self.advance()