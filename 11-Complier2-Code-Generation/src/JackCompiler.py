import os
import sys
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from CompilationEngine import CompilationEngine


class JackCompiler:
    """
    The JackAnalyzer class drives the compilation process of a single .jack file.
    """
    def __init__(self, input_file):
        self.tokenizer = JackTokenizer(input_file)   # Create a JackTokenizer from the input file
        self.symbol_table = SymbolTable()   # Create a symbol table
        self.vm_writer = VMWriter(input_file)   # Create a VMWriter
        self.compilation_engine = CompilationEngine(self.tokenizer, self.symbol_table, self.vm_writer)
    
    def compile(self):
        """
        Compile the single input file.
        """
        self.compilation_engine.compileClass()
        self.vm_writer.close()

def get_path():
    """
    Check if the user has provided a valid file source. 
    Return the path of the file or all files in the directory.
    Output: files - a list of files to be translated or None if the input is invalid
    """
    # The number of arguments must be 2 and the filename must end with .jack or be a directory
    if len(sys.argv) != 2 or (not sys.argv[1].endswith('.jack') and not os.path.isdir(sys.argv[1])):
        print('Usage: python3 JackCompiler.py <filename>.jack or python3 JackCompiler.py <directory>')
        return
    
    input_path = sys.argv[1]
    files = []

    # Check if the file exists
    if not os.path.exists(input_path):
        print('File or directory does not exist')
        return
    
    # If the input is a directory, get all the .jack files in the directory
    if os.path.isdir(input_path):
        for file in os.listdir(input_path):
            if file.endswith('.jack'):
                files.append(os.path.join(input_path, file))
        if not files:
            # If there are no .jack files in the directory, throw an error message
            print('No .jack files in the directory')
            return
    else:
        files.append(input_path)
    
    return files

def main():
    """
    The main function of the JackCompiler class.
    """
    # Get the path of the file or all files in the directory
    files = get_path()  # List of files to be translated
    if not files:
        return
    
    for file in files:
        JackCompiler(file).compile()

if __name__ == "__main__":
    main()