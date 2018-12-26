from Consts import Token, Priorities
import Consts


class ASTNode:
    def __init__(self, priority, action, additional_data=None):
        self.priority = priority
        self.params = []
        # action is the actual string given
        self.action = action
        # additional data is for things that can act in different ways
        # and cant be classified as one type of operator such as [7]
        self.additional_data = additional_data

    def get_priority(self): return self.priority

    def add_data(self, data): self.additional_data = data

    def parse(self, line):
        raise NotImplementedError("parse method is abstract in the ASTNode class")

    def __str__(self):
        return str(self.action)

    def generate_code(self):
        return ""
        raise NotImplementedError("generate_code method is abstract in the ASTNode class")


# Receives a list of ASTNode and returns the one we calculate last
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


# turns a list of ASTNode into an ast tree
# Returns the root of the tree
from UnaryOperator import Declaration
def parse(line):
    if len(line) > 1:
        prev = None
        # Deal with thing like [3]
        for word in line:
            # Deal things like x[3] and int[3]
            if BracketsBlock == type(word):
                if Declaration != type(prev) and Identifier != type(prev):
                    Consts.compiler.write_error("Random array index")
                prev.add_data(word.data)
                line.remove(word)
                word = None
            if word:
                prev = word
    if line:
        root = find_highest_priority(line)
        root.parse(line)
        # print("root is: " + str(root))
        return root


class BracketsBlock:
    def __init__(self, data):
        self.data = data


class ParenthesesBlock(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, "")
        self.params = [ast_node_factory(i[0], i[1]) for i in action]

    def parse(self, line):
        self.params = [parse(self.params)]

    def generate_code(self):
        return self.params[0].generate_code()

    def __str__(self):
        return str(self.params[0])

from BinaryOperator import BinaryOperator_factory
from UnaryOperator import UnaryOperator_factory
from NullaryOperator import NullaryOperator_factory


def ast_node_factory(token, data):
    if token == Token.binary_op:
        return BinaryOperator_factory(data)
    if token == Token.unary_op:
        return UnaryOperator_factory(data)
    return NullaryOperator_factory(token, data)



