from Parser import ASTNode, find_highest_priority
from Consts import Priorities, Types
from NullaryOperator import Identifier, ParenthesesBlock
import Consts


def UnaryOperator_factory(data):
    if "int" == data:
        return IntDeclaration(data)
    if "boolean" == data:
        return BooleanDeclaration(data)
    if "if" == data:
        return If(data)
    if "while" == data:
        return While(data)
    if "return" == data:
        return Return(data)
    if data in ["++", "--"]:
        return BasicLValue(data)


# Abstract class for operators who receive their parameters on the left, such as x++
class LValueUnaryOperator(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, Priorities.left_value_unary_op[action], action)

    # Receives a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[:line.index(self)]))
        self.params[0].parse(line[:line.index(self)])


# Abstract class for operators who receive their parameters on the right
class RValueUnaryOperator(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, Priorities.right_value_unary_op[action], action)

    # Receives a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        if len(self.params) < 1 or not self.params[0]:
            Consts.compiler.write_error(self.action + " requires 1 argument")
            return
        self.params[0].parse(line[line.index(self) + 1:])


class If(RValueUnaryOperator):
    def __init__(self, action):
        RValueUnaryOperator.__init__(self, action)

    def generate_code(self):
        Consts.compiler.which_block_am_i.append(Consts.Blocks.if_block)
        if type(self.params[0]) is not ParenthesesBlock:
            Consts.compiler.write_error("Condition must be in parentheses")
        if self.params[0].get_return_type() != Types.boolean_type:
            Consts.compiler.write_error("Condition must be boolean")
        self.params[0].generate_code()
        Consts.compiler.write_code("pop rax")
        Consts.compiler.write_code("cmp al, 0")
        end_of_if = Consts.compiler.label_gen()
        Consts.compiler.write_code("je " + end_of_if)
        Consts.compiler.gen_at_end_of_block(end_of_if + ":")

    def get_return_type(self):
        return Types.void


class While(RValueUnaryOperator):
    def __init__(self, action):
        RValueUnaryOperator.__init__(self, action)

    def generate_code(self):
        if type(self.params[0]) is not ParenthesesBlock:
            Consts.compiler.write_error("Condition must be in parentheses")
        if self.params[0].get_return_type() != Types.boolean_type:
            Consts.compiler.write_error("Condition must be boolean")
        Consts.compiler.which_block_am_i.append(Consts.Blocks.while_block)
        start_of_loop = Consts.compiler.label_gen()
        end_of_loop = Consts.compiler.label_gen()
        Consts.compiler.write_code("jmp " + end_of_loop)
        Consts.compiler.write_code(start_of_loop + ":")
        gen_at_end_of_block = [end_of_loop + ":", self.params[0], "pop rax", "cmp al, 0", "jne " + start_of_loop]
        Consts.compiler.gen_at_end_of_block(gen_at_end_of_block)

    def get_return_type(self):
        return Types.void


class Declaration(RValueUnaryOperator):
    def __init__(self, action):
        RValueUnaryOperator.__init__(self, action)

    def get_return_type(self):
        return Types.void

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        if len(self.params) < 1 or not self.params[0]:
            Consts.compiler.write_error(self.action + " missing a name")
            return
        self.params[0].parse(line[line.index(self) + 1:])

    def get_name(self):
        self.generate_code()
        if self.params[0]:
            return "[rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "]"


class IntDeclaration(Declaration):
    def __init__(self, action):
        Declaration.__init__(self, action)

    def get_size(self):
        return Consts.sizes[Types.int_type]

    def get_type(self):
        return Types.int_type

    def generate_code(self):
        if type(self.params[0]) is Identifier:
            var_name = self.params[0].action
            if var_name in Consts.compiler.known_vars:
                Consts.compiler.write_error(var_name + " is already defined")
            Consts.compiler.known_vars[self.params[0].action] = Types.int_type
            Consts.compiler.stack_used[-1] += Consts.get_size(Types.int_type)
            Consts.compiler.where_on_stack[-1][self.params[0].action] = Consts.compiler.stack_used[-1]
            return "[rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "]"
        if self.params[0]:
            Consts.compiler.write_error(self.params[0].action + " is not a valid var name")


class BooleanDeclaration(Declaration):
    def __init__(self, action):
        Declaration.__init__(self, action)

    def get_size(self):
        return Consts.sizes[Types.boolean_type]

    def get_type(self):
        return Types.boolean_type

    def generate_code(self):
        if type(self.params[0]) is Identifier:
            var_name = self.params[0].action
            if var_name in Consts.compiler.known_vars:
                Consts.compiler.write_error(var_name + " is already defined")
            Consts.compiler.known_vars[self.params[0].action] = Types.boolean_type
            Consts.compiler.stack_used[-1] += Consts.get_size(Types.boolean_type)
            Consts.compiler.where_on_stack[-1][self.params[0].action] = Consts.compiler.stack_used[-1]
            return "[rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "]"
        if self.params[0]:
            Consts.compiler.write_error(self.params[0].action + " is not a valid boolean name")


