from abc import ABC, abstractmethod
from token import * 

from expr import *

class Visitor(ABC):
    @abstractmethod
    def visit_binary_expr(self,expr: BinaryExpr) -> str:
        pass

    @abstractmethod
    def visit_grouping_expr(self,expr: GroupingExpr) -> str:
        pass

    @abstractmethod
    def visit_literal_expr(self,expr: LiteralExpr) -> str:
        pass

    @abstractmethod
    def visit_unary_expr(self,expr: UnaryExpr) -> str:
        pass

    @abstractmethod
    def visit_conditional_expr(self, expr: TernaryExpr) -> str:
        pass

