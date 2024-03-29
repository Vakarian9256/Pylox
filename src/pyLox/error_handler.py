'''
The module houses the definition of the error handler, whose job is to monitor if a parsing or a runtime error occured and report them to the user.
'''
import sys
from token import Token
from token_type import TokenType
from error import LoxRunTimeError

class ErrorHandler:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
    
    def error(self, line: int, message: str):
        self.report(line, "", message)
    
    def error_on_token(self, token: Token, message: str):
        if token.type_ == TokenType.EOF:
            self.report(token.line, " at end ", message)
        else:
            self.report(token.line, f" at '{token.lexeme}'", message)

    def runtime_error(self, error: LoxRunTimeError):
        print(f"[line {error.token.line}] Error at '{error.token.lexeme}' : {str(error)}")
        self.had_runtime_error = True
        
    def report(self, line: int, where: str, message: str):
        print (f"[line {line}] Error {where}: {message}")
        self.had_error = True   