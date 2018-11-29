from Consts import Token, Priorities

compiler = None


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
def parse(line):
    if len(line) > 1:
        prev = None
        # Deal with thing like [3]
        for word in line:
            # Deal things like x[3] and int[3]
            if BracketsBlock == type(word):
                if RValueUnaryOperator != type(prev) and Identifier != type(prev):
                    compiler.messages.write_error("Random array index")
                prev.add_data(word.data)
                line.remove(word)
                word = None
            if word:
                prev = word
    if line:
        root = find_highest_priority(line)
        root.parse(line)
        #print("root is: " + str(root))
        return root
    

def ast_node_factory(token, data):
    if token == Token.binary_op:
        return BinaryOperator(data)
    if token == Token.unary_op:
        if data in Priorities.left_value_unary_op.keys():
            return LValueUnaryOperator(data)
        return RValueUnaryOperator(data)
    if token == Token.identifier:
        return Identifier(data)
    if token == Token.immediate:
        return Immediate(data)
    if token == Token.parentheses_block:
        return ParenthesesBlock(data)
    if token == Token.brackets_block:
        return BracketsBlock(ast_node_factory(Token.parentheses_block, data))
    raise ValueError("Unknown token: " + str(token))


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

    def generate_code(self, output):
        return ""
        raise NotImplementedError("generate_code method is abstract in the ASTNode class")


class BracketsBlock:
    def __init__(self, data):
        self.data = data


class ParenthesesBlock(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, "")
        self.params = [ast_node_factory(i[0], i[1]) for i in action]

    def parse(self, line):
        self.params = [parse(self.params)]

    def generate_code(self, output):
        return self.params[0].generate_code(output)

    def __str__(self):
        return str(self.params[0])


class BinaryOperator(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, Priorities.binary_op[action], action)

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[:line.index(self)]))
        if self.params[0] is not None:
            self.params[0].parse(line[:line.index(self)])
            self.params.append(find_highest_priority(line[line.index(self)+1:]))
            if self.params[1] is not None:
                self.params[1].parse(line[line.index(self)+1:])
                return

        compiler.messages.write_error("Binary operator " + self.action + " requires two parameters")

    def generate_code(self, output):
        if 2 != len(self.params):
            return
        if "=" == self.action:
            if not (isinstance(self.params[0], Identifier) or self.params[0].action == "int"):
                compiler.messages.write_error("Can't change the value of " + str(self.params[0]))
                return
            if self.params[1]:
                self.params[1].generate_code(output)
                if self.params[0]:
                    output.code_gen.write_code("pop " + str(self.params[0].get_name(output)))
            return
        if self.action in ['+', '-', '*']:
            if self.params[1] is not None:
                self.params[1].generate_code(output)
            if self.params[0] is not None:
                self.params[0].generate_code(output)
            output.code_gen.write_code("pop rax")
            output.code_gen.write_code("pop rbx")
            output.code_gen.write_code(["add", "sub", "imul"][['+', '-', '*'].index(self.action)] + " rax, rbx")
            output.code_gen.write_code("push rax")
            return
        if '/' == self.action:
            if self.params[0] is not None:
                self.params[0].generate_code(output)
            if self.params[1] is not None:
                self.params[1].generate_code(output)
            output.code_gen.write_code("mov edx, 0")
            output.code_gen.write_code("mov ax, 0")
            output.code_gen.write_code("mov bx, 0")
            output.code_gen.write_code("pop rbx")
            output.code_gen.write_code("pop rax")
            output.code_gen.write_code("div ebx")
            output.code_gen.write_code("push rax")
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

    def get_name(self, output):
        self.generate_code(output)
        if self.params[0]:
            return self.params[0].get_name(output)

    # Receive a list of ASTNode
    def parse(self, line):
        self.params.append(find_highest_priority(line[line.index(self) + 1:]))
        if len(self.params) < 1 or not self.params[0]:
            compiler.messages.write_error(self.action + " missing a name")
            return
        self.params[0].parse(line[line.index(self) + 1:])

    def generate_code(self, output):
        if self.action == "int":
            if type(self.params[0]) is Identifier:
                var_name = self.params[0].action
                if var_name in compiler.code_gen.known_vars:
                    compiler.messages.write_error(var_name + " is already defined")
                # If this is an array
                if self.additional_data:
                    output.code_gen.known_vars[self.params[0].action] = "int[]"
                    output.code_gen.write_data(self.params[0].action + " qword " +
                                               str(self.additional_data.params[0]) + " dup (0)")
                    var_name = self.params[0].action
                    return var_name
                # Not an array
                output.code_gen.known_vars[self.params[0].action] = "int"
                output.code_gen.write_data(self.params[0].action + " qword 0")
                var_name = self.params[0].action
                return var_name
                return var_name
            if self.params[0]:
                output.messages.write_error(self.params[0].action + " is not a valid int name")


class Immediate(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)

    def parse(self, line):
        pass

    def generate_code(self, output):
        output.code_gen.write_code("push " + self.action)


class Identifier(ASTNode):
    def __init__(self, action):
        ASTNode.__init__(self, 0, action)

    def parse(self, line):
        pass

    def add_data(self, data):
        self.additional_data = data

    def get_name(self, output):
        if self.action not in compiler.code_gen.known_vars:
            output.messages.write_error("Unknown variable " + self.action)
            return self.action
        if self.additional_data and compiler.code_gen.known_vars[self.action] != "int[]":
            compiler.messages.write_error(self.action + " is not an array")
            return self.action
        if self.additional_data:
            self.additional_data.parse([self.additional_data])
            self.additional_data.generate_code(output)
            output.code_gen.write_code("pop rbx")
            output.code_gen.write_code("imul rbx, 8")
            return "[" + self.action + " + rbx]"
        return self.action

    def generate_code(self, output):
        if self.action not in output.code_gen.known_vars:
            output.messages.write_error("Unknown variable " + self.action)
            return self.action
        if self.additional_data and compiler.code_gen.known_vars[self.action] != "int[]":
            compiler.messages.write_error(self.action + " is not an array")
            return self.action
        if self.additional_data:
            self.additional_data.parse([self.additional_data])
            self.additional_data.generate_code(output)
            output.code_gen.write_code("pop rbx")
            output.code_gen.write_code("imul rbx, 8")
            output.code_gen.write_code("push [" + self.action + " + rbx]")
        else:
            output.code_gen.write_code("push " + self.action)
        return self.action
