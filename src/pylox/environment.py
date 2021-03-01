import sys
from typing import Any
from token import Token
from error import LoxRunTimeError
class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing
        self.var_map = {}

    def define(self, name: str, value: Any):
        self.var_map[name] = value

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.var_map:
            self.define(name.lexeme, value)
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        else:
            raise LoxRunTimeError(name, f"Undefined variable {name.lexeme}.")

    def assign_at(self, distance: int, name: Token, value: Any):
        self.ancestor(distance).var_map[name.lexeme] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.var_map:
            return self.var_map[name.lexeme]
        if self.enclosing is not None:
            self.enclosing.get(name)
            return
        raise LoxRunTimeError(name, f"Undefined variable {name.lexeme}.")

    def get_at(self, distance: int, name: str) -> Any:
        return self.ancestor(distance).var_map[name]

    def ancestor(self, distance: int):
        env = self
        for i in range(0,distance):
            env = env.enclosing
        return env


