from abc import ABC, abstractmethod
from typing import Any, List

class LoxCallable:
    @abstractmethod
    def call(self, interpreter, arguments: list[Any]):
        pass

    @abstractmethod
    def arity(self):
        pass