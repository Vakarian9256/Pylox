import sys
import argparse
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
            self.run("".join(f.readlines()))
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
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("script", nargs='?', type=str , default=None,  
                            help="The path to the source file to be interpreted."+
                            "Path needs to be encapsulated with quotation marks.")
    args = arg_parser.parse_args()
    if args.script is not None:
        lox.run_file(args.script)
    else:
        lox.run_prompt()