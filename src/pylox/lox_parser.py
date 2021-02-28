import sys
from token_type import TokenType as TT
from token import Token
from expr import *
from error_handler import ErrorHandler
from stmt import *

class Parser:

    class ParseError(RuntimeError):
        def __init__(self, message):
            super().__init__(message)

    def __init__(self, tokens: list[Token], error_handler: ErrorHandler):
        self.tokens = tokens
        self.error_handler = error_handler
        self.current = 0    
        self.loop_depth = 0
    
    def parse(self) -> list[Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self) -> Stmt:
        try:
            if self.match(TT.VAR):
                return self.var_declaration()
            elif self.match(TT.FUN):
                return self.function("function")
            return self.statement()
        except Parser.ParseError as error:
            self.synchronize()
            return None
    
    def var_declaration(self) -> Stmt:
        name = self.consume(TT.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TT.EQUAL):
            initializer = self.expression()
        self.consume(TT.SEMICOLON, "Expect semicolon after variable declaration.")
        return Var(name, initializer)

    def function(self, kind: str) -> Stmt:
        name = self.consume(TT.IDENTIFIER,f"Expect {kind} name.")
        self.consume(TT.LEFT_PAREN,f"Expect '(' after {kind} name.")
        params = []
        if not self.check(TT.RIGHT_PAREN):
            while True:
                if len(params) >= 255:
                    self.error(self.peek(),"Can't have more than 255 parameters.")
                params.append(self.consume(TT.IDENTIFIER,"Expect parameter name."))
                if not self.match(TT.COMMA):
                    break
        self.consume(TT.RIGHT_PAREN,"Expect ')' after parameters.")
        self.consume(TT.LEFT_BRACE,"Expect '{ before " + kind + " body.")
        body = self.block_statement()
        return Fun(name, params, body)

    def statement(self) -> Stmt:
        if self.match(TT.IF):
            return self.if_statement()
        if self.match(TT.WHILE):
            return self.while_statement()
        if self.match(TT.FOR):
            return self.for_statement()
        if self.match(TT.BREAK):
            return self.break_statement()
        if self.match(TT.PRINT):
            return self.print_statement()
        if self.match(TT.RETURN):
            return self.return_statement()
        if self.match(TT.LEFT_BRACE):
            return Block(self.block_statement())
        return self.expression_statement()

    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def block_statement(self) -> list[Stmt]:
        statements = []
        while (not self.check(TT.RIGHT_BRACE)) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TT.RIGHT_BRACE,"Expect '}' after block.")
        return statements
        
    def expression_statement(self) -> Expression:
        expr = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)

    def if_statement(self) -> If:
        self.consume(TT.LEFT_PAREN,"Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TT.RIGHT_PAREN,"Expect ')' after 'if' condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TT.ELSE):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)
    
    def while_statement(self) -> While:
        self.consume(TT.LEFT_PAREN,"Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TT.RIGHT_PAREN,"Expect ')' after 'while'")
        try:
            self.loop_depth += 1
            body = self.statement()
            return While(condition, body)
        finally:
            self.loop_depth -= 1

    def for_statement(self) -> Stmt:
        self.consume(TT.LEFT_PAREN,"Expect '(' after 'for'.")
        initializer = None
        if self.match(TT.VAR):
            initializer = self.var_declaration()
        elif not self.match(TT.SEMICOLON):
            initializer = self.expression_statement()
        condition = None
        if not self.check(TT.SEMICOLON):
            condition = self.expression()
        self.consume(TT.SEMICOLON,"Expect ';' after 'for' condition.")
        increment = None
        if not self.check(TT.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TT.RIGHT_PAREN,"Expect ')' after 'for' clauses.")
        try:
            self.loop_depth += 1
            body = self.statement()
            if increment is not None:
                body = Block([body, Expression(increment)])
            if condition is None:
                condition = Literal(True)
            body = While(condition, body)
            if initializer is not None:
                body = Block([initializer, body])
                return body 
        finally:
            self.loop_depth -= 1
        
    def break_statement(self) -> Break:
        if self.loop_depth == 0:
            self.error(self.previous(), "Must be inside loop to use 'break'.")
        self.consume(TT.SEMICOLON,"Expect ';' after break.")
        return Break()

    def return_statement(self) -> Return:
        keyword = self.previous()
        value = None
        if not self.check(TT.SEMICOLON):
            value = self.expression()
        self.consume(TT.SEMICOLON,"Expect ';' after return value.")
        return Return(keyword,value)

    def expression(self) -> Expr:
        return self.comma_op()

    ''' In C, the comma operator has the lowest precedence,
     and therefore it will be the first "level" in the descent
     '''
    def comma_op(self) -> Expr:
        expr = self.assignment()
        while self.match(TT.COMMA):
            operator = self.previous()
            right = self.assignment()
            expr = Binary(expr, operator, right)
        return expr

    def assignment(self) -> Expr:
        expr = self.conditional()
        if self.match(TT.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if type(expr) is Variable:
                name = expr.name
                return Asign(name, value)
            self.error(equals, "Invalid assignment target.")
        return expr


    def conditional(self) -> Expr:
        expr = self.or_expr()
        if self.match(TT.QUESTION):
            then_branch = self.or_expr()
            self.consume(TT.COLON, " Expect ':' seperator after then branch in ternary conditional.")
            else_branch = self.or_expr()
            expr = Conditional(expr, then_branch, else_branch)
        return expr

    def or_expr(self) -> Expr:
        expr = self.and_expr()
        while self.match(TT.OR):
            operator = self.previous()
            right = self.and_expr()
            expr = Logical(expr, operator, right)
        return expr

    def and_expr(self) -> Expr:
        expr = self.equality()
        while self.match(TT.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
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
        return self.call()

    def call(self) -> Expr:
        expr = self.primary()
        while True:
            if self.match(TT.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break   
        return expr

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
        if self.match(TT.IDENTIFIER):
            return Variable(self.previous())
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

    def finish_call(self, callee: Call) -> Expr:
        arguments = []
        if not self.check(TT.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Cant have more than 255 arguments. ")
                arguments.append(self.conditional())
                if not self.match(TT.COMMA):
                    break
        paren = self.consume(TT.RIGHT_PAREN,"Expect ')' after arguments.")
        return Call(callee, paren, arguments)
        


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
