from Consts import Token, Priorities
import Consts


class ASTNode:
    def __init__(self, priority, action):
        self.priority = priority
        self.params = []
        # action is the actual string given
        self.action = action
        # additional data is for things that can act in different ways
        # and cant be classified as one type of operator such as [7]
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
    #print([str(k) for k in line])
    for i in line:
        if i.get_priority() > best.get_priority():
            best = i
    line.reverse()
    return best


# turns a list of ASTNode into an ast tree
# Returns the root of the tree
from UnaryOperator import Declaration, ArrayDeclaration
from NullaryOperator import Identifier, BracketsBlock, Prefix, ArrayNode


def parse(line):
    if len(line) > 1:
        line_index = 0
        # Deal with things like [3]
        for i in range(len(line)):
            if len(line) > i + 1:
                if isinstance(line[i+1], BracketsBlock):
                    if not isinstance(line[i], Declaration) and not isinstance(line[i], Identifier):
                        Consts.compiler.write_error("Random array index")
                    # Accessing array index
                    if isinstance(line[i], Identifier):
                        line[i] = ArrayNode(line[i], line[i+1].data)
                        line[i+1] = None
                    # Declaring arrays
                    if isinstance(line[i], Declaration):
                        line[i] = ArrayDeclaration(line[i].action, line[i].get_type(), line[i+1].data)
                        line[i+1] = None
    line = [i for i in line if i is not None]
    # Build the AST tree
    if line:
        root = find_highest_priority(line)
        root.parse(line)
        #print("root is: " + root)
        return root


from BinaryOperator import BinaryOperator_factory
from UnaryOperator import UnaryOperator_factory
from NullaryOperator import NullaryOperator_factory


def ast_node_factory(token, data):
    if token == Token.binary_op:
        return BinaryOperator_factory(data)
    if token == Token.unary_op:
        return UnaryOperator_factory(data)
    return NullaryOperator_factory(token, data)
