from Parser import *
import Parser
import Consts
from Consts import Types


class ParenthesesBlock(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, "")
        self.params = [Parser.ast_node_factory(i[0], i[1]) for i in action if i[0] != Token.space]

    def parse(self, line):
        self.params = [Parser.parse(self.params)]

    def generate_code(self):
        return self.params[0].generate_code()

    def get_return_type(self):
        return self.params[0].get_return_type()

    def __str__(self):
        return str(self.params[0])


class BracketsBlock:
    def __init__(self, data):
        self.data = Parser.ast_node_factory(Token.parentheses_block, data)


def NullaryOperator_factory(token, data):
    if token == Token.identifier:
        return Identifier(data)
    if token == Token.immediate_int:
        return ImmediateInt(data)
    if token == Token.immediate_boolean:
        return ImmediateBolean(data)
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

    def get_return_type(self):
        return Types.void


class Immediate(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)

    def parse(self, line):
        pass

    def get_name(self):
        return self.action


class ImmediateBolean(Immediate):
    def __init__(self, action):
        Immediate.__init__(self, action)

    def generate_code(self):
        Consts.compiler.write_code("push " + str({"true": 1, "false": 0}[self.action]))

    def get_return_type(self):
        return Types.boolean_type


class ImmediateInt(Immediate):
    def __init__(self, action):
        Immediate.__init__(self, action)

    def generate_code(self):
        Consts.compiler.write_code("push " + self.action)

    def get_return_type(self):
        return Types.int_type


class Identifier(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)
        self.isGlobal = False

    def parse(self, line):
        pass

    def set_global(self):
        self.isGlobal = True

    def get_name(self):
        if self.action not in Consts.compiler.known_vars:
            Consts.compiler.write_error("Unknown variable " + self.action)
            return self.action
        var_name = "[rbp - " + str(Consts.compiler.get_var_stack_place(self.action)) + "]"
        return var_name

    def generate_code(self):
        if self.action not in Consts.compiler.known_vars:
            Consts.compiler.write_error("Unknown variable " + self.action)
            return self.action
        var_name = "[rbp - " + str(Consts.compiler.get_var_stack_place(self.action)) + "]"
        Consts.compiler.write_code("push " + var_name)
        return var_name

    def get_return_type(self):
        return Consts.compiler.known_vars[str(self)]

    def get_type(self):
        return Consts.compiler.known_vars[str(self)]


class ArrayNode(Identifier):
    def __init__(self, array, index):
        Identifier.__init__(self, array)
        self.arr = array
        self.isGlobal = False
        self.index = index

    def get_name(self):
        if str(self.action.action) not in Consts.compiler.known_vars:
            Consts.compiler.write_error("Unknown variable " + str(self.action))
            return self.action
        self.action.generate_code()
        self.index.generate_code()
        Consts.compiler.write_code("pop rbx")
        Consts.compiler.write_code("pop rax")
        Consts.compiler.write_code("imul rbx, " + str(Consts.get_size(Consts.compiler.known_vars[str(self.action.action)][0])))
        Consts.compiler.write_code("add rbx, rax")
        return "[rbx]"

    def generate_code(self):
        if str(self.action.action) not in Consts.compiler.known_vars:
            Consts.compiler.write_error("Unknown variable " + str(self.action.action))
            return self.action
        self.action.generate_code()
        self.index.generate_code()
        Consts.compiler.write_code("pop rbx")
        Consts.compiler.write_code("pop rax")
        Consts.compiler.write_code("imul rbx, " + str(Consts.get_size(Consts.compiler.known_vars[str(self.action.action)][0])))
        Consts.compiler.write_code("add rbx, rax")
        Consts.compiler.write_code("push [rbx]")

    def parse(self, line):
        self.index.parse(self.index)

    def get_return_type(self):
        return self.arr.get_return_type()[0]

    def get_type(self):
        return self.arr.get_return_type()[0]


class Prefix:
    def __int__(self, data):
        self.data = data
