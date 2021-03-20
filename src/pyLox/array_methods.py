from Lox_callable import LoxCallable
from error import LoxRunTimeError

class _Get(LoxCallable):
    def __init__(self, outer):
        self.outer = outer

    def call(self, interpreter, arguments):
        index = arguments[0]
        if index < len(self.outer.elements):
            return self.outer.elements[index]
        else:
            raise LoxRunTimeError(name,"Array index out of range.")  

    def arity(self):
        return 1

class _Set(LoxCallable):
    def __init__(self, outer):
        self.outer = outer

    def call(self, interpreter, arguments):
        index = arguments[0]
        value = arguments[1]
        if index is not None:
            self.outer.elements[index] = value
        else:
            self.outer.elements.append(value)

    def arity(self):
        return 2

class _Length(LoxCallable):
    def __init__(self, outer):
        self.outer = outer
    
    def call(self, interpreter, arguments):
        return len(self.outer.elements)

    def arity(self):
        return 0