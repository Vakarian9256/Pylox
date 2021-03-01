import sys
from decimal import Decimal
import operator
from typing import Any
from native import Clock
from visitor import Visitor
from stmt import Stmt, Expression, Print, Var, Block, If, While, Fun, Return, Break
from expr import Expr, Assign, Binary, Conditional, Grouping, Literal, Logical, Unary, Variable, Function, Call
from token_type import TokenType
from token import Token
from error import LoxRunTimeError, DivisionByZeroError, ReturnException, BreakException
from error_handler import ErrorHandler
from environment import Environment
from run_mode import RunMode
from Lox_callable import LoxCallable
from Lox_function import LoxFunction
from var_state import VarState

class Interpreter(Visitor):

    uninitialized = object()
    op_dic = {
              TokenType.LESS : operator.lt,
              TokenType.LESS_EQUAL: operator.le,
              TokenType.GREATER : operator.gt,
              TokenType.GREATER_EQUAL : operator.ge,
              TokenType.MINUS : operator.sub,
              TokenType.SLASH : operator.truediv,
              TokenType.STAR : operator.mul,
              TokenType.EQUAL_EQUAL : operator.eq,
              TokenType.BANG_EQUAL : operator.ne
             }

    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.globals = Environment()
        self.environment = self.globals
        self.globals.define('clock', Clock())
        self.locals = {}

    def interpret(self, statements: list[Stmt], mode: RunMode):
        try:
            for statement in statements:
                self.execute_by_mode(statement, mode)
        except LoxRunTimeError as error:
            self.error_handler.runtime_error(error)

    def execute_by_mode(self, statement: Stmt, mode: RunMode):
        if mode == RunMode.REPL and type(statement) is Expression and type(statement.expr) is not Assign:
                value = self.evaluate(statement.expr)
                print(self.stringify(value))
        else:
            self.execute(statement)

    def execute(self, statement: Stmt):
        statement.accept(self)
    
    def resolve(self, expr: Expr, depth: int):
        self.locals[expr] = depth
    
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
        if self.is_truth(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_return_stmt(self, stmt: Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnException(value)

    def visit_while_stmt(self, loop: While):
        try:
            while self.is_truth(self.evaluate(loop.condition)):
                self.execute(loop.body)
        except BreakException:
            pass
    
    def visit_break_stmt(self, break_stmt: Break):
        raise BreakException()
    
    def visit_fun_stmt(self, stmt: Fun):
        f_name = stmt.name.lexeme
        self.environment.define(f_name, LoxFunction(f_name, stmt.function, self.environment))
        return None

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self.look_up_variable(expr.name, expr)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value = self.evaluate(expr.value)
        if expr in self.locals:
            self.environment.assign_at(self.locals[expr], expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_literal_expr(self, expr: Literal) -> str:
        return expr.value

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: Unary) -> str:
        right = self.evaluate(expr.right)
        if expr.operator.type_ == TokenType.MINUS:
            return -Decimal(right)
        if expr.operator.type_ == TokenType.BANG:
            return not self.is_truth(right)

    def visit_binary_expr(self, expr: Binary) -> str:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.type_ == TokenType.MINUS:
            self.check_number_operand(expr.operator, left, right)
            return Decimal(left) - Decimal(right)
        elif expr.operator.type_ == TokenType.STAR:
            self.check_number_operand(expr.operator, left, right)
            return Decimal(left) * Decimal(right)
        elif expr.operator.type_ == TokenType.SLASH:
            if self.legal_divisor(expr.operator, right):
                self.check_number_operand(expr.operator, left, right)
                return Decimal(left) / Decimal(right)
        elif expr.operator.type_ == TokenType.PLUS:
            '''
            Notice that because of Pythons dynamic typing, we didnt have to check for types,
            but we did so for learning purposes
            '''
            if type(left) is Decimal and type(right) is Decimal:
                return Decimal(left) + Decimal(right)
            elif type(left) is str or type(right) is str:
                return self.stringify(left)+self.stringify(right)
            raise LoxRunTimeError(expr.operator, "Operands must either strings or numbers.")
        elif expr.operator.type_ in Interpreter.op_dic:
                op_func = Interpreter.op_dic[expr.operator.type_]
                self.check_comparison_operands(expr.operator, left, right)
                return op_func(left, right)
        elif expr.operator.type_ == TokenType.COMMA:
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
        if expr.operator.type_ == TokenType.OR:
            if self.is_truth(left):
                return left
        else:
            if not self.is_truth(left):
                return left
        return self.evaluate(expr.right)

    def visit_function_expr(self, expr: Function) -> str:
        return LoxFunction(None, expr, self.environment)

    def visit_call_expr(self, expr: Call) -> str:
        callee = self.evaluate(expr.callee)
        if not isinstance(callee, LoxCallable):
            raise LoxRunTimeError(expr.paren,"Can only call functions and classes." )
        arguments = [self.evaluate(argument) for argument in expr.args]
        if len(arguments) != callee.arity():
            raise LoxRunTimeError(expr.paren,f"Expected {callee.arity()} arguments but got {len(arguments)}.")
        return callee.call(self, arguments)

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
            if type(arg) is not Decimal:
                all_num = False
        if all_num == False and all_string == False:
            raise LoxRunTimeError(operator, "Operands must all be of the same type.")

    def is_truth(self, expression) -> bool:
        if expression is None:
            return False
        if type(expression) is bool:
            return expression
        return True

    def look_up_variable(self, name: Token, expr: Expr) -> Any:
        if expr in self.locals:
            value = self.environment.get_at(self.locals[expr], name.lexeme)
        else:
            value = self.globals.get(name)
        if value == Interpreter.uninitialized:
            raise LoxRunTimeError(name, "Variable must be initialized before use.")
        return value
    
    def check_number_operand(self, operator: Token, *args):
        for arg in args:
            if type(arg) is not Decimal:
                raise LoxRunTimeError(operator, "Operands must be numbers.")
    
    def stringify(self, value: any) -> str:
        if value is None:
            return "nil"
        if type(value) is Decimal:
            text = str(value)
            if text.endswith(".0"):
                text = text[0:len(text)-2]
            return text
        return str(value)

    def legal_divisor(self, operator: Token, divisor: Decimal) -> bool:
        if divisor == 0:
            raise DivisionByZeroError(operator)
            return False
        return True

            

    