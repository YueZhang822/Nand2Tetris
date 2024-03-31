import os
import sys

class Parser():
    """
    Handles the parsing of a single .vm file, and encapsulates access to the input code.
    Reads VM commands, parses them, and provides convenient access to their components.
    """
    def __init__(self, filename):
        self.commands = self.clean_file_into_stream(filename)    # List of cleaned commands
        self.next_index = 0
        self.current_command = None
        self._type_table = {
            "add": "C_ARITHMETIC",
            "sub": "C_ARITHMETIC",
            "neg": "C_ARITHMETIC",
            "eq": "C_ARITHMETIC",
            "gt": "C_ARITHMETIC",
            "lt": "C_ARITHMETIC",
            "and": "C_ARITHMETIC",
            "or": "C_ARITHMETIC",
            "not": "C_ARITHMETIC",
            "push": "C_PUSH",
            "pop": "C_POP",
            "label": "C_LABEL",
            "goto": "C_GOTO",
            "if-goto": "C_IF",
            "function": "C_FUNCTION",
            "call": "C_CALL",
            "return": "C_RETURN",
        }

    def hasMoreCommands(self):
        """
        Check if there are more commands to be parsed
        Output: True if there are more commands, False otherwise
        """
        return self.next_index < len(self.commands)
    
    def advance(self):
        """
        Read the next command from the input and make it the current command
        """
        self.current_command = self.commands[self.next_index]
        self.next_index += 1

    def commandType(self):
        """
        Return the type of the current command
        Output: one of C_ARITHMETIC, C_PUSH, C_POP
        """
        return self._type_table[self.current_command.split()[0]]
    
    def arg1(self):
        """
        Return the first argument of the current command
        """
        if self.commandType() == "C_ARITHMETIC":
            return self.current_command.split()[0]
        return self.current_command.split()[1]
        
    def arg2(self):
        """
        Return the second argument of the current command
        """
        return self.current_command.split()[2]
        
    def clean_file_into_stream(self, file_name):
        """
        Clean the file by removing comments and empty lines
        Input: file_name - the name of the file to be cleaned
        Output: cleaned - a list of cleaned commands
        """
        with open(file_name, "r") as f:
            content = f.read()

            # Remove comments starting with /* and ending with */
            while "/*" in content and "*/" in content:
                start = content.find("/*")
                end = content.find("*/") + 2
                content = content[:start] + content[end:]

            # Remove blanks and comments starting with //
            cleaned = "\n".join([line.split("//")[0].strip() for line in content.split("\n") if line.strip()])
            command_list = [line for line in cleaned.split("\n") if line.strip()]
        
        return command_list
        
        
