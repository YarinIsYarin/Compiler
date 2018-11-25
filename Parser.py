from Consts import Token, Priorities


# Receives a list of ASTNode
def find_highest_priority(line):
    if not line or len(line) < 1:
        return None
    line.reverse()
    best = line[0]
    for i in line:
        if i.get_priority() > best.get_priority():
            best = i
    line.reverse()
    return best


# Receives a list of ASTNode
def parse(line):
    if len(line) > 1:
        prev = None
        # Deal with thing like [3]
        for word in line:
            if BracketsBlock == type(word): #and type(prev) == RValueUnaryOperator:
                prev.add_data(word.data)
                line.remove(word)
                word = None
            if word:
                prev = word
    if line:
        root = find_highest_priority(line)
        root.parse(line)
        return root
    

def ast_node_factory(token, data):
    if token == Token.binary_op:
        return binary_operator_factory(data)
    if token == Token.unary_op:
        return unary_operator_factory(data)
    if token == Token.identifier:
        return Identifier(data)
    if token == Token.immediate:
        return Immediate(data)
    if token == Token.parentheses_block:
        return ParenthesesBlock(data)
    if token == Token.brackets_block:
        return BracketsBlock(ast_node_factory(Token.parentheses_block, data))
    raise ValueError("Unknown token: " + str(token))


def binary_operator_factory(operator):
    return BinaryOperator(operator)


def unary_operator_factory(operator):
    if operator in Priorities.left_value_unary_op.keys():
        return LValueUnaryOperator(operator)
    return RValueUnaryOperator(operator)


class ASTNode:
    def __init__(self, priority, action, additonal_data=None):
        self.priority = priority
        self.params = []
        self.action = action
        self.additional_data = additonal_data
    
    def get_priority(self): return self.priority
        
    def parse(self, line):
        raise NotImplementedError("parse method is abstract in the ASTNode class")

    def __str__(self):
        return str(self.action)

    def generate_code(self, code_generator):
        return ""
        raise NotImplementedError("generate_code method is abstract in the ASTNode class")


class BracketsBlock():
    def __init__(self, data):
        self.data = data


class ParenthesesBlock(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, "")
        self.params = [ast_node_factory(i[0], i[1]) for i in action]

    def parse(self, line):
        self.params = [parse(self.params)]

    def generate_code(self, code_generator):
        return self.params[0].generate_code(code_generator)


class BinaryOperator(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, Priorities.binary_op[action], action)

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[:line.index(self)]))
        self.params[0].parse(line[:line.index(self)])
        self.params.append(find_highest_priority(line[line.index(self)+1:]))
        self.params[1].parse(line[line.index(self)+1:])

    def generate_code(self, code_generator):
        if "=" == self.action:
            self.params[1].generate_code(code_generator)
            code_generator.write_code("pop " + self.params[0].get_name(code_generator))
            return
        if self.action in ['+', '-', '*']:
            self.params[1].generate_code(code_generator)
            self.params[0].generate_code(code_generator)
            code_generator.write_code("pop rax")
            code_generator.write_code("pop rbx")
            code_generator.write_code(["add", "sub", "imul"][['+', '-', '*'].index(self.action)] + " rax, rbx")
            code_generator.write_code("push rax")
            return
        if '/' == self.action:
            self.params[0].generate_code(code_generator)
            self.params[1].generate_code(code_generator)
            code_generator.write_code("mov edx, 0")
            code_generator.write_code("mov ax, 0")
            code_generator.write_code("mov bx, 0")
            code_generator.write_code("pop rbx")
            code_generator.write_code("pop rax")
            code_generator.write_code("div ebx")
            code_generator.write_code("push rax")
            return

        print("Error: unknown binary operator")


# Operators who receive their parameters on the left, such as x++
class LValueUnaryOperator(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(Priorities.left_value_unary_op[action], action)

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[:line.index(self)]))
        self.params.append(parse(line[:line.index(self)]))


# Operators who receive their parameters on the right, such as ++x and int
class RValueUnaryOperator(ASTNode):
    def __init__(self, action, additional_data=None):
        ASTNode.__init__(self, Priorities.right_value_unary_op[action], action, additional_data)

    # To add parameters such as []
    def add_data(self, new_data):
        self.additional_data = new_data

    def get_name(self, code_generator):
        self.generate_code(code_generator)
        return self.params[0].get_name(code_generator)

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        self.params[0].parse(line[line.index(self) + 1:])

    def generate_code(self, code_generator):
        if self.action == "int":
            if type(self.params[0]) is Identifier:
                # If this is an array
                if self.additional_data:
                    code_generator.write_data(self.params[0].action + " qword " +\
                                              str(self.additional_data.params[0]) + " dup (0)")
                    var_name = self.params[0].action
                    code_generator.known_vars.append((self.params[0].action, "int[]"))
                    return var_name
                code_generator.write_data(self.params[0].action + " qword 0")
                var_name = self.params[0].action
                code_generator.known_vars.append(self.params[0].action)
                return var_name
            print("Error: " + self.params[0].action + " is not a valid int name")


class Immediate(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)

    def parse(self, line):
        pass

    def generate_code(self, code_generator):
        code_generator.write_code("push " + self.action)


class Identifier(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)

    def parse(self, line):
        pass

    def add_data(self, data):
        self.additional_data = data

    def get_name(self, code_generator):
        if self.additional_data:
            self.additional_data.parse([self.additional_data])
            self.additional_data.generate_code(code_generator)
            code_generator.write_code("pop rbx")
            code_generator.write_code("imul rbx, 8")
            return "[" + self.action + " + rbx]"
        return self.action

    def generate_code(self, code_generator):
        if self.additional_data:
            self.additional_data.parse([self.additional_data])
            self.additional_data.generate_code(code_generator)
            code_generator.write_code("pop rbx")
            code_generator.write_code("imul rbx, 8")
            code_generator.write_code("push [" + self.action + " + rbx]")
        else:
            code_generator.write_code("push " + self.action)
        return self.action
