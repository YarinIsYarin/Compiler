from enum import Enum, auto
import re


class Token(Enum):
    new_line = auto()
    dec = auto()
    num = auto()
    binary_op = auto()
    identifier = auto()
    eof = auto()


def lex(file_name):
    source = open(file_name, 'r')
    text = read_word(source.read())
    for word in text:
        if word == "\n":
            yield (Token.new_line)
        elif word == "int":
            yield (Token.dec)
        elif re.match("\\d+", word):
            yield (Token.num, word)
        elif re.match("[-,+,*,//]", word):
            yield (Token.binary_op, word)
        else:
            yield (Token.identifier, word)
    yield (Token.eof)


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
