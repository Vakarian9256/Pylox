import decimal
import sys
import operator
from visitor import Visitor
from expr import *
from token_type import TokenType as TT
from runtime_error import LoxRunTimeError
from error_handler import ErrorHandler
from stmt import *
from environment import Environment
from run_mode import RunMode

class Interpreter(Visitor):

    uninitialized = object()

    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.environment = Environment()

    def interpret(self, statements: list[Stmt], mode: RunMode):
        try:
            for statement in statements:
                self.execute_by_mode(statement, mode)
        except LoxRunTimeError as error:
            self.error_handler.runtime_error(error)

    def execute_by_mode(self, statement: Stmt, mode: RunMode):
        if mode == RunMode.REPL and type(statement) is Expression and type(statement.expr) is not Asign:
                value = self.evaluate(statement.expr)
                print(self.stringify(value))
        else:
            self.execute(statement)

    def execute(self, statement: Stmt):
        statement.accept(self)
    
    def visit_var_stmt(self, stmt: Var):
        value = Interpreter.uninitialized
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visit_expression_stmt(self, stmt: Expression):
        expr = self.evaluate(stmt.expr)

    def visit_print_stmt(self, stmt: Print):
        value = self.evaluate(stmt.expr)
        print(self.stringify(value))

    def visit_block_stmt(self, stmt: Block):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_if_stmt(self, stmt: If):
        if self.is_truth(stmt.condition):
            self.execute(stmt.then_branch)
        elif not self.is_truth(stmt.condition):
            self.execute(stmt.else_branch)

    def visit_variable_expr(self, expr: Variable) -> Any:
        value = self.environment.get(expr.name)
        if value == Interpreter.uninitialized:
            raise LoxRunTimeError(expr.name, "Variable must be initialized before use.")
        return value

    def visit_asign_expr(self, expr: Asign) -> Any:
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

    def visit_literal_expr(self, expr: Literal) -> str:
        return expr.value

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: Unary) -> str:
        right = self.evaluate(expr.right)
        if expr.operator.type_ == TT.MINUS:
            return -decimal.Decimal(right)
        if expr.operator.type_ == TT.BANG:
            return not self.is_truth(right)

    def visit_binary_expr(self, expr: Binary) -> str:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.type_ == TT.MINUS:
            self.check_number_operand(expr.operator, left, right)
            return decimal.Decimal(left) - decimal.Decimal(right)
        elif expr.operator.type_ == TT.STAR:
            self.check_number_operand(expr.operator, left, right)
            return decimal.Decimal(left) * decimal.Decimal(right)
        elif expr.operator.type_ == TT.SLASH:
            if self.legal_divisor(expr.operator, right):
                self.check_number_operand(expr.operator, left, right)
                return decimal.Decimal(left) / decimal.Decimal(right)
        elif expr.operator.type_ == TT.PLUS:
            '''
            Notice that because of Pythons dynamic typing, we didnt have to check for types,
            but we did so for learning purposes
            '''
            if type(left) is decimal.Decimal and type(right) is decimal.Decimal:
                return decimal.Decimal(left) + decimal.Decimal(right)
            elif type(left) is str or type(right) is str:
                return self.stringify(left)+self.stringify(right)
            raise LoxRunTimeError(expr.operator, "Operands must either strings or numbers.")
        elif expr.operator.type_ in (TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL, TT.BANG_EQUAL,
                TT.EQUAL_EQUAL):
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
                op_func = op_dic[expr.operator.type_]
                self.check_comparison_operands(expr.operator, left, right)
                return op_func(left, right)
        elif expr.operator.type_ == TT.COMMA:
            return right
        return None

    def visit_conditional_expr(self, expr: Conditional) -> str:
        condition = self.evaluate(expr.condition)
        then_branch = self.evaluate(expr.left)
        else_branch = self.evaluate(expr.right)
        if self.is_truth(condition):
            return then_branch
        return else_branch
        
    def visit_logical_expr(self, expr: Logical) -> str:
        left = self.evaluate(expr.left)
        if expr.operator.type_ == TT.OR:
            if self.is_truth(left):
                return left
        else:
            if not self.is_truth(left):
                return left
        return self.evaluate(expr.right)

    def visit_while_stmt(self, loop: While):
        while self.is_truth(self.evaluate(loop.condition)):
            self.execute(loop.body)
    
    def execute_block(self, statements: list[Stmt], environment: Environment):
        previous_envi = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous_envi
    
    def evaluate(self, expr: Expr) -> str:
        return expr.accept(self)

    def check_comparison_operands(self, operator: Token, *args):
        all_string = True
        all_num = True
        for arg in args:
            if type(arg) is not str:
                all_string = False
            if type(arg) is not decimal.Decimal:
                all_num = False
        if all_num == False and all_string == False:
            raise LoxRunTimeError(operator, "Operands must all be of the same type.")

    def is_truth(self, expression) -> bool:
        if expression is None:
            return False
        if type(expression) is bool:
            return expression
        return True
    
    def check_number_operand(self, operator: Token, *args):
        for arg in args:
            if type(arg) is not decimal.Decimal:
                raise LoxRunTimeError(operator, "Operands must be numbers.")
    
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

            

    