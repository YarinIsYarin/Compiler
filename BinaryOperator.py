from Parser import *
import Parser
from Consts import Priorities, Types
import Consts
from NullaryOperator import Identifier


def BinaryOperator_factory(data):
    if data in ['+', '-', '*']:
        return BasicArithmeticOperator(data)
    if "=" == data:
        return Equals(data)
    if "/" == data:
        return Division(data)
    if "," == data:
        return Comma(data)
    if data in ["==", ">", "<", ">=", "=>", "<=", "=<", "!="]:
        return Compare(data)


class BinaryOperator(Parser.ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, Priorities.binary_op[action], action)

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[:line.index(self)]))
        if self.params[0] is not None:
            self.params[0].parse(line[:line.index(self)])
            self.params.append(find_highest_priority(line[line.index(self)+1:]))
            if self.params[1] is not None:
                self.params[1].parse(line[line.index(self)+1:])
                return

        Consts.compiler.write_error("Binary operator " + self.action + " requires two parameters")

    def get_return_type(self):
        raise NotImplementedError("get_return_type method is abstract in the BinaryOperator class")

    def generate_code(self):
        raise NotImplementedError("generate_code method is abstract in the BinaryOperator class")


# This class represents all the simple Binary Operator (with are +, -, *)
class BasicArithmeticOperator(BinaryOperator):
    def __init__(self, action):
        BinaryOperator.__init__(self, action)

    def generate_code(self):
        if 2 != len(self.params):
            return
        if self.params[1] is None or self.params[0] is None:
            return
        self.params[1].generate_code()
        self.params[0].generate_code()
        if not (self.params[1].get_return_type() == Types.int_type and\
                self.params[1].get_return_type() == Types.int_type):
            Consts.compiler.write_error("Cannot add " + str(self.params[1].get_return_type()) + " and " + str(
                self.params[0].get_return_type()))

        Consts.compiler.write_code(";COMPILING: basic arithmetic of " + str(self.action))
        Consts.compiler.write_code("pop rax")
        Consts.compiler.write_code("pop rbx")
        Consts.compiler.write_code(["add", "sub", "imul"][['+', '-', '*'].index(self.action)] + " rax, rbx")
        Consts.compiler.write_code("push rax")
        return

    def get_return_type(self):
        if self.params[1]:
            return self.params[1].get_return_type()


class Comma(BinaryOperator):
    def __init__(self, action):
        BinaryOperator.__init__(self, action)

    def generate_code(self):
        if 2 != len(self.params):
            Consts.compiler.write_error("Comma must receive two values")
        if self.params[1] is None or self.params[0] is None:
            return
        self.params[0].generate_code()
        self.params[1].generate_code()
        '''
        if self.params[0].get_return_type() == Types.void:
            Consts.compiler.write_error("Comma cannot be applied to void expression " + str(self.params[0]))
        if self.params[1].get_return_type() == Types.void:
            Consts.compiler.write_error("Comma cannot be applied to void expression " + str(self.params[1]))
        '''

    def get_return_type(self):
        if type(self.params[0].get_return_type()) != list:
            #print("is not list " + str(self.params[0].get_return_type()))
            return [self.params[0].get_return_type(), self.params[1].get_return_type()]
        #print("is list " + str(self.params[0].get_return_type()))
        return self.params[0].get_return_type() + [self.params[1].get_return_type()]


class Division(BinaryOperator):
    def __init__(self, action):
        BinaryOperator.__init__(self, action)

    def generate_code(self):
        if 2 != len(self.params):
            return
        if self.params[1] is not None and self.params[0] is not None:
            if self.params[1].get_return_type() == Types.int_type and \
                    self.params[1].get_return_type() == Types.int_type:
                self.params[1].generate_code()
                self.params[0].generate_code()
            else:
                Consts.compiler.write_error("Cannot divide " + str(self.params[1].get_return_type()) + " and " + str(
                    self.params[0].get_return_type()))
        Consts.compiler.write_code(";COMPILING: Division")
        Consts.compiler.write_code("mov edx, 0")
        Consts.compiler.write_code("mov ax, 0")
        Consts.compiler.write_code("mov bx, 0")
        Consts.compiler.write_code("pop rbx")
        Consts.compiler.write_code("pop rax")
        Consts.compiler.write_code("div ebx")
        Consts.compiler.write_code("push rax")

    def get_return_type(self):
        return self.params[1].get_return_type()


# = not ==
class Equals(BinaryOperator):
    def __init__(self, action):
        BinaryOperator.__init__(self, action)

    def generate_code(self):
        if 2 != len(self.params):
            return
        if not (isinstance(self.params[0], Identifier) or isinstance(self.params[0], Declaration)):
            Consts.compiler.write_error("Can't change the value of " + str(self.params[0]))
        if self.params[1].get_return_type() != self.params[0].get_type():
            Consts.compiler.write_error("Both sides must be of the same type")
        self.params[1].generate_code()
        Consts.compiler.write_code(";COMPILING: =")
        if Types.int_type == self.params[0].get_type():
            Consts.compiler.write_code("pop " + str(self.params[0].get_name()))
        if Types.boolean_type == self.params[0].get_type():
            Consts.compiler.write_code("pop rcx")
            Consts.compiler.write_code("mov " + str(self.params[0].get_name()) + ", cl")

    def get_return_type(self):
        return Types.void


class Compare(BinaryOperator):
    def __init__(self, action):
        BinaryOperator.__init__(self, action)

    def generate_code(self):
        if 2 != len(self.params):
            return
        if self.params[0] is not None and self.params[1] is not None:
            if self.params[0].get_return_type() != self.params[0].get_return_type():
                Consts.compiler.write_error("Cannot compare different types")
            # Check that its a type we can compare
            elif self.params[0].get_return_type() not in [Types.int_type]:
                Consts.compiler.write_error("Incomparable type")
            self.params[0].generate_code()
            self.params[1].generate_code()
        Consts.compiler.write_code(";COMPILING:" + str(self.action))
        Consts.compiler.write_code("pop rbx")
        Consts.compiler.write_code("pop rax")
        Consts.compiler.write_code("cmp rax, rbx")
        true = Consts.compiler.label_gen()
        false = Consts.compiler.label_gen()
        Consts.compiler.write_code({">": "jg", "<": "jl", "<=": "jle", "=<": "jle", ">=": "jge",
                                    "=>": "jge", "==": "je", "!=": "jne"}[self.action] + " " + true)
        Consts.compiler.write_code("push 0")
        Consts.compiler.write_code("jmp " + false)
        Consts.compiler.write_code(true + ":")
        Consts.compiler.write_code("push 1")
        Consts.compiler.write_code(false + ":")

    def get_return_type(self):
        return Types.boolean_type
