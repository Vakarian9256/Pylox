'''
The module houses the definition of a class in Lox. The class inherits from instance
, which is how we implement metaclasses and class methods, and implements Lox callable.
'''
from abc import ABC, abstractmethod
from typing import Any
from Lox_callable import LoxCallable
from Lox_instance import LoxInstance
from token import Token
from error import LoxRunTimeError

class LoxClass(LoxCallable, LoxInstance):
    def __init__(self, metaclass, super_class, name: str, methods):
        super().__init__(metaclass)
        self.super_class = super_class
        self.name = name
        self.methods = methods
        
    def call(self, interpreter, arguments: list[Any]):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def arity(self):
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def find_method(self, name: str):
        if name in self.methods.keys():
            return self.methods.get(name)
        if self.super_class is not None:
            return self.super_class.find_method(name)
        return None

    def __str__(self):
        return self.name