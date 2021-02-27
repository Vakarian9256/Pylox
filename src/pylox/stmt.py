from abc import ABC, abstractmethod
from expr import Expr
from token import Token 

class Stmt:
    pass

class Expression(Stmt):
    def __init__(self, expr: Expr):
        self.expr = expr

    def accept(self, visitor) -> str:
        return visitor.visit_expression_stmt(self)

class Print(Stmt):
    def __init__(self, expr: Expr):
        self.expr = expr

    def accept(self, visitor) -> str:
        return visitor.visit_print_stmt(self)

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor) -> str:
        return visitor.visit_var_stmt(self)

class Block(Stmt):
    def __init__(self, statements: list[Stmt]):
        self.statements = statements

    def accept(self, visitor) -> str:
        return visitor.visit_block_stmt(self)

