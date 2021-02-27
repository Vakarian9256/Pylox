from abc import ABC, abstractmethod
from expr import * 
from stmt import *  

from stmt import *
from expr import *

class Visitor(ABC):
    @abstractmethod
    def visit_binary_expr(self,expr: Binary):
        pass

    @abstractmethod
    def visit_grouping_expr(self,expr: Grouping):
        pass

    @abstractmethod
    def visit_literal_expr(self,expr: Literal):
        pass

    @abstractmethod
    def visit_unary_expr(self,expr: Unary):
        pass

    @abstractmethod
    def visit_conditional_expr(self,expr: Conditional):
        pass
'''
    @abstractmethod
    def visit_expression_stmt(self,stmt: Expression):
        pass

    @abstractmethod
    def visit_print_stmt(self,stmt: Print):
        pass
'''