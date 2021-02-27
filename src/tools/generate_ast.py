import sys
import argparse
def define_import(outf, base_name: str):
    outf.write("from abc import ABC, abstractmethod\n")
    if base_name == 'Expr':
        outf.write("from typing import Any\n")
    elif base_name == 'Stmt':
        outf.write("from expr import Expr\n")
    if not base_name == 'visitor':
        outf.write("from token import Token \n\n")

def define_base_class(outf, base_name: str):
    outf.write(f"class {base_name}:")
    outf.write("\n")
    outf.write("    pass\n\n")

def define_sub_classes(outf,base_name: str,types: list[str]):
    for type_ in types:
        split_str = type_.split("|")
        type_name = split_str[0].strip()
        type_fields = split_str[1].strip()
        define_type(outf, base_name ,type_name, type_fields)
        outf.write("\n")
    

def define_type(outf, base_name: str, type_name: list[str], type_fields: list[str]):
        outf.write(f"class {type_name}({base_name}):\n")
        outf.write(f"    def __init__(self, {type_fields}):")
        outf.write("\n")
        fields = type_fields.split(", ")
        for field in fields:
            field = field.split(":")
            field_name = field[0].strip()
            outf.write(f"        self.{field_name} = {field_name}")
            outf.write("\n")
        outf.write("\n    def accept(self, visitor) -> str:\n")
        outf.write(f"        return visitor.visit_{type_name.lower()}_{base_name.lower()}(self)\n")

def add_visit(visitor_lines, base_name: str, types: list[str]):
    for type_ in types:
        type_name = type_.split("|")[0].strip()
        visitor_lines.append("    @abstractmethod\n")
        visitor_lines.append(f"    def visit_{type_name.lower()}_{base_name.lower()}(self,{base_name.lower()}:"+
                            f"{type_name}) -> str:\n")
        visitor_lines.append("        pass\n\n")

def define_ast(out_dir, base_name: str, types: list[str], visitor_lines: list[str]):
    path = f"{out_dir}\{base_name.lower()}.py"
    outf = open(path, mode='w+', encoding='utf-8')
    define_import(outf, base_name)
    define_base_class(outf,base_name)
    define_sub_classes(outf, base_name,types)
    visitor_lines.insert(0,f"from {base_name.lower()} import * \n")
    add_visit(visitor_lines, base_name, types)
    

def define_visitor(out_dir, visitor_lines: list[str]):
    visitor = "visitor"
    path = f"{out_dir}\{visitor}.py"
    outf = open(path, mode='w+', encoding='utf-8')
    define_import(outf, visitor)
    for line in visitor_lines:
        outf.write(line)
        if line == visitor_lines[1]:
            outf.write("\n")
    outf.close()



def main():
    '''
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("path", nargs=1, type=str,  
                            help="The path to the directory which will store the written files."+
                            "Path needs to be encapsulated with quotation marks.")
                            '''
    args ="d:/Programming/Crafting Interpreters/Tree Walker/src/pylox"
    visitor_lines = ["\nclass Visitor(ABC):\n"]

    define_ast(args, "Expr",
               ["Asign | name: Token, value: Expr",
                "Binary | left: Expr, operator: Token,  right: Expr",
               "Grouping | expression: Expr",
               "Literal | value: Any",
               "Unary | operator: Token, right: Expr",
               "Conditional | condition: Expr, left: Expr, right: Expr",
               "Variable | name: Token",
               "Logical |  left: Expr, operator: Token, right: Expr"], visitor_lines)

    define_ast(args, "Stmt", [
               "Expression | expr: Expr",
               "Print | expr: Expr",
               "Var | name: Token, initializer: Expr",
               "Block | statements: list[Stmt]",
               "If | condition: Expr, then_branch: Stmt, else_branch: Stmt",
               "While | condition: Expr, body: Stmt"], visitor_lines)

    define_visitor(args, visitor_lines)

if __name__ == "__main__":
    main()