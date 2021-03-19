from typing import Any
from Lox_callable import LoxCallable
from stmt import Expression, Print, Var, Block, If, While, Fun, Return, Break
from expr import Function
from environment import Environment
from error import ReturnException
from function_type import FunctionType

class LoxFunction(LoxCallable):
    def __init__(self, name: str, declaration: Function, closure: Environment, is_ini=False):
        self.name = name
        self.declaration = declaration
        self.closure = closure
        self.is_ini = is_ini

    def call(self,interpreter, arguments: list[Any]):
        environment = Environment(self.closure)
        for i in range(len(arguments)):
            environment.define(arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as ret:
            if type(self.is_ini) is int:
                return self.closure.get_at(0, self.is_ini)
            return ret.value
        if type(self.is_ini) is int:
            return self.closure.get_at(0, self.is_ini)
        return None

    def arity(self):
        return len(self.declaration.params)
    
    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define(instance)
        if type(self.is_ini) is bool and self.is_ini:
            return LoxFunction(self.name, self.declaration, environment, len(environment.vars)-1)
        else:
            return LoxFunction(self.name, self.declaration, environment, self.is_ini)

    def is_getter(self):
        return self.declaration.type_ == FunctionType.GETMETHOD

    def __str__():
        if self.name is None:
            return "<function>"
        return f"<function {self.name}>"

