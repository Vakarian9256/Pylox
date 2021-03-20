'''
The module is used to define the visitor pattern, the visits are implemented in the interpreter and the resolver.
We use the visitor design pattern to resolve variables, execute statements and evaluate expressions.
'''
from abc import ABC, abstractmethod
#from stmt import Stmt, Expression,Print, Var, Block, If, While, Break, Fun, Return, Class
from stmt import Stmt, Expression, Var, Block, If, While, Break, Fun, Return, Class
from expr import Expr, Assign, Binary, Conditional, Grouping, Literal, Logical, Unary, Variable, Function, Call, Get, Set, This, Super


class Visitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: Assign):
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: Binary):
        pass

    @abstractmethod
    def visit_conditional_expr(self, expr: Conditional):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping):
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: Literal):
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: Logical):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: Unary):
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: Variable):
        pass

    @abstractmethod
    def visit_function_expr(self, expr: Function):
        pass

    @abstractmethod
    def visit_call_expr(self, expr: Call):
        pass

    @abstractmethod
    def visit_get_expr(self, expr: Get):
        pass

    @abstractmethod
    def visit_set_expr(self, expr: Set):
        pass

    @abstractmethod
    def visit_this_expr(self, expr: This):
        pass

    @abstractmethod
    def visit_super_expr(self, expr: Super):
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression):
        pass
    '''
    @abstractmethod
    def visit_print_stmt(self, stmt: Print):
        pass
    '''
    @abstractmethod
    def visit_var_stmt(self, stmt: Var):
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt: Block):
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: If):
        pass

    @abstractmethod
    def visit_fun_stmt(self, stmt: Fun):
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt: Return):
        pass

    @abstractmethod
    def visit_class_stmt(self, stmt: Class):
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: While):
        pass

    @abstractmethod
    def visit_break_stmt(self, stmt: Break):
        pass
