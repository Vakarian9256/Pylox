'''
The module houses native functions and classes for Lox - The "Lox Native Library"/LNL.
'''
import time
from typing import List, Any
from Lox_callable import LoxCallable
from Lox_instance import LoxInstance
from abc import ABC, abstractmethod
from token import Token
from error import LoxRunTimeError
import array_methods as arr
from input_util import _typify

'''
This function will show the time passed since the running of interpreter started and until the function has been called. Can be called by clock()
'''
class Clock(LoxCallable):
            def call(self, interpreter, arguments: list[Any]):
                return float(time.perf_counter())
            
            def arity(self):
                return 0
            
            def __str__(self):
                return "<Native func 'clock'>"

'''
This function reads input from the user. it receives a single argument, message, which will be shown as a prompt to the user. 
Can be called by read(message)
'''
class Read(LoxCallable):
    def call(self, interpreter, arguments: list[Any]):
        message  = arguments[0]
        user_input = input(message)
        return _typify(user_input)
    
    def arity(self):
        return 1

'''
This class creates a new Lox array object. It receives a single argument, size, which will be the size of the new array object.
Can be called by array(size).
'''
class Array(LoxCallable):
    def call(self, interpreter, arguments: list[Any]):
        return LoxArray(int(arguments[0]))
    
    def arity(self):
        return 1
    
'''
The implementation of the Lox array, I chose to implement it as a dynamic array.
On construction, the array is initialized to be an array of 'size' amount of nil.
The array has three methods:
1. get(i) - returns the value at index i. a runtime error is raised if the index is not in range or is not an integer.
2. set(i, value) - if i is not nil, then set value at index i, else append the value to the end of the array.
                   A runtime error is raised if the index is not in range or is not an integer.
3. length() - returns the length of the array.
'''
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


'''
This class serves as our print function. It receives a single argument, message, which will be printed.
'''
class Print(LoxCallable):
    def call(self, interpreter, arguments: list[Any]):
        message = arguments[0]
        message = interpreter.stringify(message)
        print(message)
    
    def arity(self):
        return 1