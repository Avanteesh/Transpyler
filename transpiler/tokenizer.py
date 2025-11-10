import sys
from dataclasses import dataclass
from transpiler.models.lexeme import Lexeme
from transpiler.grammar import Grammar, RESERVED_WORDS, NAMED_OPERATORS

class Tokenizer:
    def __init__(self, file):
        self.file = file
        self.code = None
        self.line_no = 1
        self.token_streams = []
        self.index = 0

    def __tokenize_name(self):
        token = Lexeme(lexeme="",lex_type=Grammar.RESERVED_NAME)
        while True:
            if self.code[self.index] == '(' or self.code[self.index] == ')' or self.code[self.index] == '}' or self.code[self.index] == '\n' or self.code[self.index] == ';' or self.code[self.index] == " " or self.code[self.index] == ',' or self.code[self.index] == ".":
                    break
            if not (self.code[self.index] == '_' or self.code[self.index].isalpha() or self.code[self.index].isdigit()):
                print(f"LexicalError: invalid token {self.code[self.index]}  at line no. {self.line_no}")
                sys.exit(-1)
            token.lexeme += self.code[self.index]
            self.index += 1
        if token.lexeme in NAMED_OPERATORS:
            token.lex_type = NAMED_OPERATORS[token.lexeme]
        elif token.lexeme not in RESERVED_WORDS:
            token.lex_type = Grammar.NAME
        print(f"TOKEN: {token.lexeme}, {token.lex_type}")
        self.token_streams.append(token)

    def __tokenize_numeric(self):
        """
        Tokenize numeric literals: (Floating point, Hex, Oct, Integer, Binary)
        """
        token = Lexeme(lexeme="",lex_type=Grammar.NUMERIC_LITERAL)
        if self.code[self.index] == '0' and (self.code[self.index + 1] == 'x' or self.code[self.index + 1] == 'b' or self.code[self.index] == 'o'):
            hexdigits = {"a","b","c","d","e","f","A","B","C","D","E","F"}
            decimal_sys = self.code[self.index + 1]
            token.lexeme += f"0{self.code[self.index + 1]}"
            if not (self.code[self.index + 2].isdigit() or self.code[self.index + 2].isalpha()):
                print(f"LexicalError: invalid token {self.code[self.index]} at line no. {self.line_no}")
                sys.exit(-1)
            self.index += 2
            while True:
                if self.code[self.index] == " ":
                    break
                if decimal_sys == 'b':
                    if self.code[self.index] != 0 or self.code[self.index] != 1:
                        print(f"LexicalError: invalid token {self.code[self.index]} at line no. {self.line_no}")
                        sys.exit(-1)
                elif decimal_sys == 'x':
                    if (not self.code[self.index].isdigit()) or (self.code[self.index] not in hexdigits):
                        print(f"LexicalError: invalid token {self.code[self.index]} at line no. {self.line_no}")
                        sys.exit(-1)
                elif decimal_sys == 'o':
                    if not (self.code[self.index] >= "0" and self.code[self.index] <= "7"):
                        print(f"LexicalError: invalid token {self.code[self.index]} at line no. {self.line_no}")
                        sys.exit(-1)
                token.lexeme += self.code[self.index]
                token.lexeme = int(self.code[self.index])
                self.index += 1
        elif self.code[self.index].isdigit() or self.code[self.index] == '.':
            dotfound = self.code[self.index] == '.' and True or False
            while self.code[self.index].isdigit() == True or self.code[self.index] == '.':
                if self.code[self.index] == '.':
                    if dotfound:
                        print(f"Lexical Error: token '{self.code[self.index]}' appears more than ones at line no. {self.line_no}")
                        sys.exit(-1)
                    else:
                        dotfound = True
                token.lexeme += self.code[self.index]
                self.index += 1
            token.lexeme = dotfound and float(token.lexeme) or int(token.lexeme)
        print(f"TOKEN {token.lexeme} , {token.lex_type}")
        self.token_streams.append(token)

    def __tokenize_assigment_or_bitwise(self):
        """
        Tokenize grammar: ("<-", "<<")
        """
        if self.code[self.index + 1] == '-':
            token = Lexeme(lexeme=None, lex_type=Grammar.ASSIGNMENT_OP)
            self.index += 2
        elif self.code[self.index + 1] == '<':
            token = Lexeme(lexeme=None, lex_type=Grammar.L_SHIFT_OP)
            self.index += 2
        print(f"TOKEN {token.lex_type}")
        self.token_streams.append(token)

    def __tokenize_arithmatic_rshift(self):
        """
        Tokenize right shift
        """
        if self.code[self.index + 1] == '>':
            token = Lexeme(lexeme=None, lex_type=Grammar.R_SHIFT_OP)
            self.index += 2
            print(f"TOKEN {token.lexeme}, {token.lex_type}")
            self.token_streams.append(token)
            return
        print("LexicalError: invalid token {self.code[self.index]} at line no. {self.line_no}")
        sys.exit(-1)

    def __tokenize_pipe(self):
        token = None
        if self.code[self.index + 1] == '>':
            self.index += 1
            token = Lexeme(lexeme=None, lex_type=Grammar.RETURN_OP)
        else:
            token = Lexeme(lexeme=None,lex_type=Grammar.BITWISE_OR)
        self.index += 1
        print(f"TOKEN {token.lex_type}")
        self.token_streams.append(token)

    def __tokenize_unary_flip(self):
        token = Lexeme(lexeme=None,lex_type=Grammar.UNARY_FLIP)
        self.index += 1
        print(f"TOKEN {token.lex_type}")
        self.token_streams.append(token)

    def __tokenize_lbrace(self):
        """
        tokenize left bracket or comments
        """
        if self.code[self.index + 1] == '*':
            self.index += 2
            while self.code[self.index] != '*' and self.code[self.index + 1] != ')':
                if self.code[self.index] == '\n':
                    self.line_no += 1
                self.index += 1
            self.index += 2
            return
        token = Lexeme(lexeme=None, lex_type=Grammar.LEFT_BRACE)
        print(f"TOKEN {token.lex_type}")
        self.token_streams.append(token)
        self.index += 1

    def __tokenize_string_literal(self):
        token = Lexeme(lexeme="", lex_type=Grammar.STRING_LITERAL)
        self.index += 1
        while self.code[self.index] != "\"":
            if self.code[self.index] == '\\':
                token.lexeme += self.code[self.index]
                if self.code[self.index + 1] == "\"":
                    token.lexeme += self.code[self.index + 1]
                    self.index += 2
            else:
                token.lexeme += self.code[self.index]
                self.index += 1
        self.index += 1
        return token

    def __tokenize_question_mark(self):
        if self.code[self.index + 1] == '?':
            token = Lexeme(lexeme=None,lex_type=Grammar.NULL_COAL)
            self.index += 2
            print(f"TOKEN {token.lex_type}")
            self.token_streams.append(token)
        print(f"LexicalError: Invalid token '?' found at {self.line_no}")

    def __tokenize_single_line_comment(self):
        self.index += 1
        while self.code[self.index] != '\n':
            self.index += 1
        self.index += 1
        self.line_no += 1
    
    def __tokenize_slash(self):
        token = None
        if self.code[self.index + 1] == '/':
            token = Lexeme(lexeme=None,lex_type=Grammar.FLOOR_DIV_OP)
            self.index += 2
        else:
            token = Lexeme(lexeme=None,lex_type=Grammar.FLOOR_DIV_OP)
            self.index += 1
        print(f"TOKEN {token.lex_type}")
        self.token_streams.append(token)

    def __tokenize_dash(self):
        token = None
        if self.code[self.index + 1] == 'g':
            if self.code[self.index + 2] == 't':
                token = Lexeme(lexeme=None,lex_type=Grammar.GREATER_THAN_OP)
                print("GREATER_THAN_OP")
                self.index += 3
            elif self.code[self.index + 2] == 'e':
                if self.code[self.index + 3] == 'q':
                    token = Lexeme(lexeme=None,lex_type=Grammar.GREATER_OR_EQUAL_OP)
                    print("GREATER_OR_EQUAL_OP")
                    self.index += 4
                else:
                    print(f"LexicalError: Invalid token after '{self.code[self.index + 2]}' at line no. {self.line_no}")
                    sys.exit(-1)
            else:
                print(f"LexicalError: Invalid token after '{self.code[self.index + 1]}' at line no. {self.line_no}")
                sys.exit(-1)
        elif self.code[self.index + 1] == 'l':
            if self.code[self.index + 2] == 't':
                token = Lexeme(lexeme=None,lex_type=Grammar.LESS_THAN_OP)
                print("LESS_THAN_OP")
                self.index += 3
            elif self.code[self.index + 2] == 'e':
                if self.code[self.index + 3] == 'q':
                    token = Lexeme(lexeme=None,lex_type=Grammar.LESS_OR_EQUAL_OP)
                    print("LESS_OR_EQUAL_OP")
                    self.index += 4
                else:
                    print(f"LexicalError: Invalid token after '{self.code[self.index + 2]}' at line no. {self.line_no}")
                    sys.exit(-1)
            else:
                print(f"LexicalError: Invalid token after '{self.code[self.index + 1]}' at line no. {self.line_no}")
                sys.exit(-1)
        elif self.code[self.index + 1] == 'e':
            if self.code[self.index + 2] == 'q':
                token = Lexeme(lexeme=None,lex_type=Grammar.EQUALITY_OP)
                print("EQUALITY_OP")
                self.index += 3
            else:
                print(f"LexicalError: Invalid token after '{self.code[self.index + 1]}' at line no. {self.line_no}")
                sys.exit(-1)
        elif self.code[self.index + 1] == 'n':
            if self.code[self.index + 2] == 'e':
                if self.code[self.index + 3] == 'q':
                    token = Lexeme(lexeme=None,lex_type=Grammar.NOT_EQUAL_OP)
                    print("NOT_EQUAL_OP")
                    self.index += 4
                else:
                    print(f"LexicalError: Invalid token after '{self.code[self.index + 2]}' at line no. {self.line_no}")
                    sys.exit(-1)
            else:
                print(f"LexicalError: Invalid token after '{self.code[self.index + 1]}' at line no. {self.line_no}")
                sys.exit(-1)
        else:
            token = Lexeme(None,lex_type=Grammar.MINUS_OP)
            print("MINUS_OP")
            self.index += 1
        self.token_streams.append(token)
    
    def __call__(self):
        with open(self.file, "r") as f1:
            self.code = f1.read()
            l1 = len(self.code)
            while self.index < l1:
                token = self.code[self.index]
                if token.isalpha() or token == "_":
                    self.__tokenize_name()
                elif token.isdigit() or (token == '.' and self.code[self.index + 1].isdigit()):
                    self.__tokenize_numeric()
                else:
                    match self.code[self.index]:
                        case '<':
                            self.__tokenize_assigment_or_bitwise()
                        case '>':
                            self.__tokenize_arithmatic_rshift()
                        case '(':
                            self.__tokenize_lbrace()
                        case '#':
                            self.__tokenize_single_line_comment()
                        case ',':
                            token = Lexeme(lexeme=None,lex_type=Grammar.COMMA)
                            print("COMMA")
                            self.index += 1
                            self.token_streams.append(token)
                        case ')':
                            token = Lexeme(lexeme=None, lex_type=Grammar.RIGHT_BRACE)
                            print(f"TOKEN {token.lex_type}")
                            self.token_streams.append(token)
                            self.index += 1
                        case '[':
                            token = Lexeme(lexeme=None, lex_type=Grammar.LIST_LEFT_BRACE)
                            print(f"TOKEN LIST_LEFT")
                            self.token_streams.append(token)
                            self.index += 1
                        case ']':
                            token = Lexeme(lexeme=None,lex_type=Grammar.LIST_RIGHT_BRACE)
                            print(f"TOKEN RIGHT_BRACE")
                            self.token_streams.append(token)
                            self.index += 1
                        case '*':
                            token = Lexeme(lexeme=None,lex_type=Grammar.PRODUCT_OP)
                            print(f"TOKEN {token.lex_type}")
                            self.token_streams.append(token)
                            self.index += 1
                        case '/':
                            self.__tokenize_slash()
                        case '^':
                            token = Lexeme(lexeme=None,lex_type=Grammar.POWER_OP)
                            print(f"TOKEN {token.lex_type}")
                            self.token_streams.append(token)
                            self.index += 1
                        case '"':
                            token = self.__tokenize_string_literal()
                            print(f"TOKEN {token.lexeme},{token.lex_type}")
                            self.token_streams.append(token)
                        case ';':
                            token = Lexeme(lexeme=None, lex_type=Grammar.SEMICOLON)
                            print("SEMICOLON")
                            self.token_streams.append(token)
                            self.index += 1
                        case ':':
                            token = Lexeme(lexeme=None, lex_type=Grammar.COLON)
                            print("COLON")
                            self.token_streams.append(token)
                            self.index += 1
                        case '?':
                            self.__tokenize_question_mark()
                        case '+':
                            token = Lexeme(lexeme=None,lex_type=Grammar.PLUS_OP)
                            print("PLUS_OP")
                            self.token_streams.append(token)
                            self.index += 1
                        case '-':
                            self.__tokenize_dash()
                        case '|':
                            self.__tokenize_pipe()
                        case '&':
                            self.token_streams.append(
                             Lexeme(lexeme=None,lex_type=Grammar.BITWISE_AND)
                            )
                            print("BIT_AND")
                            self.index += 1 
                        case '~':
                            self.__tokenize_unary_flip()
                        case '.':
                            self.token_streams.append(
                             Lexeme(lexeme=None,lex_type=Grammar.DOT)
                            )
                            print("DOT")
                            self.index += 1
                        case '\n':
                            self.token_streams.append(
                              Lexeme(lexeme=None,lex_type=Grammar.LINE_END)
                            )
                            print("NEW LINE")
                            self.line_no += 1
                            self.index += 1
                        case ' ':
                            self.index += 1
                

