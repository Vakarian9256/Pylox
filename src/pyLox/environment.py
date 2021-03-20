'''
The module houses the defintion of an environment, which is the implementation of a scope in Lox.
'''
import sys
from typing import Any
from token import Token
from error import LoxRunTimeError
from var_state import VarState

class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing
        self.vars = []

    def define(self, value: Any):
        self.vars.append(value)

    def assign_at(self, distance: int, slot: int, value: Any):
        self.ancestor(distance).vars[slot] = value

    def get_at(self, distance: int, slot) -> Any:
        return self.ancestor(distance).vars[slot]

    def ancestor(self, distance: int):
        env = self
        for i in range(0,distance):
            env = env.enclosing
        return env


