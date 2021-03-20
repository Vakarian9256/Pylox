from Lox_callable import LoxCallable
from error import LoxRunTimeError

class _Get(LoxCallable):
    def __init__(self, outer, name):
        self.outer = outer
        self.name = name

    def call(self, interpreter, arguments):
        index = arguments[0]
        if index < len(self.outer.elements):
            return self.outer.elements[index]
        else:
            raise LoxRunTimeError(self.name,"Array index out of range.")  

    def arity(self):
        return 1

class _Set(LoxCallable):
    def __init__(self, outer, name):
        self.outer = outer
        self.name = name

    def call(self, interpreter, arguments):
        index = arguments[0]
        value = arguments[1]
        if index is not None:
            if type(index) is int or (type(index) is float and index.is_integer()):
                index = int(index)
                if index < len(self.outer.elements):
                    self.outer.elements[int(index)] = value
                else:
                    raise LoxRunTimeError(self.name,"Array index out of range.")
            else:
                raise LoxRunTimeError(self.name,"Array index must be an integer.")
        else:
            self.outer.elements.append(value)

    def arity(self):
        return 2

class _Length(LoxCallable):
    def __init__(self, outer):
        self.outer = outer
    
    def call(self, interpreter, arguments):
        return float(len(self.outer.elements))

    def arity(self):
        return 0