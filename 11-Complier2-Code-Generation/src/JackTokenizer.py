import re


class JackTokenizer:
    """
    The JackTokenizer class removes all comments and white space from the input stream
    and breaks it into Jack-language tokens, as specified by the Jack grammar.
    """
    def __init__(self, input_file):
        """
        Constructor - Opens the input stream and gets ready to tokenize it.
        Input: input_stream - the input stream
                output_stream - the output stream
        """
        self.input = input_file
        self.tokens = self.tokenize()
        self.next_index = 0
        self.current_token = None
        self._keyword_table = {"class": "CLASS", "constructor": "CONSTRUCTOR", "function": "FUNCTION",
                                "method": "METHOD", "field": "FIELD", "static": "STATIC", "var": "VAR",
                                "int": "INT", "char": "CHAR", "boolean": "BOOLEAN", "void": "VOID",
                                "true": "TRUE", "false": "FALSE", "null": "NULL", "this": "THIS",
                                "let": "LET", "do": "DO", "if": "IF", "else": "ELSE", "while": "WHILE",
                                "return": "RETURN"}
        self._symbol_table = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/",
                                "&", "|", "<", ">", "=", "~"]

    def tokenize(self):
        """
        Clean the file by removing comments and empty lines
        Input: file_name - the name of the file to be cleaned
        Output: tokens - a flat list of cleaned tokens
        """
        with open(self.input, "r") as f:
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
    
    def hasMoreTokens(self):
        """
        Check if there are more tokens to be parsed.
        """
        return self.next_index < len(self.tokens)

    def advance(self):
        """
        Read the next token from the input and make it the current token.
        """
        if not self.hasMoreTokens():
            raise Exception("Expected more tokens but reached the end of the file")
        self.current_token = self.tokens[self.next_index]
        self.next_index += 1

    def tokenType(self):
        """
        Return the type of the current token as a constant.
        """
        if self.current_token in self._keyword_table.keys():
            return "KEYWORD"
        elif self.current_token in self._symbol_table:
            return "SYMBOL"
        elif self.current_token.isdigit() and (0 <= int(self.current_token) <= 32767):
            return "INT_CONST"
        elif self.current_token.startswith('"') and self.current_token.endswith('"'):
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def keyword(self):
        """
        Return the keyword which is the current token as a constant.
        This method should be called only if tokenType() is KEYWORD.
        """
        return self.current_token

    def symbol(self):
        """
        Return the character which is the current token.
        This method should be called only if tokenType() is SYMBOL.
        """
        return self.current_token

    def identifier(self):
        """
        Return the identifier which is the current token.
        This method should be called only if tokenType() is IDENTIFIER.
        """
        return self.current_token

    def intVal(self):
        """
        Return the integer value of the current token.
        This method should be called only if tokenType() is INT_CONST.
        """
        return self.current_token

    def stringVal(self):
        """
        Return the string value of the current token, without the double quotes.
        This method should be called only if tokenType() is STRING_CONST.
        """
        return self.current_token.strip('"')
    
    def peek(self):
        """
        Return the next token without advancing the pointer.
        """
        return self.tokens[self.next_index]