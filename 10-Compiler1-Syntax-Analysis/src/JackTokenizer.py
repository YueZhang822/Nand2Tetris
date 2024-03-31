# The JackTokenizer class removes all comments and white space from the input stream
# and breaks it into Jack-language tokens, as specified by the Jack grammar.

class JackTokenizer:
    def __init__(self, input_stream, output_stream):
        """
        Constructor - Opens the input stream and gets ready to tokenize it.
        Input: input_stream - the input stream
                output_stream - the output stream
        """
        self.tokens = input_stream
        self.output_stream = output_stream
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
        if self.current_token == "<":
            return "&lt;"
        elif self.current_token == ">":
            return "&gt;"
        elif self.current_token == "&":
            return "&amp;"
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
    
    def tokenize(self):
        """
        Tokenize the input stream and write the parsed tokens into the output file.
        """
        self.output_stream.write("<tokens>\n")
        while self.hasMoreTokens():
            self.advance()
            token_type = self.tokenType()
            if token_type == "KEYWORD":
                self.output_stream.write("<keyword> {} </keyword>\n".format(self.keyword()))
            elif token_type == "SYMBOL":
                self.output_stream.write("<symbol> {} </symbol>\n".format(self.symbol()))
            elif token_type == "IDENTIFIER":
                self.output_stream.write("<identifier> {} </identifier>\n".format(self.identifier()))
            elif token_type == "INT_CONST":
                self.output_stream.write("<integerConstant> {} </integerConstant>\n".format(self.intVal()))
            elif token_type == "STRING_CONST":
                self.output_stream.write("<stringConstant> {} </stringConstant>\n".format(self.stringVal()))
            else:
                raise Exception("Invalid token type")
        self.output_stream.write("</tokens>\n")