from visitor import Visitor
from stmt import Stmt, Expression, Print, Var, Block, If, While, Fun, Return, Break
from expr import Expr, Assign, Binary, Conditional, Grouping, Literal, Logical, Unary, Variable, Function, Call
from error_handler import ErrorHandler
from token import Token
from interpreter import Interpreter
from function_types import FunctionType

class Resolver(Visitor):
    def __init__(self, interpreter: Interpreter, error_handler: ErrorHandler):
        self.interpreter = interpreter
        self.scopes = []
        self.error_handler = error_handler
        self.current_function = FunctionType.NONE
    
    def visit_block_stmt(self, stmt: Block):
        self.begin_scope()
        self.resolve_list(stmt.statements)
        self.end_scope()
        return None

    def visit_var_stmt(self, stmt: Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve_expr(stmt.initializer)
        self.define(stmt.name)
        
    def visit_fun_stmt(self, stmt: Fun):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_expr(stmt.function)

    def visit_expression_stmt(self, stmt: Expression):
        self.resolve_expr(stmt.expr)

    def visit_if_stmt(self, stmt: If):
        self.resolve_expr(stmt.condition)
        self.resolve_expr(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve_expr(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print):
        self.resolve_expr(stmt.expr)

    def visit_return_stmt(self, stmt: Return):
        if self.current_function == FunctionType.NONE:
            self.error_handler.error(stmt.keyword,"Can't return from top-level code.")
        if stmt.value is not None:
            self.resolve_expr(stmt.value)

    def visit_while_stmt(self, stmt: While):
        self.resolve_expr(stmt.condition)
        self.resolve(stmt.body)
    
    def visit_variable_expr(self, expr: Variable):
        if len(self.scopes) != 0 and expr.name.lexeme in self.scopes[-1] == False:
            self.error_handler.error(expr.name, "Cant read local variable in its own initializer.")
        self.resolve_local(expr, expr.name)

    def visit_break_stmt(self, stmt: Break):
        pass

    def visit_assign_expr(self, expr: Assign):
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name) 

    def visit_call_expr(self, expr: Call):
        self.resolve_expr(expr.callee)
        for arg in expr.args:
            self.resolve_expr(arg)
    
    def visit_binary_expr(self, expr: Binary):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_conditional_expr(self, expr: Conditional):
        self.resolve_expr(expr.condition)
        self.resolve_expr(expr.then_branch)
        self.resolve_expr(expr.else_branch)

    def visit_logical_expr(self, expr: Logical):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_unary_expr(self, expr: Unary):
        self.resolve_expr(expr.right)

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

    def resolve(self, statement: Stmt):
        statement.accept(self)

    def resolve_expr(self, expr: Expr):
        expr.accept(self)

    def resolve_local(self, expr: Expr, name: Token):
        for i in range(len(self.scopes)-1,-1,-1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - i - 1)
                return

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if len(self.scopes) == 0:
            return None
        peek = self.scopes[-1]
        if name.lexeme in peek:
            self.error_handler.error(name,"Variable with this name has already been declared in this scope.")
        peek[name.lexeme] = False
    
    def define(self, name: Token):
        if len(self.scopes) == 0:
            return None
        self.scopes[-1][name.lexeme] = True