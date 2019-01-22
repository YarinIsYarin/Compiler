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
    if token == token.prefix:
        return Prefix(data)
    if data == "else":
        return Else(data)


class Else(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 50, action)

    def parse(self, line):
        pass

    def generate_code(self):
        if Consts.compiler.which_block_am_i.pop() not in [Consts.Blocks.if_block, Consts.Blocks.elif_block]:
            Consts.compiler.write_error("Else can be applied only to if and elif")
            return
        Consts.compiler.which_block_am_i.append(Consts.Blocks.else_block)
        end_else_label = Consts.compiler.label_gen()
        end_if_label = Consts.compiler.block_stack.pop()
        Consts.compiler.write_code("jmp " + end_else_label)
        Consts.compiler.write_code(end_if_label)
        Consts.compiler.gen_at_end_of_block(end_else_label + ":")


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
        self.isGlobal = False

    def parse(self, line):
        pass

    def add_data(self, data):
        self.additional_data = data

    def set_global(self):
        self.isGlobal = True

    def get_name(self):
        if self.action not in Consts.compiler.known_vars:
            Consts.compiler.write_error("Unknown variable " + self.action)
            return self.action
        if self.additional_data and Consts.compiler.known_vars[self.action] != "int[]":
            Consts.compiler.write_error(self.action + " is not an array")
            return self.action
        var_name = "[rbp - " + str(Consts.compiler.get_var_stack_place(self.action)) + "]"
        if self.additional_data:
            self.additional_data.parse([self.additional_data])
            self.additional_data.generate_code()
            Consts.compiler.write_code("pop rbx")
            Consts.compiler.write_code("imul rbx, 8")
            Consts.compiler.write_code("add rbx, " + var_name)
            return "[rbx]"
        return var_name

    def generate_code(self):
        if self.action not in Consts.compiler.known_vars:
            Consts.compiler.write_error("Unknown variable " + self.action)
            return self.action
        if self.additional_data and Consts.compiler.known_vars[self.action] != "int[]":
            Consts.compiler.write_error(self.action + " is not an array")
            return self.action
        var_name = "[rbp - " + str(Consts.compiler.get_var_stack_place(self.action)) + "]"
        if self.additional_data:
            self.additional_data.parse([self.additional_data])
            self.additional_data.generate_code()
            Consts.compiler.write_code("pop rbx")
            Consts.compiler.write_code("imul rbx, 8")
            Consts.compiler.write_code("add rbx, " + var_name)
            Consts.compiler.write_code("push [rbx]")
        else:
            Consts.compiler.write_code("push " + var_name)
        return var_name

class Prefix:
    def __int__(self, data):
        self.data = data