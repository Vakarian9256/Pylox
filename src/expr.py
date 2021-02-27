from abc import ABC, abstractmethod
from token import *
from typing import Any

class Expr:
    pass

class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token,  right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

class GroupingExpr(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor) -> str:
        return visitor.visit_grouping_expr(self)

class LiteralExpr(Expr):
    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor) -> str:
        return visitor.visit_literal_expr(self)

class UnaryExpr(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_unary_expr(self)   

class ConditionalExpr(Expr):
    def __init__(self, condition: Expr, then_branch: Expr, else_branch: Expr):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor) -> str:
        return visitor.visit_conditional_expr(self)


