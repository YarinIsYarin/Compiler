from Parser import *
import Parser
from Consts import Priorities
import Consts
from NullaryOperator import Identifier


def BinaryOperator_factory(data):
    if data in ['+', '-', '*']:
        return BasicArithmeticOperator(data)
    if "=" == data:
        return Equals(data)
    if "/" == data:
        return Division(data)


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

    def generate_code(self):
        raise NotImplementedError("generate_code method is abstract in the BinaryOperator class")


# This class represents all the simple Binary Operator (with are +, -, *)
class BasicArithmeticOperator(BinaryOperator):
    def __init__(self, action):
        BinaryOperator.__init__(self, action)

    def generate_code(self):
        if 2 != len(self.params):
            return
        if self.params[1] is not None:
            self.params[1].generate_code()
        if self.params[0] is not None:
            self.params[0].generate_code()
        Consts.compiler.write_code("pop rax")
        Consts.compiler.write_code("pop rbx")
        Consts.compiler.write_code(["add", "sub", "imul"][['+', '-', '*'].index(self.action)] + " rax, rbx")
        Consts.compiler.write_code("push rax")
        return


class Division(BinaryOperator):
    def __init__(self, action):
        BinaryOperator.__init__(self, action)

    def generate_code(self):
        if 2 != len(self.params):
            return
        if self.params[0] is not None:
            self.params[0].generate_code()
        if self.params[1] is not None:
            self.params[1].generate_code()
        Consts.compiler.write_code("mov edx, 0")
        Consts.compiler.write_code("mov ax, 0")
        Consts.compiler.write_code("mov bx, 0")
        Consts.compiler.write_code("pop rbx")
        Consts.compiler.write_code("pop rax")
        Consts.compiler.write_code("div ebx")
        Consts.compiler.write_code("push rax")
        return


class Equals(BinaryOperator):
    def __init__(self, action):
        BinaryOperator.__init__(self, action)

    def generate_code(self):
        if 2 != len(self.params):
            return
        if not (isinstance(self.params[0], Identifier) or self.params[0].action == "int"):
            Consts.compiler.write_error("Can't change the value of " + str(self.params[0]))
            return
        if self.params[1]:
            self.params[1].generate_code()
            if self.params[0]:
                Consts.compiler.write_code("pop " + str(self.params[0].get_name()))
        return
