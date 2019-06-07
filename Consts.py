# This file contains dictionaries of all the safe words and operators in this language
# When parsing first of all handle the ones with the higher keys
# Note that this file can also be used to tell the type of all the keyword in the language
from enum import Enum, auto

class Token(Enum):
    new_line = auto()
    nullary_op = auto()
    unary_op = auto()
    binary_op = auto()
    immediate_int = auto()
    immediate_boolean = auto()
    identifier = auto()
    parentheses_block = auto()
    brackets_block = auto()
    eof = auto()
    comment = auto()
    missing_parentheses = auto()
    space = auto()
    prefix = auto()


class Blocks(Enum):
    main_block = auto()
    if_block = auto()
    else_block = auto()
    elif_block = auto()
    while_block = auto()


class Priorities:
    binary_op = {'and': 30, 'or': 40, '+': 40, '-': 40, '*': 20, '/': 20, '=': 100,  "==": 90,
                 ">": 90, "<": 90, ">=": 90, "=>": 90, "<=": 90, "=<": 90, "!=": 90, ",": 120}
    right_value_unary_op = {"boolean": 10, "int": 10, "if": 100, "elif": 50, "while": 100, "return": 150}
    nullary_op = {"else": 50, "main" : 100}
    prefix = ["global"]


class Types(Enum):
    boolean_type = auto()
    int_type = auto()
    pointer = auto()
    void = auto()


compiler = None
frame_size = 32
indent_size = 4
size_of_tab = 4

def get_size(var_type):
    sizes = {Types.int_type: 8, Types.pointer: 8, Types.boolean_type: 1}
    if isinstance(var_type, list):
        return sizes[Types.pointer]
    return sizes[var_type]


def type_to_string(types):
    if type(types) == list:
        if len(types) == 1:
            return type_to_string(types[0]) + "BB"
        ret = ""
        for i in types:
            ret += "$" + type_to_string(i)
        return ret[1:]
    try:
        return {Types.void: "void", Types.boolean_type: "boolean", Types.int_type: "int", Types.pointer: "pointer"}[types]
    except:
        compiler.write_error("Unbalanced parenthesis")
        return ""


def string_to_type(stri):
    if len(stri) >= 2 and stri[-2:] == "BB":
        return [string_to_type(stri[:-2])]
    return {"void": Types.void, "boolean": Types.boolean_type, "int": Types.int_type, "pointer": Types.pointer}[stri]



