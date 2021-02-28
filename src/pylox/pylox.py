import sys
import argparse
from error_handler import ErrorHandler
from scanner import Scanner
from Lox_parser import Parser
from ast_printer import AstPrinter
from interpreter import Interpreter
from run_mode import RunMode as mode

class Lox:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.interpreter = Interpreter(self.error_handler)
    
    def run_file(self, path: str):
        with open(path, "r") as f:
            self.run("".join(f.readlines()), mode.FILE)
            if self.error_handler.had_error or self.error_handler.had_runtime_error:
                sys.exit()

    def run_prompt(self):
        try:
            while True:
                self.run(input(">"), mode.REPL)
                self.error_handler.had_error = False
                self.error_handler.had_runtime_error = False
        except KeyboardInterrupt:
            print ("\nKeyboard interrupt.")

    def run(self, source: str, mode):
        scanner = Scanner(self.error_handler, source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()
        if self.error_handler.had_error == True:
            return 
        self.interpreter.interpret(statements, mode)


        


if __name__ == "__main__":
    Lox = Lox()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("script", nargs='?', type=str , default=None,  
                            help="The path to the source file to be interpreted."+
                            " Path needs to be encapsulated with quotation marks.")
    args = arg_parser.parse_args()
    if args.script is not None:
        Lox.run_file(args.script)
    else:
        Lox.run_prompt()