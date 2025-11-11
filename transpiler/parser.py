import sys
import transpiler.models.new_ast as new_ast
from transpiler.models.lexeme import Lexeme
from transpiler.grammar import Grammar, RESERVED_WORDS
from collections import deque

def check_if_comparision_op(op):
    """
    check if an operator is comparision operator
    """
    return (
      op == Grammar.GREATER_THAN_OP or op == Grammar.LESS_THAN_OP or op == Grammar.LESS_THAN_OP or op == Grammar.GREATER_OR_EQUAL_OP or op == Grammar.LESS_OR_EQUAL_OP or 
      op == Grammar.EQUALITY_OP or op == Grammar.NOT_EQUAL_OP
    )

def operator_precedance(operator) -> int:
    if operator == Grammar.LEFT_BRACE or operator == Grammar.RIGHT_BRACE:
        return 13
    elif check_if_comparision_op(operator):
        return 4
    elif operator == Grammar.POWER_OP:
        return 12
    elif operator == Grammar.UNARY_PLUS_OP or operator == Grammar.UNARY_FLIP or operator == Grammar.UNARY_MINUS_OP:
        return 11
    elif operator == Grammar.PRODUCT_OP or operator == Grammar.DIVISION_OP or operator == Grammar.MODULO_OP or operator == Grammar.FLOOR_DIV_OP:
        return 10
    elif operator == Grammar.PLUS_OP or operator == Grammar.MINUS_OP:
        return 9
    elif operator == Grammar.L_SHIFT_OP or operator == Grammar.R_SHIFT_OP:
        return 8
    elif operator == Grammar.BITWISE_AND:
        return 7
    elif operator == Grammar.BITWISE_XOR:
        return 6
    elif operator == Grammar.BITWISE_OR:
        return 5
    elif operator == Grammar.LOGICAL_NOT:
        return 3
    elif operator == Grammar.LOGICAL_AND:
        return 2
    elif operator == Grammar.LOGICAL_OR or operator == Grammar.NULL_COAL:
        return 1
    return -1

