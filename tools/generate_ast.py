import sys

def define_import(outf):
    outf.write("from abc import ABC, abstractmethod\n")
    outf.write("from token import * \n")
    outf.write("\n")

def define_base_class(outf,base_name):
    outf.write(f"class {base_name}:")
    outf.write("\n")
    outf.write("    pass\n\n")

def define_sub_classes(outf,base_name,types):
    for type_ in types:
        split_str = type_.split(":")
        type_name = split_str[0].strip()
        type_fields = split_str[1].strip()
        define_type(outf, base_name ,type_name, type_fields)
        outf.write("\n")
    

def define_type(outf, base_name, type_name, type_fields):
        outf.write(f"class {type_name}({base_name}):")
        outf.write("\n")
        outf.write(f"    def __init__(self, {type_fields}):")
        outf.write("\n")
        fields = type_fields.split(", ")
        for field in fields:
            field = field.strip()
            outf.write(f"        self.{field} = {field}")
            outf.write("\n")
        outf.write("\n    def accept(self, visitor):\n")
        outf.write(f"        return visitor.visit_{type_name.lower()}_{base_name.lower()}(self,{base_name})\n")

def add_visit(visitor_lines, base_name, types):
    visitor_lines.insert(0, f"from {base_name.lower()} import *\n")
    for type_ in types:
        type_name = type_.split(":")[0].strip()
        visitor_lines.append("    @abstractmethod\n")
        visitor_lines.append(f"    def visit_{type_name.lower()}_{base_name.lower()}(self,{base_name})\n")
        visitor_lines.append("        pass\n\n")

def define_ast(output_dir, base_name, types, visitor_lines):
    path = f"{output_dir}\{base_name.lower()}.py"
    output_file = open(path, mode='w+', encoding='utf-8')
    define_import(output_file)
    define_base_class(output_file,base_name)
    define_sub_classes(output_file, base_name,types)
    add_visit(visitor_lines, base_name, types)
    

def define_visitor(output_dir, visitor_lines):
    visitor = "visitor"
    path = f"{output_dir}\{visitor}.py"
    output_file = open(path, mode='w+', encoding='utf-8')
    define_import(output_file)
    for line in visitor_lines:
        output_file.write(line)
    output_file.close()



def main():
    if len(sys.argv) != 2:
        print ("Usage: generate_ast <output directory>")
        exit(0)
        
    output_dir = sys.argv[1]
    visitor_lines = ["\nclass Visitor(ABC):\n"]
    define_ast(output_dir, "Expr",
               ["Binary : left, operator,  right",
               "Grouping : expression",
               "Literal : value",
               "Unary : operator, right"], visitor_lines)
    define_visitor(output_dir, visitor_lines)

if __name__ == __name__:
    main()