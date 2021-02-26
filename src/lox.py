import sys
from error_handler import ErrorHandler
from scanner import Scanner
from lox_parser import Parser
from ast_printer import AstPrinter
from interpreter import Interpreter

class Lox:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.interpreter = Interpreter(self.error_handler)
    
    def run_file(self, path: str):
        with open(path, "r") as f:
            self.run(self, "".join(f.readlines()))
            if self.error_handler.had_error:
                exit()
            if self.error_handler.had_runtime_error:
                exit()

    def run_prompt(self):
        try:
            while True:
                self.run(input(">"))
                self.error_handler.had_error = False
        except KeyboardInterrupt:
            print ("\n Keyboard interrupt")

    def run(self, source: str):
        scanner = Scanner(self.error_handler, source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, self.error_handler)
        expression = parser.parse()
        if self.error_handler.had_error == True:
            return 
        self.interpreter.interpret(expression)


        


if __name__ == "__main__":
    lox = Lox()
    if  len(sys.argv) > 2:
        print ("Usage: pylox [script]")
    elif len(sys.argv) == 2:
        lox.run_file(sys.argv[1])
    else:
        lox.run_prompt()
    asdas