import os


class VMWriter:
    """
    The VMWriter class emits VM commands into a file, using the VM command syntax.
    """
    def __init__(self, input_file):
        """
        Creates a new file and prepares it for writing.
        """
        self.output_file = self.setOutputFile(input_file)

    def setOutputFile(self, input_file):
        """
        Set the output file.
        """
        output_file = input_file.replace('.jack', '.vm')
        # Create the directory if it does not exist
        if os.path.dirname(output_file):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        # Open the output file for writing
        output_fd = open(output_file, 'w')
        return output_fd

    def write_push(self, segment, index):
        """
        Writes a VM push command.
        Segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP.
        """
        if segment == "CONST":
            segment = "constant"
        elif segment == "ARG":
            segment = "argument"
        self.output_file.write("push {} {}\n".format(segment.lower(), str(index)))

    def write_pop(self, segment, index):
        """
        Writes a VM pop command.
        Segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP.
        """
        if segment == "CONST":
            segment = "constant"
        elif segment == "ARG":
            segment = "argument"
        self.output_file.write("pop {} {}\n".format(segment.lower(), str(index)))

    def write_arithmetic(self, command):
        """
        Writes a VM arithmetic-logical command.
        Command: ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT.
        """
        self.output_file.write("{}\n".format(command.lower()))

    def write_label(self, label):
        """
        Writes a VM label command.
        """
        self.output_file.write("label {}\n".format(label))

    def write_goto(self, label):
        """
        Writes a VM goto command.
        """
        self.output_file.write("goto {}\n".format(label))

    def write_if(self, label):
        """
        Writes a VM if-goto command.
        """
        self.output_file.write("if-goto {}\n".format(label))

    def write_call(self, name, n_args):
        """
        Writes a VM call command.
        """
        self.output_file.write("call {} {}\n".format(name, str(n_args)))

    def write_function(self, name, n_locals):
        """
        Writes a VM function command.
        """
        self.output_file.write("function {} {}\n".format(name, str(n_locals)))

    def write_return(self):
        """
        Writes a VM return command.
        """
        self.output_file.write("return\n")

    def close(self):
        """
        Closes the output file.
        """
        self.output_file.close()