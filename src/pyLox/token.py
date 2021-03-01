from token_type import TokenType

class Token():
    def __init__(self, type_: int, lexeme: str, literal: object, line: int):
        self.type_ = type_
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __str__(self) -> str:
        return f"{self.type_} {self.lexeme} {self.literal}"