class CodeWriter():
    """
    Translates VM commands into Hack assembly code.
    """
    def __init__(self, filename):
        # initialize an output file handler
        self.output = self.openFile(filename)
        # Count the number of labels we have create for jump commands
        self._label_count = 0
        self.file_name = None
        self.function_name = "OS"
        self._arithmetic_table = {
            "add": "M=D+M\n",
            "sub": "M=M-D\n",
            "neg": "M=-M\n",
            "eq": "D;JEQ\n",
            "gt": "D;JGT\n",
            "lt": "D;JLT\n",
            "and": "M=D&M\n",
            "or": "M=D|M\n",
            "not": "M=!M\n",
        }
        self._segment_table = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT",
            "static": 16,
            "pointer": 3,
            "temp": 5,
        }

    def openFile(self, output_file):
        """
        Inform the code writer that the translation of a new VM file is started.
        Input: filename - the name of the file to be translated
        Output: fd - the file handler of the output file
        """
        if os.path.dirname(output_file):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        fd = open(output_file, "w")
        return fd
    
    def setFileName(self, filename):
        """
        Inform the code writer that the translation of a new VM file is started.
        Input: filename - the name of the file to be translated
        """
        self.file_name = filename
    
    def writeInit(self):
        """
        Write assembly code that effects the VM initialization, also called bootstrap code.
        This code must be placed at the beginning of the output file.
        """
        self.output.write("@256\nD=A\n@SP\nM=D\n")
        self.writeCall("Sys.init", 0)

    def writeLabel(self, label):
        """
        Write assembly code that effects the label command.
        Input: label - the label to be translated
        """
        self.output.write(f"({self.function_name}${label})\n")

    def writeGoto(self, label):
        """
        Write assembly code that effects the goto command.
        Input: label - the label to be translated
        """
        self.output.write(f"@{self.function_name}${label}\n0;JMP\n")

    def writeIf(self, label):
        """
        Write assembly code that effects the if-goto command.
        Input: label - the label to be translated
        """
        self.output.write("@SP\nAM=M-1\nD=M\n")
        self.output.write(f"@{self.function_name}${label}\nD;JNE\n")

    def writeCall(self, functionName, numArgs):
        """
        Write assembly code that effects the call command.
        Input: functionName - the name of the function to be called
                numArgs - the number of arguments
        """
        return_label = f"{functionName}$ret.{self.generate_label()}"
        self.output.write(f"@{return_label}\nD=A\n@SP\nAM=M+1\nA=A-1\nM=D\n")
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            self.output.write(f"@{segment}\nD=M\n@SP\nAM=M+1\nA=A-1\nM=D\n")
        self.output.write(f"@SP\nD=M\n@5\nD=D-A\n@{numArgs}\nD=D-A\n@ARG\nM=D\n")
        self.output.write(f"@SP\nD=M\n@LCL\nM=D\n")
        self.output.write(f"@{functionName}\n0;JMP\n({return_label})\n")

    def writeReturn(self):
        """
        Write assembly code that effects the return command.
        """
        self.output.write("@LCL\nD=M\n@R13\nM=D\n")
        self.output.write("@5\nA=D-A\nD=M\n@R14\nM=D\n")
        self.output.write("@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n")
        self.output.write("@ARG\nD=M+1\n@SP\nM=D\n")
        for segment in ["THAT", "THIS", "ARG", "LCL"]:
            self.output.write("@R13\nAM=M-1\nD=M\n")
            self.output.write(f"@{segment}\nM=D\n")
        self.output.write("@R14\nA=M\n0;JMP\n")

    def writeFunction(self, functionName, numLocals):
        """
        Write assembly code that effects the function command.
        Input: functionName - the name of the function
                numLocals - the number of local variables
        """
        self.function_name = functionName
        self.output.write(f"({functionName})\n")
        for _ in range(int(numLocals)):
            self.writePushPop("C_PUSH", "constant", 0)
    
    def generate_label(self):
        """
        Generate a unique label for jump commands
        Output: a unique label name
        """
        self._label_count += 1
        return f"LABEL{self._label_count}"

    def writeArithmetic(self, command):
        """
        Write the assembly code that is the translation of the given arithmetic command.
        Input: command - the single arithmetic command to be translated
        """
        if command in ["neg", "not"]:
            self.output.write("@SP\nA=M-1\n")
            self.output.write(self._arithmetic_table[command])
        else:
            self.output.write("@SP\nAM=M-1\nD=M\nA=A-1\n")
            if command in ["add", "sub", "and", "or"]:
                self.output.write(self._arithmetic_table[command])
            else:
                label = self.generate_label()
                self.output.write(f"D=M-D\nM=-1\n@{label}\n{self._arithmetic_table[command]}")
                self.output.write(f"@SP\nA=M-1\nM=0\n({label})\n")

    def writePushPop(self, command, segment, index):
        """
        Write the assembly code that is the translation of the given command, where command is either C_PUSH or C_POP.
        Input: command - the command type
                segment - the segment to be pushed or popped
                index - the index of the segment
        """
        self.parse_address(segment, index)
        if command == "C_POP":
            self.output.write(f"D=A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
        else:
            if segment == "constant":
                self.output.write(f"D=A\n")
            else:
                self.output.write(f"D=M\n")
            self.output.write("@SP\nAM=M+1\nA=A-1\nM=D\n")

    def parse_address(self, segment, index):
        """
        This function parse the address to A register.
        """
        if segment == "constant":
            self.output.write(f"@{index}\n")
        elif segment == "static":
            self.output.write(f"@{self.file_name}.{index}\n")
        elif segment in ["pointer", "temp"]:
            self.output.write(f"@R{self._segment_table[segment]+index}\n")
        elif segment in ["local", "argument", "this", "that"]:
            self.output.write(f"@{self._segment_table[segment]}\nD=M\n@{index}\nA=D+A\n")
                
    def close(self):
        """
        Close the output file
        """
        self.output.close()

def get_path():
    """
    Check if the user has provided a valid file source. 
    Return the path of the file or all files in the directory.
    Output: files - a list of files to be translated or None if the input is invalid
    """
    # The number of arguments must be 2 and the filename must end with .vm or be a directory
    if len(sys.argv) != 2 or (not sys.argv[1].endswith('.vm') and not os.path.isdir(sys.argv[1])):
        print('Usage: python3 VMtranslator.py <filename>.vm or python3 VMtranslator.py <directory>')
        return
    
    input_path = sys.argv[1]
    files = []

    # Check if the file exists
    if not os.path.exists(input_path):
        print('File or directory does not exist')
        return
    
    # If the input is a directory, get all the .vm files in the directory
    if os.path.isdir(input_path):
        for file in os.listdir(input_path):
            if file.endswith('.vm'):
                files.append(os.path.join(input_path, file))
        if not files:
            # If there are no .vm files in the directory, throw an error message
            print('No .vm files in the directory')
            return
    else:
        files.append(input_path)
    
    return files


def main():
    """
    Initialize the parser and the code writer.
    Read the input file and translate it into assembly code.
    """
    # Get the path of the file or all files in the directory
    files = get_path()  # List of files to be translated
    if not files:
        return

    # Decide the output filename
    output_filename = os.path.join(os.path.dirname(files[0]), os.path.basename(os.path.dirname(files[0])) + '.asm')
    
    # Create a CodeWriter to write to the output file
    code_writer = CodeWriter(output_filename)

    # Write the bootstrap code
    sys_init_required = any(file.endswith('Sys.vm') for file in files)
    if sys_init_required:
        code_writer.writeInit()
    
    for file in files:
        # Create a Parser for the input file
        parser = Parser(file)
        code_writer.setFileName(os.path.basename(file).split('.')[0])

        # Parse and write the assembly code
        while parser.hasMoreCommands():
            parser.advance()
            ctype = parser.commandType()
            
            if ctype == 'C_ARITHMETIC':
                code_writer.writeArithmetic(parser.arg1())
            elif ctype in ['C_PUSH', 'C_POP']:
                code_writer.writePushPop(ctype, parser.arg1(), int(parser.arg2()))
            elif ctype == 'C_LABEL':
                code_writer.writeLabel(parser.arg1())
            elif ctype == 'C_GOTO':
                code_writer.writeGoto(parser.arg1())
            elif ctype == 'C_IF':
                code_writer.writeIf(parser.arg1())
            elif ctype == 'C_FUNCTION':
                code_writer.writeFunction(parser.arg1(), parser.arg2())
            elif ctype == 'C_RETURN':
                code_writer.writeReturn()
            elif ctype == 'C_CALL':
                code_writer.writeCall(parser.arg1(), int(parser.arg2()))
    
    # Close the output file
    code_writer.close()
    

if __name__ == "__main__":
    main()