class Parser:
    def __init__(self, token_stream: list[Lexeme]):
        self.token_stream = token_stream
        self.index_ptr = 0
        self.line_no = 1
        self.ast = None
    
    def __check_if_special_operator(self):
        """
        operators which may act both unary and binary (+, -)
        """
        if self.token_stream[self.index_ptr - 1].lex_type != Grammar.NUMERIC_LITERAL and self.token_stream[self.index_ptr - 1].lex_type != Grammar.NAME and self.token_stream[self.index_ptr - 1].lex_type == Grammar.RESERVED_NAME and (self.token_stream[self.index_ptr].lex_type != Grammar.LEFT_BRACE or self.token_stream[self.index_ptr]) == Grammar.RIGHT_BRACE:
            if self.token_stream[self.index_ptr].lex_type == Grammar.PLUS_OP:
                self.token_stream[self.index_ptr].lex_type = Grammar.UNARY_PLUS_OP
            elif self.token_stream[self.index_ptr].lex_type == Grammar.MINUS_OP:
                self.token_stream[self.index_ptr].lex_type = Grammar.UNARY_MINUS_OP

    def __parse_expression(self):
        stack, postfix = [], []
        while True:
            if self.token_stream[self.index_ptr].lex_type == Grammar.SEMICOLON or self.token_stream[self.index_ptr].lex_type == Grammar.LINE_END or self.token_stream[self.index_ptr].lex_type == Grammar.COMMA or self.token_stream[self.index_ptr].lex_type == Grammar.LIST_RIGHT_BRACE:
                break
            elif self.token_stream[self.index_ptr].lex_type == Grammar.LIST_LEFT_BRACE:
                postfix.append(self.__parse_listexp())
            elif self.token_stream[self.index_ptr].lex_type == Grammar.RESERVED_NAME:
                match self.token_stream[self.index_ptr].lexeme:
                    case "do": break
                    case "done": break
                    case "Null": 
                        postfix.append(new_ast.NamedExp(name="Null",line_no=self.line_no))
                        self.index_ptr += 1
                    case "True":
                        postfix.append(new_ast.NamedExp(name="True",line_no=self.line_no))
                        self.index_ptr += 1
                    case "False":
                        postfix.append(new_ast.NamedExp(name="False",line_no=self.line_no))
                    case "fun":
                        postfix.append(self.__parse_anonymous_fun())
            elif self.token_stream[self.index_ptr].lex_type == Grammar.NUMERIC_LITERAL or self.token_stream[self.index_ptr].lex_type == Grammar.STRING_LITERAL:
                postfix.append(new_ast.Constant(value=self.token_stream[self.index_ptr].lexeme,line_no=self.line_no))
                self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.NAME:
                if self.token_stream[self.index_ptr + 1].lex_type == Grammar.LEFT_BRACE:
                    call = self.__parse_function_call()
                    postfix.append(call)
                elif self.token_stream[self.index_ptr + 1].lex_type == Grammar.DOT:
                    attribute = self.__parse_attributenode()
                    postfix.append(attribute)
                else:
                    literal = new_ast.NamedExp(name=self.token_stream[self.index_ptr].lexeme,line_no=self.line_no)
                    postfix.append(literal)
                    self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.LEFT_BRACE:
                stack.append(self.token_stream[self.index_ptr].lex_type)
                self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.RIGHT_BRACE or check_if_comparision_op(self.token_stream[self.index_ptr].lex_type):
                if len(stack) != 0 and check_if_comparision_op(self.token_stream[self.index_ptr].lex_type):
                    while True:
                        if not stack:
                            break
                        elif stack[-1] == Grammar.LEFT_BRACE:
                            break
                        item = stack.pop()
                        postfix.append(item)
                    if len(stack) != 0:
                        stack.pop()
                if check_if_comparision_op(self.token_stream[self.index_ptr].lex_type):
                    stack.append(self.token_stream[self.index_ptr].lex_type)
                self.index_ptr += 1
            else:
                self.__check_if_special_operator()
                if not (self.token_stream[self.index_ptr].lex_type == Grammar.UNARY_MINUS_OP or self.token_stream[self.index_ptr].lex_type == Grammar.UNARY_PLUS_OP):
                    if len(stack) > 0:
                        first = operator_precedance(self.token_stream[self.index_ptr].lex_type)
                        while (len(stack) != 0) and (first <= operator_precedance(stack[-1])) and stack[-1] != Grammar.LEFT_BRACE:
                            postfix.append(stack.pop())
                stack.append(self.token_stream[self.index_ptr].lex_type)
                self.index_ptr += 1
        while len(stack) != 0:
            postfix.append(stack.pop())
        res_expression = new_ast.Expr(line_no=self.line_no)
        for tokens in postfix:
            if isinstance(tokens, new_ast.Constant) == True or isinstance(tokens, new_ast.NamedExp) == True or isinstance(tokens, new_ast.FunctionCall) or isinstance(tokens, new_ast.AnonymousFuncExp) or isinstance(tokens, new_ast.Attribute) or isinstance(tokens, new_ast.ListObj):
                stack.append(tokens)
            elif tokens == Grammar.PLUS_OP or tokens == Grammar.MINUS_OP or tokens == Grammar.POWER_OP or tokens == Grammar.PRODUCT_OP or tokens == Grammar.MODULO_OP or tokens == Grammar.DIVISION_OP or tokens == Grammar.FLOOR_DIV_OP or tokens == Grammar.BITWISE_AND or tokens == Grammar.BITWISE_XOR or tokens == Grammar.BITWISE_OR or tokens == Grammar.L_SHIFT_OP or tokens == Grammar.R_SHIFT_OP or tokens == Grammar.NULL_COAL:
                first, second = stack.pop(), stack.pop()
                binexp = new_ast.BinaryExp(op=tokens,left=second,right=first,line_no=self.line_no)
                stack.append(binexp)
            elif tokens == Grammar.UNARY_FLIP or tokens == Grammar.UNARY_PLUS_OP or tokens == Grammar.UNARY_MINUS_OP or tokens == Grammar.LOGICAL_NOT:
                operand = stack.pop()
                unaryexp = new_ast.UnaryExp(op=tokens,operand=operand,line_no=self.line_no)
                stack.append(unaryexp)
            elif tokens == Grammar.LOGICAL_AND or tokens == Grammar.LOGICAL_OR:
                first, second = stack.pop(), stack.pop()
                boolexp = new_ast.BooleanExp(tokens,left=second,right=first,line_no=self.line_no)
                stack.append(boolexp)
            elif check_if_comparision_op(tokens):
                first, second, compareexp = stack.pop(), stack.pop(), None
                if isinstance(second, new_ast.ComparatorExp):
                    compareexp = new_ast.ComparatorExp(tokens,left=first,line_no=self.line_no)
                    compareexp.op += second.op 
                    compareexp.comparator = [*second.comparator,second.left]
                else:
                    compareexp = new_ast.ComparatorExp(tokens,left=second,line_no=self.line_no)
                    compareexp.comparator.append(first)
                stack.append(compareexp)
        res_expression.value = stack.pop()
        return res_expression

    def __parse_function_call(self):
        name_exp = new_ast.NamedExp(self.token_stream[self.index_ptr].lexeme,self.line_no)
        functioncall = new_ast.FunctionCall(name_exp, self.line_no)
        self.index_ptr += 2
        while True:
            if self.token_stream[self.index_ptr].lex_type == Grammar.COMMA:
                self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.RIGHT_BRACE:
                if self.token_stream[self.index_ptr + 1].lex_type == Grammar.SEMICOLON:
                    self.index_ptr += 2
                elif self.token_stream[self.index_ptr + 1].lex_type == Grammar.RIGHT_BRACE:
                    pass

                else:
                    self.index_ptr += 1
                break
            else:
                argument = self.__parse_expression()
                functioncall.arguments.append(argument)
                if self.token_stream[self.index_ptr].lex_type == Grammar.SEMICOLON:
                    self.index_ptr -= 1
                else:
                    self.index_ptr += 1
        return functioncall

    def __parse_anonymous_fun(self) -> new_ast.AnonymousFuncExp:
        self.index_ptr += 1
        anonymousfn = new_ast.AnonymousFuncExp(self.line_no)
        while True:
            if self.token_stream[self.index_ptr].lexeme == "do":
                break
            elif self.token_stream[self.index_ptr].lex_type == Grammar.COMMA:
                self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.NAME:
                if self.token_stream[self.index_ptr + 1].lex_type == Grammar.COMMA or self.token_stream[self.index_ptr + 1].lexeme == "do":
                    argobj = new_ast.ArgumentObject(
                      self.token_stream[self.index_ptr].lexeme,self.line_no
                    )
                    anonymousfn.arg_list.append(argobj)
                    self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.LEFT_BRACE:
                self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.RIGHT_BRACE:
                self.index_ptr += 1
        self.index_ptr += 1
        anonymousfn.expression = self.__parse_expression()
        return anonymousfn

    def __parse_assignment_exp(self) -> new_ast.AssignmentExpr:
        assignexp = new_ast.AssignmentExpr(self.line_no)
        if self.token_stream[self.index_ptr + 1].lex_type == Grammar.ASSIGNMENT_OP:
            name = new_ast.NamedExp(self.token_stream[self.index_ptr].lexeme,self.line_no)
            assignexp.target.append(name)
            self.index_ptr += 2
            expr = self.__parse_expression()
            assignexp.value.append(expr)
            self.index_ptr += 1
        else:
            while self.token_stream[self.index_ptr].lex_type != Grammar.ASSIGNMENT_OP:
                if self.token_stream[self.index_ptr].lex_type == NAME:
                    name = new_ast.NamedExp(self.token_stream[self.index_ptr].lexeme, self.line_no)
                    assignexp.target.append(name)
                    self.index_ptr += 1
                elif self.token_stream[self.index_ptr].lex_type == COMMA:
                    self.index_ptr += 1
                else:
                    raise SyntaxError(f"Invalid token '{self.token_stream[self.index_ptr].lexeme}'")
            while self.token_stream[self.index_ptr].lex_type != Grammar.SEMICOLON or self.token_stream[self.index_ptr].lex_type != Grammar.LINE_END:
                expression = self.__parse_expression()
                assignexp.value.append(expression)
                if self.token_stream[self.index_ptr].lex_type == COMMA:
                    self.index_ptr += 1
        return assignexp

    def __parse_listexp(self) -> new_ast.ListObj:
        self.index_ptr += 1
        lis_obj = new_ast.ListObj(self.line_no)
        while True:
            if self.token_stream[self.index_ptr].lex_type == Grammar.LIST_RIGHT_BRACE:
                self.index_ptr += 1
                break
            elif self.token_stream[self.index_ptr].lex_type == Grammar.COMMA:
                self.index_ptr += 1
            else:
                expression = self.__parse_expression()
                lis_obj.elts.append(expression)
        return lis_obj

    def __parse_ifstatement(self) -> new_ast.IfStatement:
        self.index_ptr += 1
        ifstatement = new_ast.IfStatement(self.__parse_expression(),self.line_no)
        if self.token_stream[self.index_ptr].lexeme != "do":
            print(f"LexicalError: missing token do after if condition!")
            sys.exit(-1)
        self.index_ptr += 1
        ifstatement.body = self.__body_parser()
        if self.token_stream[self.index_ptr].lexeme == "elif":
            ifstatement.orelse.append(self.__parse_ifstatement())
        elif self.token_stream[self.index_ptr].lexeme == "else":
            self.index_ptr += 1
            ifstatement.orelse = self.__body_parser()
            if self.token_stream[self.index_ptr - 1].lexeme != "done":
                print("LexicalError: missing token 'done' after if statement end block!")
                sys.exit(-1)
        return ifstatement

    def __parse_until_loop(self) -> new_ast.UntilLoop:
        self.index_ptr += 1
        until_loop = new_ast.UntilLoop(condition=self.__parse_expression(),line_no=self.line_no)
        if self.token_stream[self.index_ptr].lexeme != "do":
            print(f"LexicalError: missing token do after if condition!")
            sys.exit(-1)
        self.index_ptr += 1
        until_loop.body = self.__body_parser()
        if self.token_stream[self.index_ptr - 1].lexeme != "done":
            print("LexicalError: missing token 'done' after until loop block")
            sys.exit(-1)
        return until_loop

    def __parse_enumdef(self) -> new_ast.EnumDef:
        if self.token_stream[self.index_ptr + 1].lex_type == Grammar.NAME:
            name = self.token_stream[self.index_ptr + 1].lexeme
            if not name[0].isupper():
                print("LexicalError: enum declarations must be in upper case only!")
                sys.exit(-1)
            enumdef = new_ast.EnumDef(name=name,line_no=self.line_no)
            if self.token_stream[self.index_ptr + 2].lexeme != "do":
                print("LexicalError: missing 'do' statement!")
                sys.exit(-1)
            self.index_ptr += 3
            while True:
                if self.token_stream[self.index_ptr].lexeme == "done":
                    break
                elif self.token_stream[self.index_ptr].lex_type == Grammar.COMMA:
                    self.index_ptr += 1
                elif self.token_stream[self.index_ptr].lex_type == Grammar.LINE_END:
                    self.index_ptr += 1
                elif self.token_stream[self.index_ptr].lex_type == Grammar.NAME:
                    namedexp = new_ast.NamedExp(name=self.token_stream[self.index_ptr].lexeme)
                    enumdef.constants.append(namedexp)
                    if self.token_stream[self.index_ptr + 1].lex_type == Grammar.COMMA or self.token_stream[self.index_ptr + 1].lex_type == Grammar.LINE_END:
                        init_len = len(enumdef.values)
                        enumdef.values.append(new_ast.Constant(value=init_len))
                        self.index_ptr += 1
                    elif self.token_stream[self.index_ptr + 1].lex_type  == Grammar.ASSIGNMENT_OP:
                        self.index_ptr += 2
                        if self.token_stream[self.index_ptr].lex_type == Grammar.COMMA:
                            print("LexicalError: Missing expression after assignment!")
                            sys.exit(-1)
                        expr = self.__parse_expression()
                        enumdef.values.append(expr)
            return enumdef
        print("LexicalError: missing 'name' after enum declaration!")
        sys.exit(-1)

    def __parse_structdef(self, mutable: bool=False) -> new_ast.StructDef:
        self.index_ptr += 1
        if self.token_stream[self.index_ptr].lex_type != Grammar.NAME:
            print("LexicalError: missing struct name!")
            sys.exit(-1)
        name = self.token_stream[self.index_ptr].lexeme
        if not name[0].isupper():
            print("LexicalError: struct name should be capitalized!")
            sys.exit(-1)
        structdef = new_ast.StructDef(name, mutable,self.line_no)
        if self.token_stream[self.index_ptr + 1].lexeme != "do":
            print("LexicalError: missing 'do' statement!")
            sys.exit(-1)
        self.index_ptr += 2
        while True:
            if self.token_stream[self.index_ptr].lexeme == "done":
                break
            elif self.token_stream[self.index_ptr].lex_type == Grammar.NAME:
                structdef.variables.append(self.token_stream[self.index_ptr].lexeme)
                if self.token_stream[self.index_ptr + 1].lex_type == Grammar.SEMICOLON:
                    structdef.values.append(None)
                    self.index_ptr += 2
                elif self.token_stream[self.index_ptr + 1].lex_type == Grammar.ASSIGNMENT_OP:
                    self.index_ptr += 2
                    expr = self.__parse_expression()
                    structdef.values.append(expr)
                    self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.LINE_END:
                self.index_ptr += 1
                self.line_no += 1
        return structdef

    def __parse_attributenode(self) -> new_ast.Attribute:
        attribute_node = new_ast.Attribute(
          value=new_ast.NamedExp(name=self.token_stream[self.index_ptr].lexeme,line_no=self.line_no),
          line_no=self.line_no
        )
        if self.token_stream[self.index_ptr + 2].lex_type == Grammar.NAME:
            if self.token_stream[self.index_ptr + 3].lex_type == Grammar.DOT:
                attribute_node.attr = self.token_stream[self.index_ptr + 2].lexeme
                self.index_ptr += 3
            else:
                attribute_node.attr = self.token_stream[self.index_ptr + 2].lexeme
                self.index_ptr += 3
        while True:
            if self.token_stream[self.index_ptr].lex_type == Grammar.NAME:
                if self.token_stream[self.index_ptr + 1].lex_type == Grammar.DOT:
                    self.index_ptr += 1
                    new_attr = new_ast.Attribute(value=attribute_node)
                    if self.token_stream[self.index_ptr + 1].lex_type == Grammar.NAME:
                        new_attr.attr = self.token_stream[self.index_ptr + 1].lexeme
                        attribute_node = new_attr
                        self.index_ptr += 1
                else:
                    self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.DOT:
                self.index_ptr += 1
            else:
                break
        return attribute_node

    def __parse_exit_call(self) -> new_ast.Exit:
        self.index_ptr += 1
        exit_call = new_ast.Exit(line_no=self.line_no)
        if self.token_stream[self.index_ptr].lex_type == Grammar.SEMICOLON or self.token_stream[self.index_ptr].lex_type == Grammar.LINE_END:
            return exit_call
        exit_call.call_arg = self.__parse_expression()
        return exit_call

    def __parse_fromimport(self) -> new_ast.FromImport:
        self.index_ptr += 1 
        moduleobj = new_ast.FromImport(module='', line_no=self.line_no)
        while True:
            if self.token_stream[self.index_ptr].lexeme == "import":
                self.index_ptr += 1
                break
            elif self.token_stream[self.index_ptr].lex_type == Grammar.NAME:
                if self.token_stream[self.index_ptr + 1].lex_type == Grammar.DOT or self.token_stream[self.index_ptr + 1].lexeme == "import":
                    moduleobj.module += self.token_stream[self.index_ptr].lexeme
                else:
                    print("LexicalError: invalid token found after from import!")
                    sys.exit(-1)
            elif self.token_stream[self.index_ptr].lex_type == Grammar.DOT:
                moduleobj.module += "."
            self.index_ptr += 1
        while True:
            if self.token_stream[self.index_ptr].lex_type == Grammar.SEMICOLON or self.token_stream[self.index_ptr].lex_type == Grammar.LINE_END:
                break
            elif self.token_stream[self.index_ptr].lex_type == Grammar.NAME:
                moduleobj.names.append(new_ast.NamedExp(name=self.token_stream[self.index_ptr].lexeme,line_no=self.line_no))
                self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.COMMA:
                self.index_ptr += 1
        return moduleobj

    def __parse_functiondef(self) -> new_ast.FunctionDef:
        fdef = new_ast.FunctionDef(function_name='', line_no=self.line_no)
        if self.token_stream[self.index_ptr + 1].lex_type == Grammar.NAME:
            name = self.token_stream[self.index_ptr + 1]
            if name.lexeme.islower() or name.lexeme[0] == '_':
                fdef.function_name = new_ast.NamedExp(name.lexeme, self.line_no)
            else:
                print(f"LexicalError: function name must be a lower case alphabet!")
                sys.exit(-1)
            self.index_ptr += 2
            if self.token_stream[self.index_ptr].lex_type == Grammar.LEFT_BRACE:
                self.index_ptr += 1
                while True:
                    match self.token_stream[self.index_ptr].lex_type:
                        case Grammar.RIGHT_BRACE:
                            self.index_ptr += 1
                            break
                        case Grammar.COMMA:
                            self.index_ptr += 1
                        case Grammar.NAME:
                            arg_obj = new_ast.ArgumentObject(
                             self.token_stream[self.index_ptr].lexeme
                            )
                            fdef.arg_list.append(arg_obj)
                            self.index_ptr += 1
                if self.token_stream[self.index_ptr].lexeme == "do":
                    self.index_ptr += 1
                    fdef.body = self.__body_parser()
                    return fdef
                else:
                    print("LexicalError: 'do' statement missing after function declaration")
        else:
            print(f"LexicalError: function name cannot be annonymous!")
            sys.exit(-1)


    def __body_parser(self):
        body = []
        size = len(self.token_stream)
        while self.index_ptr < size:
            if self.token_stream[self.index_ptr].lex_type == Grammar.NAME:
                if self.token_stream[self.index_ptr + 1].lex_type == Grammar.ASSIGNMENT_OP or self.token_stream[self.index_ptr + 1].lex_type == Grammar.COMMA:
                    body.append(self.__parse_assignment_exp())
                elif self.token_stream[self.index_ptr + 1].lex_type == Grammar.LEFT_BRACE:
                    exp = new_ast.Expr(self.__parse_function_call())
                    body.append(exp)
                elif self.token_stream[self.index_ptr + 1].lex_type == Grammar.DOT:
                    attribute = new_ast.Expr(self.__parse_attribute_node())
                    body.append(attribute)
            elif self.token_stream[self.index_ptr].lex_type == Grammar.LINE_END:
                self.line_no += 1
                self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.RESERVED_NAME:
                match self.token_stream[self.index_ptr].lexeme:
                    case "funcdef":
                        body.append(self.__parse_functiondef())
                    case "Enum":
                        body.append(self.__parse_enumdef())
                        self.index_ptr += 1
                    case "struct":
                        body.append(self.__parse_structdef())
                        self.index_ptr += 1
                    case "mutable":
                        if self.token_stream[self.index_ptr + 1].lexeme == "struct":
                            self.index_ptr += 1
                            body.append(self.__parse_structdef(True))
                            self.index_ptr += 1
                        else:
                            print("LexicalError: invalid use of the keyword 'mutable'")
                            sys.exit(-1)
                    case "until":
                        body.append(self.__parse_until_loop())
                    case "break":
                        body.append(new_ast.Break(self.line_no))
                        self.index_ptr += 1
                    case "continue":
                        body.append(new_ast.Continue(self.line_no))
                        self.index_ptr += 1
                    case "exit":
                        body.append(self.__parse_exit_call())
                        self.index_ptr += 1
                    case "done":
                        self.index_ptr += 1
                        break
                    case "else":
                        break
                    case "elif":
                        break
                    case "if":
                        body.append(self.__parse_ifstatement())
                    case "from":
                        body.append(self.__parse_fromimport())
                        self.index_ptr += 1
                    case _:
                        print("LexicalError: invalid declaration of {self.token_stream[self.index_ptr].lexeme}")
                        sys.exit(-1)
            elif self.token_stream[self.index_ptr].lex_type == Grammar.RETURN_OP:
                retexp = new_ast.Return()
                self.index_ptr += 1
                if self.token_stream[self.index_ptr].lex_type == Grammar.LINE_END:
                    print("LexicalError: must include a semicolon for implicit return")
                    sys.exit(-1)
                retexp.value = self.__parse_expression()
                body.append(retexp)
                self.index_ptr += 1
            elif self.token_stream[self.index_ptr].lex_type == Grammar.SEMICOLON:
                break
        return body
             
    def __call__(self):
        self.ast = new_ast.Module(body=self.__body_parser())


