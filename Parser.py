from Consts import Token, Priorities
from CodeGen import CodeGen

# Receives a list of ASTNode
def find_highest_priority(line):
    if not line or len(line) < 1:
        return None
    best = line[0]
    for i in line:
        if i.get_priority() > best.get_priority():
            best = i
    return best


# Receives a list of ASTNode
def parse(line):
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
    raise ValueError("Unknown token: " + str(token))


def binary_operator_factory(operator):
    return BinaryOperator(operator)


def unary_operator_factory(operator):
    if operator in Priorities.left_value_unary_op.keys():
        return LValueUnaryOperator(operator)
    return RValueUnaryOperator(operator)


class ASTNode:
    def __init__(self, priority, action):
        self.priority = priority
        self.params = []
        self.action = action
    
    def get_priority(self): return self.priority
        
    def parse(self, line):
        raise NotImplementedError("parse method is abstract in the ASTNode class")

    def __str__(self):
        return str(self.action)

    def generate_code(self, code_generator):
        return ""
        raise NotImplementedError("generate_code method is abstract in the ASTNode class")


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
            code_generator.write_code("pop [" + self.params[0].get_name(code_generator) + "]")
            return
        if self.action in ['+', '-', '*']:
            self.params[0].generate_code(code_generator)
            self.params[1].generate_code(code_generator)
            code_generator.write_code("pop rbx")
            code_generator.write_code("pop rax")
            code_generator.write_code(["add", "sub", "imul"][['+', '-', '*'].index(self.action)] + " rax, rbx")
            code_generator.write_code("push rax")
            return
        if '/' == self.action:
            self.params[0].generate_code(code_generator)
            self.params[1].generate_code(code_generator)
            code_generator.write_code("mov EDX, 0")
            code_generator.write_code("mov ax, 0")
            code_generator.write_code("mov bx, 0")
            code_generator.write_code("pop rbx")
            code_generator.write_code("pop rax")
            code_generator.write_code("div ebx")
            code_generator.write_code("push rbx")
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
    def __init__(self, action):
        ASTNode.__init__(self, Priorities.right_value_unary_op[action], action)

    def get_name(self, code_generator):
        self.generate_code(code_generator)
        return self.params[0].action

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        self.params[0].parse(line[line.index(self) + 1:])

    def generate_code(self, code_generator):
        if self.action == "int":
            if type(self.params[0]) is Identifier:
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

    def get_name(self, code_generator):
        return self.action

    def generate_code(self, code_generator):
        code_generator.write_code("push " + self.action)
        return self.action
