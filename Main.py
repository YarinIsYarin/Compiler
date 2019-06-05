from Lexer import lex
from Parser import ast_node_factory, parse
import Compiler
import Consts
import re


Consts.compiler = Compiler.Compiler("output", "input")

# Goes over all of the file and finds the names of all the functions, stores them
# in the format of funcname$type_of_arg1$type_of_arg2... in Compiler.known_funcs
def split_into_funcs(file_name):
    reading_from = open(file_name, 'r+')
    line_number = 0
    curr_line = reading_from.readline()
    while curr_line:
        line_number += 1
        # Search for lines starting with func
        if re.search('^func', curr_line):
            name = re.sub('\s*func\s+\S+\s*', "", curr_line)
            # Remove parameters names
            while name != re.sub('\s+\S+\s*,\s*', ",", name):
                name = re.sub('\s+\S+\s*,\s*', ",", name)
            name = re.sub("\s+\S+\s*\)", ")", name)
            name = re.sub("\)[\s+\S]*", "", name)
            # Replace parentheses and commas with $, for nice output
            name = name.replace('(', "$")
            name = name.replace(',', "$")
            Consts.compiler.known_funcs[name] = curr_line.split()[1]
            Consts.compiler.func_lines[line_number] = name

            # Find the part of the parameters in the function signature
            Consts.compiler.func_declarations[name] = re.search("\(.*\)", curr_line)[0]

            curr_line = reading_from.readline()
        else:
            curr_line = reading_from.readline()
    reading_from.close()


# Dont split into lines
split_into_funcs("input.txt")

lines = []
comment_flag = False
# This flag will be used to know if we are counting the indent of the line
stat_of_line_flag = True
indent = 0
# Go over the input file and turn it into an ast tree
curr_line = []
#print(*lex(open("input.txt", 'r').read(), Consts.compiler))
for word in lex(open("input.txt", 'r').read(), Consts.compiler):
    #print("word is : " + str(word))
    if word[0] != Consts.Token.new_line:
        if not comment_flag:
            # print(word) #deb
            if Consts.Token.space != word[0]:
                stat_of_line_flag = False
            if Consts.Token.space == word[0] and stat_of_line_flag:
                indent += 1
            if Consts.Token.comment == word[0]:
                comment_flag = True
            elif Consts.Token.space != word[0]:
                if word[1] in ["else", "elif"]:
                    indent += Consts.compiler.indent_size
                curr_line.append(ast_node_factory(word[0], word[1]))
    else:
        #print("line " + str(Consts.compiler.line_number) + " is: " + str([str(i) for i in curr_line])) # deb
        lines.append((int(indent / Consts.indent_size), parse(curr_line)))
        stat_of_line_flag = True
        indent = 0
        Consts.compiler.next_line()
        curr_line = []
        comment_flag = False

Consts.compiler.line_number = 0
inp = open("input.txt", 'r')
for i in range(len(lines)):
    line = lines[i]
    #print("line is : " + str(line))
    Consts.compiler.next_line(line[0])
    if line[1]:
        if i+1 in Consts.compiler.func_lines:
            Consts.compiler.write_code("jmp @$$$end_of_code")
            Consts.compiler.write_code("@" + Consts.compiler.func_lines[i+1] + ":")
            Consts.compiler.stack_used.append(8)
            Consts.compiler.in_func = Consts.compiler.func_lines[i+1]
        # Add the matching line from the file
        Consts.compiler.write_code("\t;" + inp.readline()[0:-1])
        line[1].generate_code()
        Consts.compiler.write_code("")
        if i+1 in Consts.compiler.func_lines:
            Consts.compiler.gen_at_end_of_block("mov rax, [rbp - 8]\njmp rax")
            Consts.compiler.stack_used.pop()

    #print(line)
Consts.compiler.generate_code()
if Consts.compiler.errors > 0:
    print("File had " + str(Consts.compiler.errors) + " errors")
else:
    print("Compiled successfully!")


# For debugging, prints the AST tree of every line
def dfs(root):
    print("{", end='')
    print(str(root), end='')
    if root and len(root.params) > 0:
        dfs(root.params[0])
        if len(root.params) > 1:
            dfs(root.params[1])
    print("}", end='')

# For debugging!
if True:
    print("DFS:")
    for i in range(len(lines)):
        line = lines[i]
        dfs(line[1])
        print()

# For debugging
if False:
    print("Funcs names:")
    print(Consts.compiler.known_funcs)
    print(Consts.compiler.func_lines)
    print(Consts.compiler.known_vars)
    print(Consts.compiler.where_on_stack)
    print(Consts.compiler.stack_used)

