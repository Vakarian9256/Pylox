import decimal
import sys
import operator
from visitor import Visitor
from expr import *
from token_type import TokenType as TT
from runtime_error import LoxRunTimeError
from error_handler import ErrorHandler

op_dic = {
    TT.LESS : operator.lt,
    TT.LESS_EQUAL: operator.le,
    TT.GREATER : operator.gt,
    TT.GREATER_EQUAL : operator.ge,
    TT.MINUS : operator.sub,
    TT.SLASH : operator.truediv,
    TT.STAR : operator.mul,
    TT.EQUAL_EQUAL : operator.eq,
    TT.BANG_EQUAL : operator.ne
    }

class Interpreter(Visitor):

    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler

    def interpret(self, expr: Expr):
        try:
            value =  self.evaluate(expr)
            print(self.stringify(value))
        except LoxRunTimeError as error:
            self.error_handler.runtime_error(error)


    def visit_literal_expr(self, expr: LiteralExpr):
        return expr.value

    def visit_grouping_expr(self, expr: GroupingExpr):
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: UnaryExpr):
        right = self.evaluate(expr.right)
        if expr.operator.type_ == TT.MINUS:
            return -decimal.Decimal(right)
        if expr.operator.type_ == TT.BANG:
            return not self.is_truth(right)

    def visit_binary_expr(self, expr: BinaryExpr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.type_ == TT.MINUS:
            self.check_number_operand(expr.operator, left, right)
            return decimal.Decimal(left) - decimal.Decimal(right)
        elif expr.operator.type_ == TT.STAR:
            return decimal.Decimal(left) * decimal.Decimal(right)
        elif expr.operator.type_ == TT.SLASH:
            if self.legal_divisor(expr.operator, right):
                return decimal.Decimal(left) / decimal.Decimal(right)
        elif expr.operator.type_ == TT.PLUS:
            '''
            Notice that because of Pythons dynamic typing, we didnt have to check for types,
            but we did so for learning purposes
            '''
            if type(left) is decimal.Decimal and type(right) is decimal.Decimal:
                return decimal.Decimal(left) + decimal.Decimal(right)
            if type(left) is str or type(right) is str:
                return str(left)+str(right)
            raise LoxRunTimeError(expr.operator, "Operands must either strings or numbers.")
        elif expr.operator.type_ in (TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL, TT.BANG_EQUAL,
                TT.EQUAL_EQUAL):
                op_func = op_dic[expr.operator.type_]
                return op_func(left, right)
        elif expr.operator.type_ == TT.COMMA:
            return right
        return None

    def visit_ternary_expr(self, expr: TernaryExpr):
        condition = self.evaluate(expr.condition)
        then_branch = self.evaluate(expr.left)
        else_branch = self.evaluate(expr.right)
        if self.is_truth(condition):
            return then_branch
        return else_branch
        
    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def is_truth(self, expression) -> bool:
        if expression is None:
            return False
        if type(expression) is bool:
            return expression
        return True
    
    def check_number_operand(self, operator: Token, *args):
        for arg in args:
            if type(arg) is not decimal.Decimal:
                raise LoxRuntimeError(operator, "Operand must be a number.")
    
    def stringify(self, value: any) -> str:
        if value is None:
            return "nil"
        if type(value) is decimal.Decimal:
            text = str(value)
            if text.endswith(".0"):
                text = text[0:len(text)-2]
            return text
        return str(value)

    def legal_divisor(self, operator: Token, divisor: decimal.Decimal) -> bool:
        if divisor == 0:
            raise LoxRunTimeError(operator, "Divisor must not be zero.")
            return False
        return True

            

    