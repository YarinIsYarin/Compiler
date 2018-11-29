from Lexer import lex
import Consts
import Parser
import Compiler

output = Compiler.Compiler("output", "input")
Parser.compiler = output
lines = []
curr_line = []
comment_flag = False
# Go over the input file and turn it into an ast tree
#[print(i) for i in lex(open("input.txt", 'r').read(), output)]
for word in lex(open("input.txt", 'r').read(), output):
    if word[0] != Consts.Token.new_line:
        if not comment_flag:
            #print(word[1]) #deb
            if Consts.Token.comment == word[0]:
                comment_flag = True
            else:
                curr_line.append(Parser.ast_node_factory(word[0], word[1]))
    else:
        #print("line " + str(output.messages.line_number) + " is: " + str([str(i) for i in curr_line])) # For debugging
        lines.append(Parser.parse(curr_line))
        output.messages.next_line()
        curr_line = []
        comment_flag = False

output.messages.line_number = 0
for line in lines:
    output.messages.next_line()
    if line:
        line.generate_code(output)
output.code_gen.generate_code()
if output.messages.errors > 0:
    print("File had " + str(output.messages.errors) + " errors")
else:
    print("Compiled successfully!")
    #print([i[0] for i in output.code_gen.known_vars])
# For debugging, prints the AST tree of every line
def dfs (root):
    print("{", end='')
    print(str(root), end='')
    if root and len(root.params) > 0:
        dfs(root.params[0])
        if len(root.params) > 1:
            dfs(root.params[1])
    print("}", end='')
'''''
for line in lines:
    dfs(line)
    print()'''
