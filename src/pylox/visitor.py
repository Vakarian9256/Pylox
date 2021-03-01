from abc import ABC, abstractmethod
from stmt import Expression, Print, Var, Block, If, While, Fun, Return, Break
from expr import Assign, Binary, Conditional, Grouping, Literal, Logical, Unary, Variable, Function, Call


class Visitor(ABC):
    @abstractmethod
    def visit_assign_expr(self, expr: Assign) -> str:
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> str:
        pass

    @abstractmethod
    def visit_conditional_expr(self, expr: Conditional) -> str:
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> str:
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> str:
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: Logical) -> str:
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> str:
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: Variable) -> str:
        pass

    @abstractmethod
    def visit_function_expr(self, expr: Function) -> str:
        pass

    @abstractmethod
    def visit_call_expr(self, expr: Call) -> str:
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> str:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> str:
        pass

    @abstractmethod
    def visit_var_stmt(self, stmt: Var) -> str:
        pass

    @abstractmethod
    def visit_block_stmt(self, stmt: Block) -> str:
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: If) -> str:
        pass

    @abstractmethod
    def visit_fun_stmt(self, stmt: Fun) -> str:
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt: Return) -> str:
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: While) -> str:
        pass

    @abstractmethod
    def visit_break_stmt(self, stmt: Break) -> str:
        pass

