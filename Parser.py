from Consts import Token, Priorities


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
        raise NotImplementedError("parse method is abstract in the Operator class")

    def __str__(self):
        return str(self.action)


class BinaryOperator(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, Priorities.binary_op[action], action)

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[:line.index(self)]))
        self.params[0].parse(line[:line.index(self)])
        self.params.append(find_highest_priority(line[line.index(self)+1:]))
        self.params[1].parse(line[line.index(self)+1:])


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

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        self.params[0].parse(line[line.index(self) + 1:])


class Immediate(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)

    def parse(self, line):
        pass


class Identifier(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)

    def parse(self, line):
        pass
