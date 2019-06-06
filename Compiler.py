import os, Parser
from Consts import Types, string_to_type


class Compiler:
    def __init__(self, output_name, input_name):
        # In the current local memory part of the stack, how many qwords did I use
        self.stack_used = [0]
        # Given a var, how much do we need to sub from bp to get that var
        self.where_on_stack = [{}]
        self.known_vars = {}
        self.vars_at_this_block = [[]]
        # This hold what we need to do at the end of each block
        self.block_stack = []
        # A stack that save the type of block we are currently in (such as if, else and etc)
        self.which_block_am_i = ["Main"]
        self.line_number = 1
        self.output_name = output_name
        self.code_seg_name = output_name + "_code_seg.txt"
        self.data_seg_name = output_name + "_data_seg.txt"
        open(self.code_seg_name, 'w')
        open(self.data_seg_name, 'w')
        self.last_label = "$a"
        self.lines = open(input_name + '.txt').readlines()
        self.output_file = open(output_name + " errors.txt", 'w')
        self.output_file.write("Compiling " + input_name + "...\n")
        self.line = 0
        # Count how many warnings \ errors the program had
        self.errors = 0
        self.warnings = 0
        # func_name: return type
        self.known_funcs = {}
        # The line the function was declared on : func_name
        self.func_lines = {}
        # The exact parameters in the functions signature
        self.func_declarations = {}
        # The name (as in known_funcs) of the function we are currently in, None if in main
        self.in_func = None
        # True iff the current function had a return statement
        self.posibble_return = False
        self.guaranteed_return = False
        self.indent = 0

    def next_line(self, indent=None):
        self.indent = indent
        if indent == 0:
            # Make sure the function has a return statement
            if self.in_func and string_to_type(self.known_funcs[self.in_func]) != Types.void and not self.posibble_return:
                self.write_error("Missing return statement")
            elif self.in_func and string_to_type(self.known_funcs[self.in_func]) != Types.void and not self.guaranteed_return:
                self.write_warning("No unconditional return statement")
            self.in_func = None
            self.posibble_return = False
            self.guaranteed_return = False

        self.line_number += 1
        if indent is None:
            return
        if indent > len(self.block_stack):
            print(self.block_stack)
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
            for x in self.vars_at_this_block[-1]:
                self.known_vars.pop(x)
                self.where_on_stack[-1].pop(x)
            self.vars_at_this_block.pop()
        while indent < len(self.which_block_am_i) - 1:
            self.which_block_am_i.pop()

    def gen_at_end_of_block(self, code):
        self.block_stack.append(code)
        self.vars_at_this_block.append([])

    def write_error(self, error_msg):
        self.output_file.write("Error at line " + str(self.line_number) + ": " + error_msg + ":\n")
        self.output_file.write(self.lines[self.line_number - 1] + "\n")
        self.errors += 1

    def write_warning(self, warning_msg):
        self.output_file.write("Warning at line " + str(self.line_number) + ": " + warning_msg + ":\n")
        self.output_file.write(self.lines[self.line_number - 1] + "\n")


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
        # This is used so that we know where we cant start to use the ds as dynamic memory
        output.write(data_seg.read())
        output.write("startOfHeap qword 0\n")
        output.write("\n.code\n")
        output.write("main proc\n")
        # We use rcx to count how much memory we are using, 64 is a nice value
        output.write("\tmov rcx, offset startOfHeap\n")
        output.write("\tmov rbp, rsp\n")
        output.write("\tadd rbp, " + str(self.stack_used[-1]) + "\n")
        code_seg = open(self.code_seg_name, 'r')
        output.write(code_seg.read())
        output.write("\tsub rbp, " + str(self.stack_used[-1]) + "\n")
        output.write("\n@$$$end_of_code:")
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
        if self.last_label[-1] == 'z':
            self.last_label += 'a'
        else:
            self.last_label = self.last_label[0:-1] + chr(ord(self.last_label[-1])+1)
        return self.last_label

    def get_var_stack_place(self, var_name):
        return self.where_on_stack[-1][var_name]

