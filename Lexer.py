import Consts
from Consts import Token, Priorities
import re


# Recursively deal with parentheses
# Returns a list of the lexed data within the parentheses
def lex_with_parentheses(text, char, output):
    closer = {'(': ')', '[': ']'}
    between = []
    count = 1
    # True iff the parenthesis are balanced
    proper_exit = False
    for word in text:
        if char == word:
            count += 1
        if closer[char] == word:
            count -= 1
        if 0 == count:
            proper_exit = True
            break
        between.append(word)
    if not proper_exit:
        Consts.compiler.write_error("Unbalanced " + {"[": "brackets", "(":"parenthesis"}[char])
    return (lex(between, output))





# Generator that returns the values in a file in this format [Token, word]
def lex(source, output):
    text = read_word(source)
    for word in text:
        if word == "\n":
            yield (Token.new_line, "\n")
        elif word in word in Priorities.right_value_unary_op.keys():
            yield (Token.unary_op, word)
        elif re.match("\\d+", word):
            yield (Token.immediate_int, word)
        elif word in ["false", "true"]:
            yield (Token.immediate_boolean, word)
        elif word in Priorities.binary_op.keys():
            yield (Token.binary_op, word)
        elif word in Priorities.nullary_op:
            yield (Token.nullary_op, word)
        elif word in Priorities.prefix:
            yield (Token.prefix, word)
        elif word in ["]", ")"]:
            Consts.compiler.write_error("Unbalanced " + {"]": "brackets", ")":"parenthesis"}[word])
        elif "(" == word:
            yield (Token.parentheses_block, lex_with_parentheses(text, '(', output))
        elif "[" == word:
            try:
                temp = lex_with_parentheses(text, '[', output)
                yield (Token.brackets_block, temp)
            except Exception:
                output.write_error("Missing parentheses")
                yield (Token.immediate_int, "1")
                yield(Token.new_line, "\n")
        elif "//" == word:
            yield (Token.comment, "//")
        elif "eof" == word:
            yield (Token.new_line, "\n")
        elif " " == word:
            yield (Token.space, " ")
        elif "\t" == word:
            print("should not lex tabs")
            for i in range(Consts.size_of_tab):
                yield (Token.space, " ")
        else:
            yield (Token.identifier, word)

def fix_tabs(text):
    for i in text:
        if i != "\t":
            yield i
        else:
            for count in range(Consts.indent_size):
                yield " "

# Reads a text word by word
def read_word(text, in_function_declaration=False):
    # reading something with a few non islanum such as <= and ++
    expr_flag = False
    word = ""
    for char in fix_tabs(text):
        # Ignore lines containing functions declarations
        if Consts.compiler.line_number in Consts.compiler.func_lines and not in_function_declaration:
            if char == "\n":
                # Lex the params in the function signature
                #print(*lex(read_word(Consts.compiler.func_declarations[Consts.compiler.func_lines[Consts.compiler.line_number]]), Consts.Compiler))
                #print(Consts.compiler.func_declarations[Consts.compiler.func_lines[Consts.compiler.line_number]])

                #for i in range(Consts.indent_size):
                #    yield " "
                for i in read_word(Consts.compiler.func_declarations[Consts.compiler.func_lines[Consts.compiler.line_number]][1:-1], in_function_declaration=True):
                    #print("is is " + str(i))
                    yield i
        else:
            # Because /// is also a comment just like //
            if "//" == word:
                yield word
                word = ""
                expr_flag = False

            if char in [" ", "\n", ')', '(', '[', ']', ',', "\t"]:
                if word != "":
                    yield word
                    word = ""
                yield char
                expr_flag = False
            else:
                if expr_flag:
                    if char in ['<', '>', '=', '+', '-', '*', '/', '!']:
                        word += char
                        #print("this word is : |" + word + "|")
                    else:
                        #print("char is : " + char + " word is " + word)
                        if word != "":
                            yield word
                        word = char
                        expr_flag = False
                elif char in ['<', '>', '=', '+', '-', '*', '/', '!']:
                    expr_flag = True
                    if word != "":
                        yield word
                    word = char
                else:
                    word += char
    if word != "":
        yield word
    yield "eof"
