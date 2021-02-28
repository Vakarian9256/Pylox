import sys
from Lox_callable import *
from stmt import *
from environment import Environment
from error import *
from expr import Function

class LoxFunction(LoxCallable):
    def __init__(self, name: str, declaration: Function, closure: Environment):
        self.name = name
        self.declaration = declaration
        self.closure = closure

    def call(self,interpreter, arguments: list[Any]):
        environment = Environment(self.closure)
        for i in range(len(arguments)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as ret:
            return ret.value
        return None

    def arity(self):
        return len(self.declaration.params)

    def __str__():
        if self.name is None:
            return "<function>"
        return f"<function {self.name}>"

