import sys
import os

class APARSER:
    def __init__(self):
        self._symbol_table = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            'R0': 0,
            'R1': 1,
            'R2': 2,
            'R3': 3,
            'R4': 4,
            'R5': 5,
            'R6': 6,
            'R7': 7,
            'R8': 8,
            'R9': 9,
            'R10': 10,
            'R11': 11,
            'R12': 12,
            'R13': 13,
            'R14': 14,
            'R15': 15,
            'SCREEN': 16384,
            'KBD': 24576
        }
        self.address_poniter = 16       # the first available memory address
    
    def add_symbol(self, symbol, index=None):
        # Add a new symbol to the symbol table
        if index:
            self._symbol_table[symbol] = index
        else:
            self._symbol_table[symbol] = self.address_poniter
            self.address_poniter += 1

    def DecimalToBinary(self, num):
        # Convert a decimal number to a 16-bit binary number
        binary = bin(num).replace('0b', '')
        return binary.zfill(16)
    
    def get_code(self, value):
        # If the value is a number, convert it to binary
        if value.isdigit():
            return self.DecimalToBinary(int(value))
        
        # If the value is in the symbol table, convert it to binary
        elif value in self._symbol_table:
            return self.DecimalToBinary(self._symbol_table[value])
        
        # If the value is not in the symbol table, add it to the symbol table and convert it to binary
        else:
            self.add_symbol(value)
            return self.DecimalToBinary(self._symbol_table[value])
        
    def parse(self, instruction):
        value = instruction[1:]
        return self.get_code(value)
        
class CPARSER:
    def __init__(self):
        self._dest_table = {
            'null': '000',
            'M': '001',
            'D': '010',
            'MD': '011',
            'A': '100',
            'AM': '101',
            'AD': '110',
            'AMD': '111'
        }
        self._comp_table = {
            '0': '0101010',
            '1': '0111111',
            '-1': '0111010',
            'D': '0001100',
            'A': '0110000',
            '!D': '0001101',
            '!A': '0110001',
            '-D': '0001111',
            '-A': '0110011',
            'D+1': '0011111',
            'A+1': '0110111',
            'D-1': '0001110',
            'A-1': '0110010',
            'D+A': '0000010',
            'D-A': '0010011',
            'A-D': '0000111',
            'D&A': '0000000',
            'D|A': '0010101',
            'M': '1110000',
            '!M': '1110001',
            '-M': '1110011',
            'M+1': '1110111',
            'M-1': '1110010',
            'D+M': '1000010',
            'D-M': '1010011',
            'M-D': '1000111',
            'D&M': '1000000',
            'D|M': '1010101'
        }
        self._jump_table = {
            'null': '000',
            'JGT': '001',
            'JEQ': '010',
            'JGE': '011',
            'JLT': '100',
            'JNE': '101',
            'JLE': '110',
            'JMP': '111'
        }
    
    def get_code(self, dest, comp, jump):
        return '111' + self._comp_table[comp] + self._dest_table[dest] + self._jump_table[jump]
    
    def parse(self, instruction):
        # Split the instruction into dest, comp and jump
        parts = instruction.split('=')
        if len(parts) == 2:
            dest = parts[0]
            comp_jump = parts[1].split(';')
        else:
            dest = 'null'
            comp_jump = parts[0].split(';')
        comp = comp_jump[0]
        if len(comp_jump) == 2:
            jump = comp_jump[1]
        else:
            jump = 'null'
        return self.get_code(dest, comp, jump)
    
class PARSER:
    def __init__(self, asm):
        self.instructions = asm.split('\n')
        self.AParser = APARSER()
        self.CParser = CPARSER()
        self.code = self.parse()

    def parse(self):
        codes = []         # Store the binary code
        no_label = []        # Store instructions without label
        label_count = 0        # Count the number of labels

        # First pass: add labels to the symbol table and remove them from the instructions
        for index, instruction in enumerate(self.instructions):
            if instruction.startswith('(') and instruction.endswith(')'):
                self.AParser.add_symbol(instruction[1:-1], index-label_count)
                label_count += 1
            else:
                no_label.append(instruction)

        # Second pass: parse the remaining instructions
        for instruction in no_label:
            if instruction.startswith('@'):      # A instruction
                code = self.AParser.parse(instruction)
            else:
                code = self.CParser.parse(instruction)      # C instruction
            codes.append(code)
        return '\n'.join(codes)
    
def get_path():
    """
    Check if the user has provided a valid filename
    """
    # The number of arguments must be 2 and the filename must end with .in
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.asm'):
        print('Usage: python3 main.py <filename>.asm')
        return
    
    input_path = sys.argv[1]

    # Check if the file exists
    if not os.path.exists(input_path):
        print('File does not exist')
        return
    
    return input_path

def clean_file(file_name):
    """
    Clean the file by removing comments and empty lines
    Input: file_name - the name of the file to be cleaned
    Output: cleaned - the cleaned file
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
        cleaned = "\n".join([line for line in cleaned.split("\n") if line.strip()])
    
    return cleaned

def main():
    # Check if the user has provided a valid filename
    input_path = get_path()

    if not input_path:
        return
    
    # Clean the file by removing comments and white spaces
    cleaned_asm = clean_file(input_path)

    # Parse the code
    result = PARSER(cleaned_asm).code

    # Create the output file
    output_path = input_path.replace('.asm', '.hack')
    if os.path.dirname(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write the result to the output file
    with open(output_path, "w") as f:
        f.write(result)

if __name__ == '__main__':
    main()