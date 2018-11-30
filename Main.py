from Lexer import lex
import Consts
import Parser
import Compiler

output = Compiler.Compiler("output", "input")
Parser.compiler = output
lines = []
curr_line = []
comment_flag = False
# This flag will be used to know if we are counting the indent of the line
stat_of_line_flag = True
indent = 0
# Go over the input file and turn it into an ast tree
for word in lex(open("input.txt", 'r').read(), output):
    if word[0] != Consts.Token.new_line:
        if not comment_flag:
            #print(word) #deb
            if Consts.Token.space != word[0]:
                stat_of_line_flag = False
            if Consts.Token.space == word[0] and stat_of_line_flag:
                indent += 1
            if Consts.Token.comment == word[0]:
                comment_flag = True
            elif Consts.Token.space != word[0]:
                curr_line.append(Parser.ast_node_factory(word[0], word[1]))
    else:
        lines.append((int(indent / 4), Parser.parse(curr_line)))
        stat_of_line_flag = True
        indent = 0
        #print("line " + str(output.line_number) + " is: " + str([str(i) for i in curr_line])) # For debugging
        output.next_line()
        curr_line = []
        comment_flag = False

output.line_number = 0
for line in lines:
    output.next_line(line[0])
    if line[1]:
        line[1].generate_code(output)
output.generate_code()
if output.errors > 0:
    print("File had " + str(output.errors) + " errors")
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
    dfs(line[1])
    print()'''
