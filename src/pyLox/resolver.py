from visitor import Visitor
from stmt import *
from expr import *
from error_handler import ErrorHandler
from token import Token
from interpreter import Interpreter
from token_type import TokenType
from function_type import FunctionType
from var_state import VarState
from class_type import ClassType

class Resolver(Visitor):
    def __init__(self, interpreter: Interpreter, error_handler: ErrorHandler):
        self.interpreter = interpreter
        self.scopes = []
        self.error_handler = error_handler
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
    
    def visit_block_stmt(self, stmt: Block):
        self.begin_scope()
        self.resolve_list(stmt.statements)
        self.end_scope()
        return None

    def visit_var_stmt(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None and stmt.initializer != Interpreter.uninitialized:
            self.resolve(stmt.initializer)
        self.define(stmt.name)
        
    def visit_fun_stmt(self, stmt: Fun):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.scopes[-1][stmt.name.lexeme].state = VarState.READ
        self.resolve(stmt.function)

    def visit_class_stmt(self, stmt: Class):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        self.begin_scope()
        self.scopes[-1]["this"] = Variable(Token(TokenType.THIS, 'this', None, stmt.name.line),VarState.READ)
        for method in stmt.methods:
            method.type_ = FunctionType.METHOD
            if method.name.lexeme == 'init':
                method.type_ = FunctionType.INITIALIZER
            self.resolve(method)
        self.end_scope()
        self.current_class = enclosing_class

    def visit_expression_stmt(self, stmt: Expression):
        self.resolve(stmt.expr)

    def visit_if_stmt(self, stmt: If):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print):
        self.resolve(stmt.expr)

    def visit_return_stmt(self, stmt: Return):
        if self.current_function == FunctionType.NONE:
            self.error_handler.error_on_token(stmt.keyword,"Can't return from top-level code.")
        elif self.current_function == FunctionType.INITIALIZER:
            self.error_handler.error_on_token(stmt.keyword,"Can't return a value from an initializer.") 
        if stmt.value is not None:
            self.resolve(stmt.value)

    def visit_while_stmt(self, stmt: While):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
    
    def visit_variable_expr(self, expr: Variable):
        if self.scopes and expr.name.lexeme in self.scopes[-1]:
            if self.scopes[-1][expr.name.lexeme].state == VarState.DECLARED:
                self.error_handler.error_on_token(expr.name, "Cant read local variable in its own initializer.")
        self.resolve_local(expr, expr.name, True)

    def visit_break_stmt(self, stmt: Break):
        pass

    def visit_assign_expr(self, expr: Assign):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name, False) 

    def visit_call_expr(self, expr: Call):
        self.resolve(expr.callee)
        for arg in expr.args:
            self.resolve(arg)

    def visit_get_expr(self, expr: Get):
        self.resolve(expr.obj)
    
    def visit_set_expr(self, expr: Set):
        self.resolve(expr.value)
        self.resolve(expr.obj)
    
    def visit_this_expr(self, expr: This):
        if self.current_class == ClassType.NONE:
            self.error_handler.error_on_token(expr.keyword, "Can't use 'this' outside of a class.")
        self.resolve_local(expr, expr.keyword, True)
    
    def visit_binary_expr(self, expr: Binary):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_conditional_expr(self, expr: Conditional):
        self.resolve(expr.condition)
        self.resolve(expr.then_branch)
        self.resolve(expr.else_branch)

    def visit_logical_expr(self, expr: Logical):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary_expr(self, expr: Unary):
        self.resolve(expr.right)

    def visit_grouping_expr(self, expr: Grouping):
        self.resolve(expr.expression)

    def visit_function_expr(self, expr: Function):
        enclosing_function = self.current_function
        self.current_function = expr.type_
        self.begin_scope()
        for param in expr.params:
            self.declare(param)
            self.define(param)
        self.resolve_list(expr.body)
        self.current_function = enclosing_function
        self.end_scope()

    def visit_literal_expr(self, expr: Literal):
        pass

    def resolve_list(self, statements: list[Stmt]):
        for statement in statements:
            self.resolve(statement)

    def resolve(self, obj: 'Stmt or Expr'):
        obj.accept(self)

    def resolve_local(self, expr: Expr, name: Token, is_read: bool):
        for i in range(len(self.scopes)-1,-1,-1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - i - 1)
                if is_read:
                    self.scopes[i][name.lexeme].state = VarState.READ
                return

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        ending = self.scopes.pop()
        for entry in ending:
            if ending[entry].state != VarState.READ:
                self.error_handler.error_on_token(ending[entry].name, "Local variable not used.")


    def declare(self, name: Token):
        if not self.scopes:
            return None
        peek = self.scopes[-1]
        if name.lexeme in peek:
            self.error_handler.error_on_token(name,"Variable with this name has already been declared in this scope.")
        peek[name.lexeme] = Variable(name, VarState.DECLARED)
    
    def define(self, name: Token):
        if not self.scopes:
            return None
        self.scopes[-1][name.lexeme] = Variable(name, VarState.DEFINED)