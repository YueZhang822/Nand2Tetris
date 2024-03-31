# The CompilationEngine class is used to compile a Jack source file into xml

class CompilationEngine:
    def __init__(self, tokenizer, output):
        self.tokenizer = tokenizer
        self.output_stream = output
        self.indent = 0  # the number of spaces to indent
        self.indent_increment = 2  # the number of spaces to increment the indentation level

    def compileClass(self):
        """
        Compile a complete class.
        """
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "class"
        self.write("<class>\n")
        self.incrementIndent()
        self.write("<keyword> class </keyword>\n")
        self.tokenizer.advance()
        self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
        self.tokenizer.advance()
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["static", "field"]:
            self.compileClassVarDec()
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["constructor", "function", "method"]:
            self.compileSubroutine()
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        assert not self.tokenizer.hasMoreTokens()
        self.decrementIndent()
        self.write("</class>\n")

    def compileClassVarDec(self):
        """
        Compile a static declaration or a field declaration.
        """
        self.write("<classVarDec>\n")
        self.incrementIndent()
        self.write("<keyword> {} </keyword>\n".format(self.tokenizer.keyword()))
        self.tokenizer.advance()
        if self.tokenizer.tokenType() == "KEYWORD":
            self.write("<keyword> {} </keyword>\n".format(self.tokenizer.keyword()))
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
        self.tokenizer.advance()
        self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
        self.tokenizer.advance()
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
            self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
            self.tokenizer.advance()
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.decrementIndent()
        self.write("</classVarDec>\n")

    def compileSubroutine(self):
        """
        Compile a complete method, function, or constructor.
        """
        self.write("<subroutineDec>\n")
        self.incrementIndent()
        self.write("<keyword> {} </keyword>\n".format(self.tokenizer.keyword()))
        self.tokenizer.advance()
        if self.tokenizer.tokenType() == "KEYWORD":
            self.write("<keyword> {} </keyword>\n".format(self.tokenizer.keyword()))
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
        self.tokenizer.advance()
        self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
        self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "("
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.compileParameterList()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ")"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.compileSubroutineBody()
        self.decrementIndent()
        self.write("</subroutineDec>\n")

    def compileSubroutineBody(self):
        """
        Compile the body of a subroutine.
        """
        self.write("<subroutineBody>\n")
        self.incrementIndent()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "{"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "var":
            self.compileVarDec()
        self.compileStatements()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "}"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.decrementIndent()
        self.write("</subroutineBody>\n")

    def compileParameterList(self):
        """
        Compile a (possibly empty) parameter list, not including the enclosing "()".
        """
        self.write("<parameterList>\n")
        self.incrementIndent()
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            if self.tokenizer.tokenType() == "KEYWORD":
                self.write("<keyword> {} </keyword>\n".format(self.tokenizer.keyword()))
            elif self.tokenizer.tokenType() == "IDENTIFIER":
                self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
            self.tokenizer.advance()
            self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
            self.tokenizer.advance()
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
                self.tokenizer.advance()
                if self.tokenizer.tokenType() == "KEYWORD":
                    self.write("<keyword> {} </keyword>\n".format(self.tokenizer.keyword()))
                elif self.tokenizer.tokenType() == "IDENTIFIER":
                    self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
                self.tokenizer.advance()
                self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
                self.tokenizer.advance()
        self.decrementIndent()
        self.write("</parameterList>\n")

    def compileVarDec(self):
        """
        Compile a var declaration.
        """
        self.write("<varDec>\n")
        self.incrementIndent()
        self.write("<keyword> var </keyword>\n")
        self.tokenizer.advance()
        if self.tokenizer.tokenType() == "KEYWORD":
            self.write("<keyword> {} </keyword>\n".format(self.tokenizer.keyword()))
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
        self.tokenizer.advance()
        self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
        self.tokenizer.advance()
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
            self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
            self.tokenizer.advance()
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.decrementIndent()
        self.write("</varDec>\n")

    def compileStatements(self):
        self.write("<statements>\n")
        self.incrementIndent()
        while self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["let", "if", "while", "do", "return"]:
            if self.tokenizer.keyword() == "let":
                self.compileLet()
            elif self.tokenizer.keyword() == "if":
                self.compileIf()
            elif self.tokenizer.keyword() == "while":
                self.compileWhile()
            elif self.tokenizer.keyword() == "do":
                self.compileDo()
            elif self.tokenizer.keyword() == "return":
                self.compileReturn()
        self.decrementIndent()
        self.write("</statements>\n")

    def compileDo(self):
        self.write("<doStatement>\n")
        self.incrementIndent()
        self.write("<keyword> do </keyword>\n")
        self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "IDENTIFIER"
        self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
        self.tokenizer.advance()
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ".":
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
            assert self.tokenizer.tokenType() == "IDENTIFIER"
            self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
            self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "("
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.compileExpressionList()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ")"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ";"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.decrementIndent()
        self.write("</doStatement>\n")

    def compileLet(self):
        self.write("<letStatement>\n")
        self.incrementIndent()
        self.write("<keyword> let </keyword>\n")
        self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "IDENTIFIER"
        self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
        self.tokenizer.advance()
        if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
            self.compileExpression()
            assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "]"
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "="
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.compileExpression()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ";"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.decrementIndent()
        self.write("</letStatement>\n")

    def compileWhile(self):
        self.write("<whileStatement>\n")
        self.incrementIndent()
        self.write("<keyword> while </keyword>\n")
        self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "("
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.compileExpression()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ")"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "{"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.compileStatements()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "}"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.decrementIndent()
        self.write("</whileStatement>\n")

    def compileReturn(self):
        self.write("<returnStatement>\n")
        self.incrementIndent()
        self.write("<keyword> return </keyword>\n")
        self.tokenizer.advance()
        if self.tokenizer.tokenType() != "SYMBOL" and self.tokenizer.symbol() != ";":
            self.compileExpression()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ";"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.decrementIndent()
        self.write("</returnStatement>\n")

    def compileIf(self):
        self.write("<ifStatement>\n")
        self.incrementIndent()
        self.write("<keyword> if </keyword>\n")
        self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "("
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.compileExpression()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ")"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "{"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        self.compileStatements()
        assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "}"
        self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
        self.tokenizer.advance()
        if self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() == "else":
            self.write("<keyword> else </keyword>\n")
            self.tokenizer.advance()
            assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "{"
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
            self.compileStatements()
            assert self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "}"
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
        self.decrementIndent()
        self.write("</ifStatement>\n")

    def compileExpression(self):
        """
        Compile an expression.
        """
        self.write("<expression>\n")
        self.incrementIndent()
        self.compileTerm()
        while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in ["+", "-", "*", "/", "&", "|", "<", ">", "=",
                                                                                     "&lt;", "&gt;", "&amp;"]:
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
            self.compileTerm()
        self.decrementIndent()
        self.write("</expression>\n")

    def compileTerm(self):
        """
        Compile a term. If the current token is an identifier, the routine must distinguish between a variable,
        an array entry, and a subroutine call. A single look-ahead token, which may be one of "[", "(", or ".",
        suffices to distinguish between the possibilities. Any other token is not part of this term and should not
        be advanced over.
        """
        self.write("<term>\n")
        self.incrementIndent()
        if self.tokenizer.tokenType() == "INT_CONST":
            self.write("<integerConstant> {} </integerConstant>\n".format(self.tokenizer.intVal()))
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "STRING_CONST":
            self.write("<stringConstant> {} </stringConstant>\n".format(self.tokenizer.stringVal()))
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "KEYWORD" and self.tokenizer.keyword() in ["true", "false", "null", "this"]:
            self.write("<keyword> {} </keyword>\n".format(self.tokenizer.keyword()))
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
            self.compileExpression()
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
        elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() in ["-", "~"]:
            self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
            self.tokenizer.advance()
            self.compileTerm()
        elif self.tokenizer.tokenType() == "IDENTIFIER":
            self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
            self.tokenizer.advance()
            if self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "[":
                self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
                self.tokenizer.advance()
                self.compileExpression()
                self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
                self.tokenizer.advance()
            elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == "(":
                self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
                self.tokenizer.advance()
                self.compileExpressionList()
                self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
                self.tokenizer.advance()
            elif self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ".":
                self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
                self.tokenizer.advance()
                self.write("<identifier> {} </identifier>\n".format(self.tokenizer.identifier()))
                self.tokenizer.advance()
                self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
                self.tokenizer.advance()
                self.compileExpressionList()
                self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
                self.tokenizer.advance()
        self.decrementIndent()
        self.write("</term>\n")

    def compileExpressionList(self):
        """
        Compile a (possibly empty) comma-separated list of expressions.
        """
        self.write("<expressionList>\n")
        self.incrementIndent()
        if self.tokenizer.tokenType() != "SYMBOL" or self.tokenizer.symbol() != ")":
            self.compileExpression()
            while self.tokenizer.tokenType() == "SYMBOL" and self.tokenizer.symbol() == ",":
                self.write("<symbol> {} </symbol>\n".format(self.tokenizer.symbol()))
                self.tokenizer.advance()
                self.compileExpression()
        self.decrementIndent()
        self.write("</expressionList>\n")

    def incrementIndent(self):
        """
        Increment the indentation level.
        """
        self.indent += self.indent_increment

    def decrementIndent(self):
        """
        Decrement the indentation level.
        """
        self.indent -= self.indent_increment

    def write(self, string):
        """
        Write the string to the output file.
        """
        self.output_stream.write(" " * self.indent + string)