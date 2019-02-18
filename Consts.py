# This file contains dictionaries of all the safe words and operators in this language
# When parsing first of all handle the ones with the higher keys
# Note that this file can also be used to tell the type of all the keyword in the language
from enum import Enum, auto

class Token(Enum):
    new_line = auto()
    nullary_op = auto()
    unary_op = auto()
    binary_op = auto()
    immediate = auto()
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
    binary_op = {'+': 40, '-': 40, '*': 20, '/': 20, '=': 100, '-=': 100, '+=': 100, '/=': 100, '*=': 100, "==": 90,
                 ">": 90, "<": 90, ">=": 90, "=>": 90, "<=": 90, "=<": 90, "!=": 90}
    right_value_unary_op = {"int": 10, "if": 100, "elif": 50, "while": 100}
    left_value_unary_op = {"++": 30, "--": 30}
    nullary_op = {"else": 50}
    prefix = ["global"]


class Types(Enum):
    int_type = auto()
    pointer = auto()


compiler = None
def get_size(var_type):
    sizes = {Types.int_type: 8, Types.pointer: 8}
    if isinstance(var_type, list):
        return sizes[Types.pointer]
    return sizes[var_type]
