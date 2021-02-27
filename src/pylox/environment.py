import sys
from typing import Any
from token import Token
from runtime_error import LoxRunTimeError
class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing if enclosing is not None else None
        self.dict = {}

    def define(self, name: str, value: Any):
        self.dict.update({name:value})

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.dict:
            self.dict[name.lexeme] = value
        elif self.enclosing is not None:
            return self.enclosing.assign(name, value)
        else:
            raise LoxRunTimeError(name, f"Undefined variable {name.lexeme}.")

    def get(self, name: Token) -> Any:
        if name.lexeme in self.dict:
            return self.dict.get(name.lexeme)
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise LoxRunTimeError(name, f"Undefined variable {name.lexeme}.")


