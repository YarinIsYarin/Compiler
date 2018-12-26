import os
import Parser


class Compiler:
    def __init__(self, output_name, input_name):
        # This hold what we need to do at the end of each block
        self.block_stack = []
        self.line_number = 1
        self.output_name = output_name
        self.code_seg_name = output_name + "_code_seg.txt"
        self.data_seg_name = output_name + "_data_seg.txt"
        open(self.code_seg_name, 'w')
        open(self.data_seg_name, 'w')
        self.known_vars = {}
        self.last_label = "$"
        self.lines = open(input_name + '.txt').readlines()
        self.output_file = open(output_name + " errors.txt", 'w')
        self.output_file.write("Compiling " + input_name + "...\n")
        self.line = 0
        self.errors = 0
        self.warnings = 0

    def next_line(self, indent=None):
        self.line_number += 1
        if indent is None:
            return
        if indent > len(self.block_stack):
            self.write_error("Over indented block")
            return
        while indent < len(self.block_stack):
            curr = self.block_stack.pop()
            if list != type(curr):
                curr = [curr]
            for i in curr:
                if isinstance(i, Parser.ASTNode):
                    i.generate_code()
                else:
                    self.write_code(i)

    def gen_at_end_of_block(self, code):
        self.block_stack.append(code)

    def write_error(self, error_msg):
        self.output_file.write("Error at line " + str(self.line_number) + ": " + error_msg + ":\n")
        self.output_file.write(self.lines[self.line_number - 1] + "\n")
        self.errors += 1

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

    def label_gen(self):
        # TODO: make a better one
        self.last_label += "a"
        return self.last_label

