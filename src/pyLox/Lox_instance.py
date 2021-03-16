from token import Token

class LoxInstance():
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name: Token):
        if name.lexeme in self.fields.keys():
            return self.fields.get(name.lexeme)
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise LoxRunTimeError(name,f"Undefined property {name.lexeme}.")

    def set(self, name: Token, value):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"{self.klass.name} instance" 