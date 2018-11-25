from Lexer import lex
import Consts
import Parser
import CodeGen

print("Compiling output.txt...")
code_gen = CodeGen.CodeGen("output")
lines = []
curr_line = []
comment_flag = False
line_num = 1
for word in lex(open("input.txt", 'r').read()):
    if word[0] != Consts.Token.new_line:
        if not comment_flag:
            if Consts.Token.comment == word[0]:
                comment_flag = True
            else:
                curr_line.append(Parser.ast_node_factory(word[0], word[1]))
    else:
        print("line " + str(line_num) + " is: " + str(curr_line)) # For debugging
        line_num += 1
        lines.append(Parser.parse(curr_line))
        curr_line = []
        comment_flag = False

for line in lines:
    if line:
        line.generate_code(code_gen)
code_gen.generate_code()


# For debugging, prints the AST tree of every line
def dfs (root):
    print("{", end='')
    print(str(root), end='')
    if root and len(root.params) > 0:
        dfs(root.params[0])
        if len(root.params) > 1:
            dfs(root.params[1])
    print("}", end='')
'''
for line in lines:
    dfs(line)
    print()'''
