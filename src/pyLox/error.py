'''
The module houses all of the different exceptions and errors that can be raised during an interpretation of Lox code.
'''
import sys
from token import Token

# An error that is reported in the parsing pass.
class ParseError(RuntimeError):
    def __init__(self, message):
        super().__init__(message)

# An error that is reported in the interpreting pass.
class LoxRunTimeError(RuntimeError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token

# An error that is raised when the interpreter encounters a division by zero.
class DivisionByZeroError(LoxRunTimeError):
    def __init__(self, token: Token):
        super().__init__("Division by zero.")

# An exception that is raised when a break statement is read to escape from the while loop.
class BreakException(Exception):
    def __init__(self):
        pass

# An exception that is raised when a return statement is read to escape from the function body and return the value.
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

