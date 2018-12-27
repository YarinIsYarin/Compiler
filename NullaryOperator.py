from Parser import *
import Parser
import Consts


class ParenthesesBlock(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, "")
        self.params = [Parser.ast_node_factory(i[0], i[1]) for i in action]

    def parse(self, line):
        self.params = [Parser.parse(self.params)]

    def generate_code(self):
        return self.params[0].generate_code()

    def __str__(self):
        return str(self.params[0])

class BracketsBlock:
    def __init__(self, data):
        self.data = Parser.ast_node_factory(Token.parentheses_block, data)

def NullaryOperator_factory(token, data):
    if token == Token.identifier:
        return Identifier(data)
    if token == Token.immediate:
        return Immediate(data)
    if token == Token.parentheses_block:
        return ParenthesesBlock(data)
    if token == Token.brackets_block:
        return BracketsBlock(data)




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
        if self.additional_data and Consts.compiler.known_vars[self.action] != "int[]":
            Consts.compiler.write_error(self.action + " is not an array")
            return self.action
        if self.additional_data:
            self.additional_data.parse([self.additional_data])
            self.additional_data.generate_code()
            Consts.compiler.write_code("pop rbx")
            Consts.compiler.write_code("imul rbx, 8")
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
            self.additional_data.generate_code()
            Consts.compiler.write_code("pop rbx")
            Consts.compiler.write_code("imul rbx, 8")
            Consts.compiler.write_code("push [" + self.action + " + rbx]")
        else:
            Consts.compiler.write_code("push " + self.action)
        return self.action


