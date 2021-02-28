import sys
from token import Token

class LoxRunTimeError(RuntimeError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token

class DivisionByZeroError(LoxRunTimeError):
    def __init__(self, token: Token):
        super().__init__("Division by zero.")

class BreakException(Exception):
    def __init__(self):
        pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
