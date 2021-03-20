import time
from typing import List, Any
from Lox_callable import LoxCallable
from Lox_instance import LoxInstance
from abc import ABC, abstractmethod
from token import Token
from error import LoxRunTimeError
import array_methods as arr
from input_util import typify

class Clock(LoxCallable):
            def call(self, interpreter, arguments: list[Any]):
                return float(time.perf_counter())
            
            def arity(self):
                return 0
            
            def __str__(self):
                return "<Native func 'clock'>"

class Read(LoxCallable):
    def call(self, interpreter, arguments: list[Any]):
        message  = arguments[0]
        user_input = input(message)
        return typify(user_input)
    
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
            return arr._Get(self, name)
        elif name.lexeme == 'set':
            return arr._Set(self, name)
        elif name.lexeme == 'length':
            return arr._Length(self)
        raise LoxRunTimeError(name,f"Undefined property {name.lexeme}.")
    def set(self, name: Token, value):
        raise LoxRunTimeError(name,"Can't add properties to arrays.")
    
    def __str__(self):
        string = "["
        for member in self.elements:
            string += f"{member}"
            if type(member) is float and member.is_integer():
                string = string[:-2]
            string += ", "
        string = string[:-2]
        string += "]"
        return string

class Print(LoxCallable):
    def call(self, interpreter, arguments: list[Any]):
        message = arguments[0]
        message = interpreter.stringify(message)
        print(message)
    
    def arity(self):
        return 1