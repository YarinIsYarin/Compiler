from Lexer import lex
import Consts
import Parser

def dfs (root):
    print("{", end='')
    print(str(root), end='')
    if len(root.params) > 0:
        dfs(root.params[0])
        if len(root.params) > 1:
            dfs(root.params[1])
    print("}", end='')


curr_line = []
root = None

for word in lex("input.txt"):
    if word[0] != Consts.Token.new_line:
        curr = Parser.ast_node_factory(word[0], word[1])
        curr_line.append(curr)
    else:
        root = Parser.parse(curr_line)
        dfs(root)
        print()
        curr_line = []
