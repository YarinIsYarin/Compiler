# This file contains dictionaries of all the safe words and operators in this language
# When parsing first of all handle the ones with the higher keys
# Note that this file can also be used to tell the type of all the keyword in the language
from enum import Enum, auto


class Token(Enum):
    new_line = auto()
    unary_op = auto()
    binary_op = auto()
    immediate = auto()
    identifier = auto()
    parentheses_block = auto()
    brackets_block = auto()
    eof = auto()
    comment = auto()
    missing_parentheses = auto()


class Priorities:
    binary_op = {'+': 40, '-': 40, '*': 20, '/': 20, '=': 100, }
    right_value_unary_op = {"int": 10}
    left_value_unary_op = {}


