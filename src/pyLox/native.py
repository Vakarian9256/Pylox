import time
from typing import List, Any
from Lox_callable import LoxCallable
from Lox_instance import LoxInstance
from token import Token
from error import LoxRunTimeError
import array_methods as arr

class Clock(LoxCallable):
            def call(self, interpreter, arguments: list[Any]):
                return time.perf_counter()
            
            def arity(self):
                return 0
            
            def __str__(self):
                return "<Native func 'clock'>"

class Read(LoxCallable):
    def call(self, interpreter, arguments: list[Any]):
        message  = argumetns[0]
        return input(message)
    
    def arity(self):
        return 1

class Array(LoxCallable):
    def call(self, interpreter, arguments: list[Any]):
        return LoxArray(int(arguments[0]))
    
    def arity(self):
        return 1
    

class LoxArray(LoxInstance):
    def __init__(self, size):
        self.elements = [None] * size
    
    def get(self, name):
        if name.lexeme == 'get':
            return arr._Get(self)
        elif name.lexeme == 'set':
            return arr._Set(self)
        elif name.lexeme == 'length':
            return arr._Length(self)
        raise LoxRunTimeError(name,f"Undefined property {name.lexeme}.")
    def set(self, name: Token, value):
        raise LoxRunTimeError(name,"Can't add properties to arrays.")
    
    def __str__(self):
        return str(self.elements)