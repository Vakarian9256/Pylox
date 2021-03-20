'''
The module serves as the interpreter for the Lox language.
There are two modes to run the interpreter in:
1. REPL - by running the interpreter without an argument, you can enter statements, which will be executed, and expressions which will be evaluated
          and displayed to the user on the terminal.
2. Source - by passing a source file as a command line argument, the interpreter will execute all statements and expressions in the source file.
The interpreter has 4 stages:
1. The scanner scans the source file and creates a list of tokens based on the input.
2. The parser parses the tokens into statements and expressions.
3. The resolver performs semantic analysis on the statements and expressions, such as resolving variable - tracking down to which declaration
   a variable refers to.
4. The interpreter executes the statements and expressions.
'''
import sys
import argparse
from run_mode import RunMode as mode
from error_handler import ErrorHandler
from scanner import Scanner
from Lox_parser import Parser
from interpreter import Interpreter
from resolver import Resolver


class Lox:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.interpreter = Interpreter(self.error_handler)
    
    # Runs the interpreter with a source file.
    def run_file(self, path: str):
        with open(path, "r") as f:
            self.run("".join(f.readlines()), mode.FILE)
            if self.error_handler.had_error or self.error_handler.had_runtime_error:
                sys.exit()

    # Runs the interpreter in REPL mode.
    def run_prompt(self):
        try:
            while True:
                self.run(input(">"), mode.REPL)
                self.error_handler.had_error = False
                self.error_handler.had_runtime_error = False
        except KeyboardInterrupt:
            print ("\nKeyboard interrupt.")

    # This functions performs the 4 passes: scanning, parsing, resolving & binding, and interpreting.
    def run(self, source: str, mode):
        scanner = Scanner(self.error_handler, source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, self.error_handler)
        statements = parser.parse()
        if self.error_handler.had_error == True:
            return 
        resolver = Resolver(self.interpreter, self.error_handler)
        resolver.resolve_list(statements)
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
