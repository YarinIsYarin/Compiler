from Lexer import lex
import Consts
import Parser
import CodeGen

code_gen = CodeGen.CodeGen("output")
lines = []
curr_line = []
for word in lex(open("input.txt", 'r').read()):
    # Print(word)
    if word[0] != Consts.Token.new_line:
        #print(word)
        curr_line.append(Parser.ast_node_factory(word[0], word[1]))
    else:
        #print("line is: " + str(curr_line))
        lines.append(Parser.parse(curr_line))
        curr_line = []

for line in lines:
    line.generate_code(code_gen)
code_gen.generate_code()


# For debugging, prints the AST tree of every line
def dfs (root):
    print("{", end='')
    print(str(root), end='')
    if len(root.params) > 0:
        dfs(root.params[0])
        if len(root.params) > 1:
            dfs(root.params[1])
    print("}", end='')

for line in lines:
    dfs(line)
    print()
