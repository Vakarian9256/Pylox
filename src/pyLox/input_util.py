'''
The module houses 3 utility functions that are used in the Lox Native Library input function - read.
'''
def _typify(string: str):
    print(string)
    if string == 'nil':
        return None
    value = convert_to_number(string)
    if type(value) is float:
        if value.is_integer():
            return int(value)
    return value

def is_digit(char: chr ) -> bool:
        return char >= '0' and char <= '9'

def convert_to_number(string: str):
    index = 0
    while index < len(string) and is_digit(string[index]):
        index += 1
    if index < len(string)-1 and string[index] == '.' and is_digit(string[index+1]):
        index += 1
        while index < len(string) and is_digit(string[index]):
            index += 1
    if index == len(string) and string != '':
        return float(string)
    return string