class ArrayDeclaration(Declaration):
    # var_type is the type of the the array, for example int[] is int
    def __init__(self, action, var_type, index):
        Declaration.__init__(self, action)
        self.var_type = var_type
        self.index = index

    def get_size(self):
        return Consts.sizes[Types.pointer]

    def get_type(self):
        return [self.var_type]

    def get_name(self):
        self.generate_code()
        if self.params[0]:
            return "[rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "]"

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        if len(self.params) < 1 or not self.params[0]:
            Consts.compiler.write_error(self.action + " missing a name")
            return
        self.params[0].parse(line[line.index(self) + 1:])

    def generate_code(self):
        if True:
            if type(self.params[0]) is Identifier:
                var_name = self.params[0].action
                if var_name in Consts.compiler.known_vars:
                    Consts.compiler.write_error(var_name + " is already defined")
                if self.index.get_return_type() != Types.int_type:
                    Consts.compiler.write_error("Array size must be int")
                Consts.compiler.known_vars[self.params[0].action] = [self.var_type]
                Consts.compiler.stack_used[-1] += Consts.get_size([self.var_type])
                Consts.compiler.where_on_stack[-1][self.params[0].action] = Consts.compiler.stack_used[-1]
                Consts.compiler.write_code(
                    "mov [rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "] , rcx")
                self.index.generate_code()
                Consts.compiler.write_code("pop rax")
                Consts.compiler.write_code("imul rax, " + str(Consts.get_size([self.var_type])))
                Consts.compiler.write_code("add rcx, rax")
                return "[rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "]"
            if self.params[0]:
                Consts.compiler.write_error(self.params[0].action + " is not a valid int name")


class IntDeclaration(Declaration):
    def __init__(self, action, additional_data=None):
        RValueUnaryOperator.__init__(self, action)

    def get_size(self):
        return Consts.sizes[Types.int_type]

    def get_type(self):
        return Types.int_type

    def get_return_type(self):
        return Types.void

    def get_name(self):
        self.generate_code()
        if self.params[0]:
            return "[rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "]"

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
                Consts.compiler.known_vars[self.params[0].action] = Types.int_type
                Consts.compiler.stack_used[-1] += 8
                Consts.compiler.where_on_stack[-1][self.params[0].action] = Consts.compiler.stack_used[-1]
                return "[rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "]"
            if self.params[0]:
                Consts.compiler.write_error(str(self.params[0].action) + " is not a valid int name")


class ArrayDeclaration(Declaration):
    # var_type is the type of the the array, for example int[] is int
    def __init__(self, action, var_type, index):
        RValueUnaryOperator.__init__(self, action)
        self.var_type = var_type
        self.index = index

    def get_size(self):
        return Consts.sizes[Types.pointer]

    def get_type(self):
        return [self.var_type]

    def get_name(self):
        self.generate_code()
        if self.params[0]:
            return "[rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "]"

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        if len(self.params) < 1 or not self.params[0]:
            Consts.compiler.write_error(self.action + " missing a name")
            return
        self.params[0].parse(line[line.index(self) + 1:])

    def generate_code(self):
        if True:
            if type(self.params[0]) is Identifier:
                var_name = self.params[0].action
                if var_name in Consts.compiler.known_vars:
                    Consts.compiler.write_error(var_name + " is already defined")
                if self.index.get_return_type() != Types.int_type:
                    Consts.compiler.write_error("Array size must be int")
                Consts.compiler.known_vars[self.params[0].action] = [self.var_type]
                Consts.compiler.stack_used[-1] += Consts.get_size(Types.pointer)
                Consts.compiler.where_on_stack[-1][self.params[0].action] = Consts.compiler.stack_used[-1]
                Consts.compiler.write_code(
                    "mov [rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "] , rcx")
                self.index.generate_code()
                Consts.compiler.write_code("pop rax")
                Consts.compiler.write_code("imul rax, " + str(Consts.get_size([self.var_type])))
                Consts.compiler.write_code("add rcx, rax")
                return "[rbp - " + str(Consts.compiler.get_var_stack_place(self.params[0].action)) + "]"
            if self.params[0]:
                Consts.compiler.write_error(self.params[0].action + " is not a valid int name")


# For ++ and --
class BasicLValue(LValueUnaryOperator):
    def __init__(self, data):
        LValueUnaryOperator.__init__(self, data)

    def generate_code(self):
        if 1 != len(self.params):
            return
        if not isinstance(self.params[0], Identifier):
            Consts.compiler.write_error("Can't change the value of " + str(self.params[0]))
            return
        if self.params[0].get_return_type() not in [Types.int_type]:
            Consts.compiler.write_error("Cannot increment this type")
            return
        if self.params[0]:
            self.params[0].generate_code()
            Consts.compiler.write_code("pop rax")
            Consts.compiler.write_code({"++": "inc", "--": "dec"}[self.action] + " rax")
            Consts.compiler.write_code("mov " + self.params[0].get_name() + ", rax")

    def get_return_type(self):
        return Types.void


class Return(RValueUnaryOperator):
    def __init__(self, action):
        RValueUnaryOperator.__init__(self, action)

    def generate_code(self):
        print("here")
        self.params[0].generate_code()
        if not Consts.compiler.in_func:
            Consts.compiler.write_error("Return must be in function")
            return
        if Consts.type_to_string(self.get_return_type()) != Consts.compiler.known_funcs[Consts.compiler.in_func]:
            Consts.compiler.write_error("Function should return " +
                                        Consts.compiler.known_funcs[Consts.compiler.in_func]
                                        + " and not " + str(self.get_return_type()))
        if self.get_return_type() != Consts.Types.void:
            # We return the value the function calculated in rbx
            Consts.compiler.write_code("pop rbx")
        Consts.compiler.write_code("mov rax, [rbp - 8]\njmp rax")

    def get_return_type(self):
        return self.params[0].get_return_type()
