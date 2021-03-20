'''
The module serves as our interpreter pass, whose job is to evaluate and execute statements, and find and report runtime errors.
The evalutation and execution are achieved with the visitor design pattern, and therefore it will implement the visitor class.
'''
import sys
import operator
from typing import Any
from native import Clock, Read, Array, Print
from visitor import Visitor
#from stmt import Stmt, Expression,Print, Var, Block, If, While, Break, Fun, Return, Class
from stmt import Stmt, Expression, Var, Block, If, While, Break, Fun, Return, Class
from expr import Expr, Assign, Binary, Conditional, Grouping, Literal, Logical, Unary, Variable, Function, Call, Get, Set, This, Super
from token_type import TokenType
from token import Token
from error import LoxRunTimeError, DivisionByZeroError, ReturnException, BreakException
from error_handler import ErrorHandler
from environment import Environment
from run_mode import RunMode
from Lox_callable import LoxCallable
from Lox_function import LoxFunction
from var_state import VarState
from Lox_class import LoxClass
from Lox_instance import LoxInstance

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
        self.globals = {}
        self.environment = None
        self.globals['clock'] =  Clock()
        self.globals['read'] = Read()
        self.globals['array'] = Array()
        self.globals['print'] = Print()
        self.locals = {}
        self.slots = {}

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
    
    def resolve(self, expr, depth: int, slot: int):
        self.locals[expr] = depth
        self.slots[expr] = slot
    
    def visit_var_stmt(self, stmt: Var):
        value = Interpreter.uninitialized
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.define(stmt.name.lexeme, value)

    def visit_expression_stmt(self, stmt: Expression):
        expr = self.evaluate(stmt.expr)
    '''
    def visit_print_stmt(self, stmt: Print):
        value = self.evaluate(stmt.expr)
        print(self.stringify(value))
    '''
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

    def visit_class_stmt(self, stmt: Class):
        self.define(stmt.name.lexeme, None)
        super_class = None
        if stmt.super_class is not None:
            super_class = self.evaluate(stmt.super_class)
            if not isinstance(super_class, LoxClass):
                raise LoxRunTimeError(stmt.super_class.name,"Superclass must be a class.")
            self.environment = Environment(self.environment)
            self.environment.define(super_class)
        class_methods = {}
        for class_method in stmt.class_methods:
            function = LoxFunction(class_method, class_method.function, self.environment, False)
            class_methods[class_method.name.lexeme] = function
        metaclass = LoxClass(None, f'{stmt.name.lexeme}metaclass', None, class_methods)
        methods = {}
        for method in stmt.methods:
            function = LoxFunction(method, method.function, self.environment, method.name.lexeme == 'init')
            methods[method.name.lexeme] = function
        klass = LoxClass(metaclass, super_class, stmt.name.lexeme, methods)
        if super_class is not None:
            self.environment = self.environment.enclosing
        if self.environment:
            self.environment.assign_at(0, self.slots[stmt], klass)
        else:
            self.globals[stmt.name.lexeme] = klass

    def visit_this_expr(self, expr: This):
        return self.look_up_variable(expr.keyword, expr)
    
    def visit_super_expr(self, expr: Super):
        super_class = self.environment.get_at(self.locals[expr], self.slots[expr])
        if self.environment:
            obj = self.environment.get_at(self.locals[expr] - 1, 0)
        else:
            obj = self.globals['this']
        method = super_class.find_method(expr.method.lexeme)
        if method is None:
            raise LoxRunTimeError(expr.method,f"Undefined propery {expr.method.lexeme}.")
        return method.bind(obj)

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
        self.define(f_name, LoxFunction(f_name, stmt.function, self.environment))
        return None

    def visit_variable_expr(self, expr: Variable) -> Any:
        return self.look_up_variable(expr.name, expr)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value = self.evaluate(expr.value)
        if expr in self.locals:
            self.environment.assign_at(self.locals[expr], self.slots[expr], value)
        else:
            if expr.name.lexeme in self.globals:
                self.globals[expr.name.lexeme] = value
            else:
                raise LoxRunTimeError(expr.name, f"Undefined variable {expr.name.lexeme}.")
        return value

    def visit_literal_expr(self, expr: Literal) -> str:
        return expr.value

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr: Unary) -> str:
        right = self.evaluate(expr.right)
        if expr.operator.type_ == TokenType.MINUS:
            value =  -float(right)
            value = int(value) if value.is_integer() else value
            return value
        if expr.operator.type_ == TokenType.BANG:
            return not self.is_truth(right)

    def visit_binary_expr(self, expr: Binary) -> str:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.type_ == TokenType.MINUS:
            self.check_number_operand(expr.operator, left, right)
            value = float(left) - float(right)
            value = int(value) if value.is_integer() else value
            return value            
        elif expr.operator.type_ == TokenType.STAR:
            self.check_number_operand(expr.operator, left, right)
            value = float(left) * float(right)
            value = int(value) if value.is_integer() else value
            return value
        elif expr.operator.type_ == TokenType.SLASH:
            if self.legal_divisor(expr.operator, right):
                self.check_number_operand(expr.operator, left, right)
                value = float(left) / float(right)
                value = int(value) if value.is_integer() else value
                return value
        elif expr.operator.type_ == TokenType.PLUS:
            '''
            Notice that because of Pythons dynamic typing, we didnt have to check for types,
            but we did so for learning purposes.
            '''
            if (type(left) is float or type(left) is int) and (type(right) is float or type(right) is int):
                value = float(left) + float(right)
                value = int(value) if value.is_integer() else value
                return value
            elif type(left) is str or type(right) is str:
                value = self.stringify(left)+self.stringify(right)
                return value
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

    def visit_get_expr(self, expr: Get) -> str:
        obj = self.evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            result = obj.get(expr.name)
            if isinstance(result, LoxFunction) and result.is_getter():
                result = result.call(self, [])
        else:
            raise LoxRunTimeError(expr.name,"Only instances have properties.")
        return result

    def visit_set_expr(self, expr: Set) -> str:
        obj = self.evaluate(expr.obj)
        if not isinstance(obj, LoxInstance):
            raise LoxRunTimeError(expr.name,"Only instances have properties.")
        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

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
            if type(arg) is not float and type(arg) is not int:
                print(type(arg))
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
            value = self.environment.get_at(self.locals[expr], self.slots[expr])
        elif name.lexeme in self.globals:
            value = self.globals[name.lexeme]
        else:
            raise LoxRunTimeError(name, f"Undefined variable {name.lexeme}.")
        if value == Interpreter.uninitialized:
            raise LoxRunTimeError(name, "Variable must be initialized before use.")
        return value
    
    def check_number_operand(self, operator: Token, *args):
        for arg in args:
            if (type(arg) is not float) and (type(arg) is not int):
                raise LoxRunTimeError(operator, "Operands must be numbers.")
    
    def stringify(self, value: any) -> str:
        if value is None:
            return "nil"
        if type(value) is float:
            text = str(value)
            if text.endswith(".0") or value.is_integer():
                text = text[0:len(text)-2]
            return text
        return str(value)

    def legal_divisor(self, operator: Token, divisor: float) -> bool:
        if divisor == 0:
            raise DivisionByZeroError(operator)
            return False
        return True

    def define(self, name: str, value: Any):
        if self.environment is not None:
            self.environment.define(value)
        else:
            self.globals[name] = value    