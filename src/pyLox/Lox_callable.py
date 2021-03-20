'''
The module houses the definition of a Lox callable - an action that can be called - a class or a function.
a callable can be called, with call(), and arity(), which specifies how many parameters must be passed to the callable action.
'''
from abc import ABC, abstractmethod
from typing import Any, List

class LoxCallable:
    @abstractmethod
    def call(self, interpreter, arguments: list[Any]):
        pass

    @abstractmethod
    def arity(self):
        pass