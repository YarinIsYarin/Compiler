from Parser import *
from Consts import Priorities
from NullaryOperator import Identifier
import Consts


def UnaryOperator_factory(data):
    if data in Priorities.left_value_unary_op.keys():
        return LValueUnaryOperator(data)
    if "int" == data:
        return Declaration(data)
    if "if" == data:
        return If(data)
    if "while" == data:
        return While(data)


# Operators who receive their parameters on the left, such as x++
class LValueUnaryOperator(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(Priorities.left_value_unary_op[action], action)

    # Receives a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[:line.index(self)]))
        self.params.append(parse(line[:line.index(self)]))


class RValueUnaryOperator(ASTNode):
    def __init__(self, action, additional_data=None):
        ASTNode.__init__(self, Priorities.right_value_unary_op[action], action, additional_data)

    # Receives a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        if len(self.params) < 1 or not self.params[0]:
            Consts.compiler.write_error(self.action + " requires 1 argument")
            return
        self.params[0].parse(line[line.index(self) + 1:])


class If(RValueUnaryOperator):
    def __init__(self, action, additional_data=None):
        RValueUnaryOperator.__init__(self, action, additional_data)

    def generate_code(self):
        self.params[0].generate_code()
        Consts.compiler.write_code("pop rax")
        Consts.compiler.write_code("cmp rax, 0")
        end_of_if = Consts.compiler.label_gen()
        Consts.compiler.write_code("je " + end_of_if)
        Consts.compiler.gen_at_end_of_block(end_of_if + ":")


class While(RValueUnaryOperator):
    def __init__(self, action, additional_data=None):
        RValueUnaryOperator.__init__(self, action, additional_data)

    def generate_code(self):
        start_of_loop = Consts.compiler.label_gen()
        end_of_loop = Consts.compiler.label_gen()
        Consts.compiler.write_code("jmp " + end_of_loop)
        Consts.compiler.write_code(start_of_loop + ":")
        gen_at_end_of_block = [end_of_loop + ":", self.params[0], "pop rax", "cmp rax, 0", "jne " + start_of_loop]
        Consts.compiler.gen_at_end_of_block(gen_at_end_of_block)


class Declaration(RValueUnaryOperator):
    def __init__(self, action, additional_data=None):
        RValueUnaryOperator.__init__(self, action, additional_data)

    # To add parameters such as []
    def add_data(self, new_data):
        self.additional_data = new_data

    def get_name(self):
        self.generate_code()
        if self.params[0]:
            return self.params[0].get_name()

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        if len(self.params) < 1 or not self.params[0]:
            Consts.compiler.write_error(self.action + " missing a name")
            return
        self.params[0].parse(line[line.index(self) + 1:])

    def generate_code(self):
        if self.action == "int":
            if type(self.params[0]) is Identifier:
                var_name = self.params[0].action
                if var_name in Consts.compiler.known_vars:
                    Consts.compiler.write_error(var_name + " is already defined")
                # If this is an array
                if self.additional_data:
                    Consts.compiler.known_vars[self.params[0].action] = "int[]"
                    Consts.compiler.write_data(self.params[0].action + " qword " +
                                      str(self.additional_data.params[0]) + " dup (0)")
                    var_name = self.params[0].action
                    return var_name
                # Not an array
                Consts.compiler.known_vars[self.params[0].action] = "int"
                Consts.compiler.write_data(self.params[0].action + " qword 0")
                var_name = self.params[0].action
                return var_name
            if self.params[0]:
                Consts.compiler.write_error(self.params[0].action + " is not a valid int name")
