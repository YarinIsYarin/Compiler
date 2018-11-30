from Consts import Token, Priorities
import re


# Recursively deal with parentheses
# Returns a list of the lexed data within the parentheses
def lex_with_parentheses(text, char, output):
    closer = {'(': ')', '[': ']'}
    ret_list = []
    # We will use the stack to the detect were the parentheses end
    stack = [char]
    word = next(text)
    if closer[char] == word:
        stack.pop
    while stack:
        if '\n' == word or "eof" == word:
            raise Exception
        ret_list.append(word)
        word = next(text)
        if char == word:
            stack.append(closer[char])
        if closer[char] == word:
            stack.pop()
    ret_list = [i for i in lex(ret_list, output) if i[0] != Token.new_line]
    return ret_list


# Generator that returns the values in a file in this format [Token, word]
def lex(source, output):
    text = read_word(source)
    for word in text:
        if word == "\n":
            yield (Token.new_line, "\n")
        elif word in Priorities.left_value_unary_op.keys() or \
                word in Priorities.right_value_unary_op.keys():
            yield (Token.unary_op, word)
        elif re.match("\\d+", word):
            yield (Token.immediate, word)
        elif word in Priorities.binary_op.keys():
            yield (Token.binary_op, word)
        elif "(" == word:
            try:
                temp = lex_with_parentheses(text, '(', output)
                #print("tempy " + str(temp))
                yield (Token.parentheses_block, temp)
            except Exception:
                output.messages.write_error("Missing parentheses")
                yield(Token.immediate, "1")
                yield (Token.new_line, "\n")
        elif "[" == word:
            try:
                temp = lex_with_parentheses(text, '[', output)
                yield (Token.brackets_block, temp)
            except Exception:
                print("hell")
                output.messages.write_error("Missing parentheses")
                yield (Token.immediate, "1")
                yield(Token.new_line, "\n")
        elif "#" == word:
            yield (Token.comment, "#")
        elif "eof" == word:
            yield (Token.new_line, "\n")
        elif " " == word:
            yield (Token.space, " ")
        else:
            yield (Token.identifier, word)


# Reads a text word by word
def read_word(text):
    word = ""
    for char in text:
        if char == " ":
            if word != "":
                yield word
                word = ""
            yield " "
        # Deal with things like 3*4
        elif not char.isalnum() and char != "_":
            if word != "":
                yield word
                word = ""
            yield char
            continue
        else:
            word += char
    if word != "":
        yield word
    yield "eof"
