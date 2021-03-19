from abc import ABC, abstractmethod
from typing import Any
from token import Token 
from function_type import FunctionType
from var_state import VarState

class Expr:
    pass

class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor) -> str:
        return visitor.visit_assign_expr(self)

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token,  right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_binary_expr(self)

class Conditional(Expr):
    def __init__(self, condition: Expr, then_branch: Expr, else_branch: Expr):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor) -> str:
        return visitor.visit_conditional_expr(self)

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

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_logical_expr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor) -> str:
        return visitor.visit_unary_expr(self)

class Variable(Expr):
    def __init__(self, name: Token, state=VarState.READ):
        self.name = name
        self.state = state

    def accept(self, visitor) -> str:
        return visitor.visit_variable_expr(self)

class Function(Expr):
    def __init__(self, params: list[Token], body: list[Any], type_: FunctionType):
        self.params = params
        self.body = body
        self.type_ = type_

    def accept(self, visitor) -> str:
        return visitor.visit_function_expr(self)

class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, args: list[Expr]):
        self.callee = callee
        self.paren = paren
        self.args = args

    def accept(self, visitor) -> str:
        return visitor.visit_call_expr(self)

class Get(Expr):
    def __init__(self, obj: Expr, name: Token):
        self.obj = obj
        self.name = name
    
    def accept(self, visitor) -> str:
        return visitor.visit_get_expr(self)

class Set(Expr):
    def __init__(self, obj: Expr, name: Token, value: Expr):
        self.obj = obj
        self.name = name
        self.value = value
    
    def accept(self, visitor) -> str:
        return visitor.visit_set_expr(self)

class This(Expr):
    def __init__(self, keyword: Token):
        self.keyword = keyword
    
    def accept(self, visitor) -> str:
        return visitor.visit_this_expr(self)