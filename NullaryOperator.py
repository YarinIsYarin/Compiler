from Parser import *
import Parser
from Consts import Priorities
import Consts


def NullaryOperator_factory(token, data):
    if token == Token.identifier:
        return Identifier(data)
    if token == Token.immediate:
        return Immediate(data)
    if token == Token.parentheses_block:
        return ParenthesesBlock(data)
    if token == Token.brackets_block:
        return BracketsBlock(ast_node_factory(Token.parentheses_block, data))


class Immediate(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)

    def parse(self, line):
        pass

    def generate_code(self):
        Consts.compiler.write_code("push " + self.action)


class Identifier(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)

    def parse(self, line):
        pass

    def add_data(self, data):
        self.additional_data = data

    def get_name(self):
        if self.action not in Consts.compiler.known_vars:
            Consts.compiler.write_error("Unknown variable " + self.action)
            return self.action
        if self.additional_data and Consts.compiler.code_gen.known_vars[self.action] != "int[]":
            Consts.compiler.write_error(self.action + " is not an array")
            return self.action
        if self.additional_data:
            self.additional_data.parse([self.additional_data])
            self.additional_data.generate_code()
            Consts.compiler.code_gen.write_code("pop rbx")
            Consts.compiler.code_gen.write_code("imul rbx, 8")
            return "[" + self.action + " + rbx]"
        return self.action

    def generate_code(self):
        if self.action not in Consts.compiler.known_vars:
            Consts.compiler.write_error("Unknown variable " + self.action)
            return self.action
        if self.additional_data and Consts.compiler.known_vars[self.action] != "int[]":
            Consts.compiler.write_error(self.action + " is not an array")
            return self.action
        if self.additional_data:
            self.additional_data.parse([self.additional_data])
            self.additional_data.generate_code(Consts.compiler)
            Consts.compiler.write_code("pop rbx")
            Consts.compiler.write_code("imul rbx, 8")
            Consts.compiler.write_code("push [" + self.action + " + rbx]")
        else:
            Consts.compiler.write_code("push " + self.action)
        return self.action
