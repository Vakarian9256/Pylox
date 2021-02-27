from abc import ABC, abstractmethod
from typing import Any
from token import Token 

class Expr:
    pass

class Asign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor) -> str:
        return visitor.visit_asign_expr(self)

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token,  right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_binary_expr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor) -> str:
        return visitor.visit_grouping_expr(self)

class Literal(Expr):
    def __init__(self, value: Any):
        self.value = value

    def accept(self, visitor) -> str:
        return visitor.visit_literal_expr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_unary_expr(self)

class Conditional(Expr):
    def __init__(self, condition: Expr, left: Expr, right: Expr):
        self.condition = condition
        self.left = left
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_conditional_expr(self)

class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor) -> str:
        return visitor.visit_variable_expr(self)

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_logical_expr(self)

