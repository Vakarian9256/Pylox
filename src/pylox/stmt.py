from abc import ABC, abstractmethod
from expr import Expr

class Stmt:
    pass

class Expression(Stmt):
    def __init__(self, expr: Expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)

class Print(Stmt):
    def __init__(self, expr: Expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

