from typing import Any
from Lox_callable import LoxCallable
from stmt import Expression, Print, Var, Block, If, While, Fun, Return, Break
from expr import Function
from environment import Environment
from error import ReturnException

class LoxFunction(LoxCallable):
    def __init__(self, name: str, declaration: Function, closure: Environment, is_ini=False):
        self.name = name
        self.declaration = declaration
        self.closure = closure
        self.is_ini = is_ini

    def call(self,interpreter, arguments: list[Any]):
        environment = Environment(self.closure)
        for i in range(len(arguments)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as ret:
            if self.is_ini:
                return self.closure.get_at(0, 'this')
            return ret.value
        if self.is_ini:
            return self.closure.get_at(0,'this')
        return None

    def arity(self):
        return len(self.declaration.params)
    
    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.name, self.declaration, environment, self.is_ini)

    def __str__():
        if self.name is None:
            return "<function>"
        return f"<function {self.name}>"

