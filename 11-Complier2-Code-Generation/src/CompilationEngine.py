class CompilationEngine:
    def __init__(self, tokenizer, symbol_table, vm_writer):
        """
        Creates a new compilation engine with the given input and output.
        The next routine called must be compileClass().
        Input: input_stream - the input stream
                output_stream - the output stream
        """
        self._tokenizer = tokenizer   # JackTokenizer
        self._symbol_table = symbol_table   # SymbolTable
        self._vm_writer = vm_writer   # VMWriter
        self._class_name = None   # current class name
        self._while_count = 0   # while count
        self._if_count = 0   # if count
        self.KIND_TABLE = {   # kind table
            "STATIC": "STATIC",
            "FIELD": "THIS",
            "ARG": "ARG",
            "VAR": "LOCAL"
        }

    def eat_token(self, token_type, token_value=None):
        """
        Check if the next token is of the given type and if so, consume it as the current token.
        """
        if not self._tokenizer.hasMoreTokens():   # check if there are more tokens
            raise Exception("Expected more tokens but reached the end of the file")
        self._tokenizer.advance()   # read the next token
        if self._tokenizer.tokenType() != token_type:
            raise Exception("Expected token type {} but got {}".format(token_type, self._tokenizer.tokenType()))
        if token_type == "KEYWORD":
            token = self._tokenizer.keyword()
        elif token_type == "SYMBOL":
            token = self._tokenizer.symbol()
        elif token_type == "INT_CONST":
            token = self._tokenizer.intVal()
        elif token_type == "STRING_CONST":
            token = self._tokenizer.stringVal()
        elif token_type == "IDENTIFIER":
            token = self._tokenizer.identifier()
        if token_value is None or token == token_value or token in token_value:
            return token
        else:
            raise Exception("Expected token value {} but got {}".format(token_value, token))
        
    def peek_token(self):
        """
        Return the next token without consuming it.
        """
        if not self._tokenizer.hasMoreTokens():
            raise Exception("Expected more tokens but reached the end of the file")
        return self._tokenizer.peek()

    def compileClass(self):
        """
        Compiles a complete class.
        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.eat_token("KEYWORD", "class")   # 'class'
        self._class_name = self.eat_token("IDENTIFIER")   # className
        self.eat_token("SYMBOL", "{")   # '{'
        while self.peek_token() in ["static", "field"]:
            self.compileClassVarDec()
        while self.peek_token() in ["constructor", "function", "method"]:
            self.compileSubroutine()
        self.eat_token("SYMBOL", "}")   # '}'

    def get_type(self):
        """
        Return the type of the current token.
        """
        if self.peek_token() in ["int", "char", "boolean", "void"]:
            return self.eat_token("KEYWORD", ["int", "char", "boolean", "void"])
        else:
            return self.eat_token("IDENTIFIER")

    def compileClassVarDec(self):
        """
        Compiles a static declaration or a field declaration.
        classVarDec: ('static' | 'field') type varName (',' varName)* ';'
        """
        kind = self.eat_token("KEYWORD", ["static", "field"])   # ('static' | 'field')
        type = self.get_type()   # type
        name = self.eat_token("IDENTIFIER")   # varName
        self._symbol_table.define(name, type, kind.upper())
        while self.peek_token() == ",":
            self.eat_token("SYMBOL", ",")
            name = self.eat_token("IDENTIFIER")   # varName
            self._symbol_table.define(name, type, kind.upper())
        self.eat_token("SYMBOL", ";")   # ';'

    def compileSubroutine(self):
        """
        Compiles a complete method, function, or constructor.
        subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        """
        self._symbol_table.startSubroutine()   # reset subroutine symbol table
        sub_kind = self.eat_token("KEYWORD", ["constructor", "function", "method"])
        if sub_kind == "method":
            self._symbol_table.define("this", self._class_name, "ARG")
        sub_type = self.get_type()   # ('void' | type)
        sub_name = self.eat_token("IDENTIFIER")   # subroutineName
        self.eat_token("SYMBOL", "(")   # '('
        self.compileParameterList()   # parameterList
        self.eat_token("SYMBOL", ")")   # ')'
        self.eat_token("SYMBOL", "{")   # '{'
        while self.peek_token() == "var":
            self.compileVarDec()
        self._vm_writer.write_function("{}.{}".format(self._class_name, sub_name), self._symbol_table.varCount("VAR"))
        if sub_kind == "constructor":
            self._vm_writer.write_push("CONST", self._symbol_table.varCount("FIELD"))
            self._vm_writer.write_call("Memory.alloc", 1)
            self._vm_writer.write_pop("POINTER", 0)
        elif sub_kind == "method":
            self._vm_writer.write_push("ARG", 0)
            self._vm_writer.write_pop("POINTER", 0)
        self.compileStatements()   # statements
        self.eat_token("SYMBOL", "}")   # '}'

    def compileParameterList(self):
        """
        Compiles a (possibly empty) parameter list, not including the enclosing "()".
        parameterList: ((type varName) (',' type varName)*)?
        """
        if self.peek_token() == ")":
            return
        type = self.get_type()   # type
        # type = self.eat_token("KEYWORD")   # type
        name = self.eat_token("IDENTIFIER")   # varName
        self._symbol_table.define(name, type, "ARG")
        while self.peek_token() == ",":
            self.eat_token("SYMBOL", ",")
            type = self.get_type()   # type
            name = self.eat_token("IDENTIFIER")
            self._symbol_table.define(name, type, "ARG")
    
    def compileVarDec(self):
        """
        Compiles a var declaration.
        varDec: 'var' type varName (',' varName)* ';'
        """
        self.eat_token("KEYWORD", "var")   # 'var'
        type = self.get_type()   # type
        name = self.eat_token("IDENTIFIER")   # varName
        self._symbol_table.define(name, type, "VAR")
        while self.peek_token() == ",":   # (',' varName)*
            self.eat_token("SYMBOL", ",")
            name = self.eat_token("IDENTIFIER")
            self._symbol_table.define(name, type, "VAR")
        self.eat_token("SYMBOL", ";")

    def compileStatements(self):
        """
        Compiles a sequence of statements, not including the enclosing "{}".
        statements: statement*
        """
        while self.peek_token() in ["let", "if", "while", "do", "return"]:
            if self.peek_token() == "let":
                self.compileLet()
            elif self.peek_token() == "if":
                self.compileIf()
            elif self.peek_token() == "while":
                self.compileWhile()
            elif self.peek_token() == "do":
                self.compileDo()
            elif self.peek_token() == "return":
                self.compileReturn()

    def compileDo(self):
        """
        Compiles a do statement.
        doStatement: 'do' subroutineCall ';'
        """
        self.eat_token("KEYWORD", "do")
        self.compileSubroutineCall()
        self._vm_writer.write_pop("TEMP", 0)
        self.eat_token("SYMBOL", ";")

    def compileLet(self):
        """
        Compiles a let statement.
        letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.eat_token("KEYWORD", "let")   # 'let'
        name = self.eat_token("IDENTIFIER")   # varName
        if self.peek_token() == "[":   # ('[' expression ']')?
            self.eat_token("SYMBOL", "[")
            self.compileExpression()
            self.eat_token("SYMBOL", "]")
            self._vm_writer.write_push(self.KIND_TABLE[self._symbol_table.kindOf(name)], self._symbol_table.indexOf(name))
            self._vm_writer.write_arithmetic("ADD")
            self._vm_writer.write_pop("TEMP", 0)
            self.eat_token("SYMBOL", "=")
            self.compileExpression()
            self._vm_writer.write_push("TEMP", 0)
            self._vm_writer.write_pop("POINTER", 1)
            self._vm_writer.write_pop("THAT", 0)
        else:
            self.eat_token("SYMBOL", "=")
            self.compileExpression()
            self._vm_writer.write_pop(self.KIND_TABLE[self._symbol_table.kindOf(name)], self._symbol_table.indexOf(name))
        self.eat_token("SYMBOL", ";")

    def compileWhile(self):
        """
        Compiles a while statement.
        whileStatement: 'while' '(' expression ')' '{' statements '}'
        """
        self._while_count += 1   # while count
        while_label = "WHILE{}".format(self._while_count)   # while label
        while_end_label = "WHILE_END{}".format(self._while_count)   # while end label
        self._vm_writer.write_label(while_label)   # label WHILE
        self.eat_token("KEYWORD", "while")   # 'while'
        self.eat_token("SYMBOL", "(")   # '('
        self.compileExpression()   # expression
        self._vm_writer.write_arithmetic("NOT")   # NOT
        self._vm_writer.write_if(while_end_label)   # if-goto WHILE_END
        self.eat_token("SYMBOL", ")")   # ')'
        self.eat_token("SYMBOL", "{")   # '{'
        self.compileStatements()   # statements
        self._vm_writer.write_goto(while_label)   # goto WHILE
        self._vm_writer.write_label(while_end_label)   # label WHILE_END
        self.eat_token("SYMBOL", "}")   # '}'

    def compileReturn(self):
        """
        Compiles a return statement.
        returnStatement: 'return' expression? ';'
        """
        self.eat_token("KEYWORD", "return")   # 'return'
        if self.peek_token() != ";":   # expression?
            self.compileExpression()
        else:
            self._vm_writer.write_push("CONST", 0)
        self._vm_writer.write_return()
        self.eat_token("SYMBOL", ";")

    def compileIf(self):
        """
        Compiles an if statement, possibly with a trailing else clause.
        ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        self._if_count += 1   # if count
        if_label = "IF{}".format(self._if_count)   # if label
        else_label = "ELSE{}".format(self._if_count)   # else label
        end_label = "IF_END{}".format(self._if_count)   # if end label
        self.eat_token("KEYWORD", "if")   # 'if'
        self.eat_token("SYMBOL", "(")   # '('
        self.compileExpression()   # expression
        self._vm_writer.write_arithmetic("NOT")   # NOT
        self._vm_writer.write_if(else_label)   # if-goto ELSE
        self.eat_token("SYMBOL", ")")   # ')'
        self.eat_token("SYMBOL", "{")   # '{'
        self.compileStatements()   # statements
        self._vm_writer.write_goto(end_label)   # goto IF_END
        self._vm_writer.write_label(else_label)   # label ELSE
        self.eat_token("SYMBOL", "}")   # '}'
        if self.peek_token() == "else":   # ('else' '{' statements '}')?
            self.eat_token("KEYWORD", "else")   # 'else'
            self.eat_token("SYMBOL", "{")   # '{'
            self.compileStatements()   # statements
            self.eat_token("SYMBOL", "}")   # '}'
        self._vm_writer.write_label(end_label)   # label IF_END

    def compileExpression(self):
        """
        Compiles an expression.
        expression: term (op term)*
        """
        self.compileTerm()   # term
        while self.peek_token() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:   # (op term)*
            op = self.eat_token("SYMBOL")
            self.compileTerm()
            if op == "+":
                self._vm_writer.write_arithmetic("ADD")
            elif op == "-":
                self._vm_writer.write_arithmetic("SUB")
            elif op == "*":
                self._vm_writer.write_call("Math.multiply", 2)
            elif op == "/":
                self._vm_writer.write_call("Math.divide", 2)
            elif op == "&":
                self._vm_writer.write_arithmetic("AND")
            elif op == "|":
                self._vm_writer.write_arithmetic("OR")
            elif op == "<":
                self._vm_writer.write_arithmetic("LT")
            elif op == ">":
                self._vm_writer.write_arithmetic("GT")
            elif op == "=":
                self._vm_writer.write_arithmetic("EQ")
    
    def compileTerm(self):
        """
        Compiles a term. This routine is faced with a slight difficulty when trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routine must distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices to distinguish between the three possibilities.
        Any other token is not part of this term and should not be advanced over.
        term: integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        """
        if self.peek_token() == "(":
            self.eat_token("SYMBOL", "(")
            self.compileExpression()
            self.eat_token("SYMBOL", ")")
        elif self.peek_token() in ["-", "~"]:
            op = self.eat_token("SYMBOL")
            self.compileTerm()
            if op == "-":
                self._vm_writer.write_arithmetic("NEG")
            elif op == "~":
                self._vm_writer.write_arithmetic("NOT")
        elif self.peek_token().isdigit():
            self._vm_writer.write_push("CONST", self.eat_token("INT_CONST"))
        elif self.peek_token().startswith('"'):
            string = self.eat_token("STRING_CONST")
            self._vm_writer.write_push("CONST", len(string))
            self._vm_writer.write_call("String.new", 1)
            for char in string:
                self._vm_writer.write_push("CONST", ord(char))
                self._vm_writer.write_call("String.appendChar", 2)
        elif self.peek_token() in ["true", "false", "null", "this"]:
            keyword = self.eat_token("KEYWORD")
            if keyword == "true":
                self._vm_writer.write_push("CONST", 0)
                self._vm_writer.write_arithmetic("NOT")
            elif keyword == "false":
                self._vm_writer.write_push("CONST", 0)
            elif keyword == "null":
                self._vm_writer.write_push("CONST", 0)
            elif keyword == "this":
                self._vm_writer.write_push("POINTER", 0)
        else:
            name = self.eat_token("IDENTIFIER")
            if self.peek_token() == "[":
                self.eat_token("SYMBOL", "[")
                self.compileExpression()
                self.eat_token("SYMBOL", "]")
                self._vm_writer.write_push(self.KIND_TABLE[self._symbol_table.kindOf(name)], self._symbol_table.indexOf(name))
                self._vm_writer.write_arithmetic("ADD")
                self._vm_writer.write_pop("POINTER", 1)
                self._vm_writer.write_push("THAT", 0)
            elif self.peek_token() in ["(", "."]:
                self.compileSubroutineCall(name)
            else:
                self._vm_writer.write_push(self.KIND_TABLE[self._symbol_table.kindOf(name)], self._symbol_table.indexOf(name))

    def compileExpressionList(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        expressionList: (expression (',' expression)* )?
        """
        n_args = 0   # number of arguments
        if self.peek_token() == ")":   # empty expression list
            return 0
        self.compileExpression()   # expression
        n_args += 1   # increment number of arguments
        while self.peek_token() == ",":
            self.eat_token("SYMBOL", ",")
            self.compileExpression()
            n_args += 1
        return n_args

    def compileSubroutineCall(self, name=None):
        """
        Compiles a subroutine call.
        subroutineCall: subroutineName '(' expressionList ')' | ( className | varName) '.' subroutineName '(' expressionList ')'
        """
        if self.peek_token() == "(":
            if name is None:
                name = self.eat_token("IDENTIFIER")
            self.eat_token("SYMBOL", "(")
            self._vm_writer.write_push("POINTER", 0)
            n_args = self.compileExpressionList()
            self._vm_writer.write_call("{}.{}".format(self._class_name, name), n_args + 1)
            self.eat_token("SYMBOL", ")")
        elif self.peek_token() == ".":
            if name is None:
                name = self.eat_token("IDENTIFIER")
            self.eat_token("SYMBOL", ".")
            sub_name = self.eat_token("IDENTIFIER")
            self.eat_token("SYMBOL", "(")
            if self._symbol_table.kindOf(name) is not None:
                self._vm_writer.write_push(self.KIND_TABLE[self._symbol_table.kindOf(name)], self._symbol_table.indexOf(name))
                n_args = self.compileExpressionList()
                self._vm_writer.write_call("{}.{}".format(self._symbol_table.typeOf(name), sub_name), n_args + 1)
            else:
                n_args = self.compileExpressionList()
                self._vm_writer.write_call("{}.{}".format(name, sub_name), n_args)
            self.eat_token("SYMBOL", ")")
        else:
            name = self.eat_token("IDENTIFIER")
            self.compileSubroutineCall(name)