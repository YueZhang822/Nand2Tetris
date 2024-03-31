import os
import re
import argparse
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


class JackAnalyzer:
    """
    The JackAnalyzer class drives the compilation process.
    """
    def __init__(self, input_file, tokenize_only=False):
        self.tokenize_only = tokenize_only   # a boolean value indicating whether to output the token file
        self.input_stream = self.clean_file_into_stream(input_file)  # a list of cleaned tokens
        self.output_stream = self.openOutputFile(input_file)      # the output file handler
        self.tokenizer = JackTokenizer(self.input_stream, self.output_stream)   # the tokenizer
        self.compilation_engine = CompilationEngine(self.tokenizer, self.output_stream)   # the parser
        self.analyze()
    
    def clean_file_into_stream(self, file_name):
        """
        Clean the file by removing comments and empty lines
        Input: file_name - the name of the file to be cleaned
        Output: tokens - a flat list of cleaned tokens
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
            pattern = r'".*?"|\w+|[^\w\s]'   # match strings, words, and symbols
            tokens = [token for line in command_list for token in re.findall(pattern, line)]    
        return tokens
    
    def openOutputFile(self, input_file):
        """
        Set the output file.
        Input: input_file - the name of the input file
        Output: output_fd - the file handler of the output file
        """
        # If tokenize_only is True, the output file is named as xxxT.xml
        # Otherwise, the output file is named as xxx.xml
        if self.tokenize_only:
            output_file = input_file.replace('.jack', 'T.xml')
        else:
            output_file = input_file.replace('.jack', '.xml')
        # Create the directory if it does not exist
        if os.path.dirname(output_file):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        # Open the output file for writing
        output_fd = open(output_file, 'w')
        return output_fd
    
    def analyze(self):
        """
        Analyze the input file and write the parsed tokens into the output file.
        """
        # If tokenize_only, tokenize the input file and write into the output file
        # Otherwise, parse the input file and write into the output file
        if self.tokenize_only:
            self.tokenizer.tokenize()
        else:
            self.compilation_engine.compileClass()
        self.close()
    
    def close(self):
        """
        Close the output file.
        """
        self.output_stream.close()


def get_path(input_path):
    """
    Check if the user has provided a valid file source. 
    Return the path of the file or all files in the directory.
    Output: files - a list of files to be translated or None if the input is invalid
    """
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
    The main function of the JackAnalyzer class.
    """
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='configurations for JackAnalyzer')
    parser.add_argument('-p', '--path', required=True, help='path to the jack file or directory')
    parser.add_argument('--token', action='store_true', help='output the token file')
    parser.add_argument('--parse', action='store_true', help='output the parse file (default)')
    args = parser.parse_args()

    # Get the path of the file or paths of all files in the directory
    files = get_path(args.path)
    if not files:
        return
    
    # For each file, create a JackAnalyzer object and translate the file
    for file in files:
        JackAnalyzer(file, args.token)

if __name__ == "__main__":
    main()