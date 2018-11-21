from Consts import Token, Priorities
import re


def lex(file_name):
    source = open(file_name, 'r')
    text = read_word(source.read())
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
        else:
            yield (Token.identifier, word)
    # This line ensures that every file ends in a blank line,
    # There we can detect end of lines by a '\n'
    yield (Token.new_line, "\n")


# Reads a text word by word
def read_word(text):
    word = ""
    for char in text:
        if char == " ":
            if word != "":
                yield word
                word = ""
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
