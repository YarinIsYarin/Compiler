from Lexer import lex
import Consts
import Parser
import CodeGen

code_gen = CodeGen.CodeGen("output")
def dfs (root):
    #root.generate_code(code_gen)
    print("{", end='')
    print(str(root), end='')
    if len(root.params) > 0:
        dfs(root.params[0])
        if len(root.params) > 1:
            dfs(root.params[1])
    print("}", end='')


lines = []
curr_line = []
for word in lex("input.txt"):
    if word[0] != Consts.Token.new_line:
        curr = Parser.ast_node_factory(word[0], word[1])
        curr_line.append(curr)
    else:
        lines.append(Parser.parse(curr_line))
        curr_line = []

for line in lines:
    line.generate_code(code_gen)
    # dfs(line)
    # print("\n")

code_gen.generate_code()
