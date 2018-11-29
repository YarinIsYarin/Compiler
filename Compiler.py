import os


class Compiler:
    def __init__(self, output_name, input_name):
        self.code_gen = CodeGen(output_name)
        self.messages = CompilingMessages(output_name, input_name)


class CompilingMessages:
    def __init__(self, output_name, input_name):
        self.lines = open(input_name + '.txt').readlines()
        self.output_file = open(output_name + " errors.txt", 'w')
        self.output_file.write("Compiling " + input_name + "...\n")
        self.line = 0
        self.errors = 0
        self.warnings = 0
        self.line_number = 1

    def write_error(self, error_msg):
        self.output_file.write("Error at line " + str(self.line_number) + ": " + error_msg + ":\n")
        self.output_file.write(self.lines[self.line_number - 1] + "\n")
        self.errors += 1

    def next_line(self):
        self.line_number += 1


class CodeGen:
    def __init__(self, output_name):
        self.output_name = output_name
        self.code_seg_name = output_name + "_code_seg.txt"
        self.data_seg_name = output_name + "_data_seg.txt"
        open(self.code_seg_name, 'w')
        open(self.data_seg_name, 'w')
        self.known_vars = {}

    def write_data(self, data):
        data_seg = open(self.data_seg_name, "a")
        data_seg.write("\t" + data + "\n")
        data_seg.close()

    def write_code(self, code):
        code_seg = open(self.code_seg_name, "a")
        code_seg.write("\t" + code + "\n")
        code_seg.close()

    def generate_code(self):
        # Join the .code, .data into a working asm program
        output = open(self.output_name + ".asm", 'w')
        output.write("ExitProcess proto\n\n")
        output.write(".data\n")
        data_seg = open(self.data_seg_name, 'r')
        output.write(data_seg.read())
        output.write("\n.code\n")
        output.write("main proc\n")
        code_seg = open(self.code_seg_name, 'r')
        output.write(code_seg.read())
        output.write("\nmov   ecx,0\n")
        output.write("call  ExitProcess\n")
        output.write("main endp\n")
        output.write("end")
        code_seg.close()
        os.remove(self.output_name + "_code_seg.txt")
        data_seg.close()
        os.remove(self.output_name + "_data_seg.txt")
        output.close()


