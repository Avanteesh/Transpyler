import ast
import math
import builtins
import transpiler.models.new_ast as new_ast
from os import path
from transpiler.tokenizer import Tokenizer
from transpiler.parser import Parser
from transpiler.grammar import Grammar
from transpiler.plugins import null
from enum import Enum
from dataclasses import dataclass, field
from typing import Any

class Execution(Enum):
    MODULE = "module"
    SCRIPT = "script"

class CodeTransformer:
    __mod_builtins__ = {name: getattr(builtins, name) for name in dir(builtins)}
    __mod_builtins__.pop('print', None)
    __mod_builtins__.pop('None', None)
    __mod_builtins__.pop('eval',None)
    __mod_builtins__.pop('exec', None)
    __mod_builtins__.pop('compile', None)
    __mod_builtins__.pop('__package__', None)
    __mod_builtins__.pop('__loader__', None)
    __mod_builtins__.pop('__annotations__', None)
    __mod_builtins__.pop('__import__', None)
    __mod_builtins__.pop('globals', None)
    __mod_builtins__.pop('locals', None)
    __mod_builtins__.pop('Ellipsis', None)
    __mod_builtins__.pop('type', None)
    def __init__(self, file, execution_mode: Execution):
        self.file = file
        self.p_ast = None
        self.line_no = 1
        self.execution_mode = execution_mode
        self.env = {
          "__builtins__": CodeTransformer.__mod_builtins__,
          "Null": null,"puts": print,"Infinity": float('inf'),
          "pi": math.pi,"e": math.e,"exp": math.exp,"Enum":Enum,"sin": math.sin,
          "cos": math.cos,"tan": math.tan,"cosec":lambda x: 1/math.sin(x),
          "sec": lambda x: 1/math.cos(x),"cot": lambda x: 1/math.tan(x),
          "arcsin":math.asin,"arccos": math.acos,"arctan":math.atan,"sinh": math.sinh, 
          "cosh": math.cosh,"radians": lambda x: 0.017453292519943295 * x,
          "tanh": math.tanh,"arcsinh": math.asinh, "arccosh": math.acosh,"arctanh":math.atanh,
          "__file__": self.file, "Any": Any,"dataclass": dataclass,"field":field
        }

    def __transform_name(self, n_ast: new_ast.NamedExp) -> ast.Name:
        return ast.Name(id=n_ast.name,lineno=self.line_no)

    def __transform_constant(self, n_ast: new_ast.Constant) -> ast.Constant:
        return ast.Constant(value=n_ast.value,lineno=self.line_no)

    def __transform_unary_operator(self, operator):
        match operator:
            case Grammar.LOGICAL_NOT: return ast.Not()
            case Grammar.UNARY_FLIP: return ast.Invert()
            case Grammar.UNARY_PLUS_OP: return ast.UAdd()
            case Grammar.UNARY_MINUS_OP: return ast.USub()
        raise TypeError("Invalid unary operator")

    def __transform_binary_arithmatic_operator(self, operator):
        match operator:
            case Grammar.PLUS_OP: return ast.Add()
            case Grammar.MINUS_OP: return ast.Sub()
            case Grammar.POWER_OP: return ast.Pow()
            case Grammar.DIVISION_OP: return ast.Div()
            case Grammar.PRODUCT_OP: return ast.Mult()
            case Grammar.FLOOR_DIV_OP: return ast.FloorDiv()
            case Grammar.MODULO_OP: return ast.Mod()
            case Grammar.L_SHIFT_OP: return ast.LShift()
            case Grammar.R_SHIFT_OP: return ast.RShift()
            case Grammar.BITWISE_AND: return ast.BitAnd()
            case Grammar.BITWISE_OR: return ast.BitOr()
            case Grammar.BITWISE_XOR: return ast.BitXor()
        raise TypeError("Invalid binary operator")

    def __transform_compare_op(self, operator):
        match operator:
            case Grammar.EQUALITY_OP: return ast.Eq()
            case Grammar.NOT_EQUAL_OP: return ast.NotEq()
            case Grammar.GREATER_THAN_OP: return ast.Gt()
            case Grammar.GREATER_OR_EQUAL_OP: return ast.GtE()
            case Grammar.LESS_THAN_OP: return ast.Lt()
            case Grammar.LESS_OR_EQUAL_OP: return ast.LtE()
        raise TypeError("Invalid comparision operator")

    def __transform_binary_logical_op(self, operator):
        match operator:
            case Grammar.LOGICAL_AND: return ast.And()
            case Grammar.LOGICAL_OR: return ast.Or()
        raise TypeError("Invalid logical operator!")

    def __transform_expression(self, n_ast: new_ast.NewAST) -> ast.AST:
        if isinstance(n_ast, new_ast.NamedExp):
            return self.__transform_name(n_ast)
        elif isinstance(n_ast, new_ast.UnaryExp):
            return self.__transform_unaryexp(n_ast)
        elif isinstance(n_ast, new_ast.Constant):
            return self.__transform_constant(n_ast)
        elif isinstance(n_ast, new_ast.BinaryExp):
            return self.__transform_binaryexp(n_ast)
        elif isinstance(n_ast, new_ast.BooleanExp):
            return self.__transform_boolexp(n_ast)
        elif isinstance(n_ast, new_ast.Expr):
            return self.__transform_expression(n_ast.value)
        elif isinstance(n_ast, new_ast.FunctionCall):
            return self.__transform_call(n_ast)
        elif isinstance(n_ast, new_ast.ComparatorExp):
            return self.__transform_compareexp(n_ast)
        elif isinstance(n_ast, new_ast.AnonymousFuncExp):
            return self.__transform_anonymousfn(n_ast)
        elif isinstance(n_ast, new_ast.Attribute):
            return self.__transform_attribute(n_ast)
        elif isinstance(n_ast, new_ast.ListObj):
            return self.__transform_listexp(n_ast)

    def __transform_boolexp(self, n_ast: new_ast.BooleanExp) -> ast.BoolOp:
        return ast.BoolOp(
          op=self.__transform_binary_logical_op(n_ast.op),
          values=[
            self.__transform_expression(n_ast.left), 
            self.__transform_expression(n_ast.right)
          ],lineno=self.line_no
        )

    def __transform_compareexp(self, n_ast: new_ast.ComparatorExp) -> ast.Compare:
        return ast.Compare(
          left=self.__transform_expression(n_ast.left),
          ops=[self.__transform_compare_op(op) for op in n_ast.op],
          comparators=[self.__transform_expression(exp) for exp in n_ast.comparator],
          lineno=self.line_no
        )

    def __transform_unaryexp(self, n_ast: new_ast.UnaryExp) -> ast.UnaryOp:
        return ast.UnaryOp(
          op=self.__transform_unary_operator(n_ast.op),
          operand=self.__transform_expression(n_ast.operand),
          lineno=self.line_no
        )

    def __transform_listexp(self, n_ast: new_ast.ListObj) -> ast.List:
        lis_obj = ast.List(elts=[],lineno=self.line_no)
        for items in n_ast.elts:
            lis_obj.elts.append(self.__transform_expression(items))
        return lis_obj

    def __transform_binaryexp(self, n_ast: new_ast.BinaryExp) -> ast.BoolOp | ast.BinOp:
        if n_ast.op == Grammar.NULL_COAL:
            compare = ast.Compare(
             left=self.__transform_expression(n_ast.left),
             ops=[ast.Eq()],comparators=[ast.Constant(value=null())]
            )
            return ast.BoolOp(
              op=ast.Or(),values=[
                ast.BoolOp(
                 op=ast.And(),values=[compare,self.__transform_expression(n_ast.right)]
                ),self.__transform_expression(n_ast.left)
              ]
            )
        return ast.BinOp(
          op=self.__transform_binary_arithmatic_operator(n_ast.op),
          left=self.__transform_expression(n_ast.left), 
          right=self.__transform_expression(n_ast.right),
          lineno=self.line_no
        )

    def __transform_attribute(self, n_ast: new_ast.Attribute) -> ast.Attribute:
        pyattribute = ast.Attribute(value=None,attr=n_ast.attr,lineno=self.line_no)
        pyattribute.value = self.__transform_expression(n_ast.value)
        return pyattribute
    
    def __transform_assign_exp(self, n_ast: new_ast.AssignmentExpr) -> ast.Assign:
        py_assign = ast.Assign(targets=[],value=None,lineno=self.line_no)
        if len(n_ast.target) == 1:
            py_assign.targets.append(self.__transform_name(n_ast.target[0]))
            py_assign.value = self.__transform_expression(n_ast.value[0])
        return py_assign
    
    def __transform_call(self, n_ast: new_ast.FunctionCall) -> ast.Call:
        call_object = ast.Call(
          func=self.__transform_expression(n_ast.function_name),
          args=[],keywords=[],lineno=self.line_no
        )
        for args in n_ast.arguments:
            transformed = self.__transform_expression(args)
            call_object.args.append(transformed)
        return call_object

    def __transform_returnobj(self, node: new_ast.Return) -> ast.Return:
        return ast.Return(
         value=self.__transform_expression(node.value),
         lineno=self.line_no
        )

    def __transform_functiondef(self, node: new_ast.FunctionDef) -> ast.FunctionDef:
        argument_list = ast.arguments(
          args=[],defaults=[],posonlyargs=[],kwonlyargs=[]
        )
        fdef = ast.FunctionDef(
         name=node.function_name.name,args=argument_list,
         decorator_list=[],body=[],lineno=self.line_no
        )
        for argz in node.arg_list:
            fdef.args.args.append(ast.arg(argz.arg_name,lineno=self.line_no))
        fdef.body = self.__transform_tree_body(node.body)
        return fdef
    
    def __transform_ifcond(self, node: new_ast.IfStatement) -> ast.If:
        ifst = ast.If(
          test=self.__transform_expression(node.condition),
          body=[],orelse=[],lineno=self.line_no
        )
        self.line_no += 1
        ifst.body = self.__transform_tree_body(node.body)
        if len(node.orelse) != 0:
            if isinstance(node.orelse[0], new_ast.IfStatement):
                ifst.orelse = [self.__transform_ifcond(node.orelse[0])]
            else:
                ifst.orelse = self.__transform_tree_body(node.orelse)
        return ifst

    def __transform_until_loop(self, node: new_ast.UntilLoop) -> ast.While:
        while_loop = ast.While(
          test=self.__transform_expression(node.condition),
          body=[],orelse=[],lineno=self.line_no
        )
        while_loop.body = self.__transform_tree_body(node.body)
        return while_loop

    def __transform_enumdef(self, node: new_ast.EnumDef) -> ast.ClassDef:
        classdef = ast.ClassDef(
          name=node.enum_name,bases=[ast.Name(id='Enum')],
          keywords=[],body=[],decorator_list=[],type_params=[],
          lineno=self.line_no
        )
        self.line_no += 1
        for constant, value in zip(node.constants, node.values):
            assign_obj = ast.Assign(
              targets=[self.__transform_expression(constant)],
              value=self.__transform_expression(value),
              lineno=self.line_no
            )
            classdef.body.append(assign_obj)
            self.line_no += 1
        return classdef

    def __transform_structdef(self, node: new_ast.StructDef) -> ast.ClassDef:
        if node.mutable:
            decorator = ast.Name(id='dataclass')
        else:
            decorator = ast.Call(
              func=ast.Name(id='dataclass'),args=[],
              keywords=[ast.keyword(arg='frozen',value=ast.Constant(value=True))]
            )
        classdef = ast.ClassDef(
          name=node.struct_name,bases=[],keywords=[],body=[],
          decorator_list=[decorator],type_params=[],lineno=self.line_no
        )
        self.line_no += 1
        for _vars, value in zip(node.variables, node.values):
            assign_obj = ast.AnnAssign(
              target=ast.Name(id=_vars),value=None,
              annotation=ast.Name(id='Any'),simple=1,lineno=self.line_no
            )
            if value is not None:
                assign_obj.value = self.__transform_expression(value)
            else:
                assign_obj.value = ast.Call(
                  func=ast.Name(id='field'),args=[],
                  keywords=[ast.keyword(arg='default_factory',value=ast.Constant(value=null()))]
                )
            classdef.body.append(assign_obj)
            self.line_no += 1
        return classdef

    def __transform_fromimport(self, node: new_ast.FromImport) -> None:
        """
        Load and compile the modules into memory.
        """
        def namespace_found(name):
            for names in node.names:
                if name == names.name:
                    return True
            return False
        modpat = node.module.split(".")
        module_name = path.join(*modpat)
        if not path.exists(f"{module_name}.rpy"):
            raise ModuleNotFoundError(f"The module '{module_name}' doesn't exist!")
        loaded_mod = CodeTransformer(f"{module_name}.rpy", Execution.MODULE) # load the module into memory
        module_ctx = ast.unparse(loaded_mod())   # generated code from module
        compiled_module = compile(module_ctx,"<module>","exec") # compile create a module instance!
        # add dependencies from module namespace on-to the global namespace!
        exec(compiled_module, loaded_mod.env) 
        loaded_mod.env = {
          name: loaded_mod.env[name] for name in loaded_mod.env.keys() if namespace_found(name) 
        }
        self.env |= loaded_mod.env

    def __transform_exit_call(self, node: new_ast.Exit) -> ast.Expr:
        return ast.Expr(
          value=ast.Call(
            func=ast.Name(id='exit'),args=[self.__transform_expression(node.call_arg)],
            keywords=[]
          ),lineno=self.line_no
        )

    def __transform_anonymousfn(self, node: new_ast.AnonymousFuncExp) -> ast.Lambda:
        lambda_node = ast.Lambda(
         args=ast.arguments(
          args=[],posonlyargs=[],kwonlyargs=[],
          kw_defauts=[],defaults=[]
         ),
         body=None,lineno=self.line_no
        )
        for args in node.arg_list:
            arg_obj = ast.arg(arg=args.arg_name)
            lambda_node.args.args.append(arg_obj)
        lambda_node.body = self.__transform_expression(node.expression)
        return lambda_node

    def __transform_tree_body(self, n_ast: list[new_ast.NewAST]):
        body = []
        for node in n_ast:
            if node == Grammar.LINE_END:
                self.line_no += 1
            elif isinstance(node, new_ast.AssignmentExpr):
                body.append(self.__transform_assign_exp(node))
            elif isinstance(node, new_ast.Expr):
                expression = self.__transform_expression(node)
                body.append(ast.Expr(expression,lineno=self.line_no))
                self.line_no += 1
            elif isinstance(node, new_ast.FunctionDef):
                body.append(self.__transform_functiondef(node))
            elif isinstance(node, new_ast.Return):
                body.append(self.__transform_returnobj(node))
                self.line_no += 1
            elif isinstance(node, new_ast.IfStatement):
                body.append(self.__transform_ifcond(node))
            elif isinstance(node, new_ast.EnumDef):
                body.append(self.__transform_enumdef(node))
            elif isinstance(node, new_ast.UntilLoop):
                body.append(self.__transform_until_loop(node))
            elif isinstance(node, new_ast.FromImport):
                self.__transform_fromimport(node)
            elif isinstance(node, new_ast.Break):
                body.append(ast.Break())
                self.line_no += 1
            elif isinstance(node, new_ast.Continue):
                body.append(ast.Continue())
                self.line_no += 1
            elif isinstance(node, new_ast.StructDef):
                body.append(self.__transform_structdef(node))
                self.line_no += 1
            elif isinstance(node, new_ast.Exit):
                body.append(self.__transform_exit_call(node))
                self.line_no += 1
        return body

    def __node_transform(self, n_ast: new_ast.Module):
        self.p_ast = ast.Module(
          body=self.__transform_tree_body(n_ast.body),
          type_ignores=[]
        )

    def __call__(self):
        """
        code execution pipeline!
        """
        tokenizer = Tokenizer(self.file)
        tokenizer()
        parse = Parser(tokenizer.token_streams)
        parse()
        self.__node_transform(parse.ast) # transform parse tree to python ast!
        if self.execution_mode == Execution.SCRIPT:
            code = ast.unparse(self.p_ast)
            print("Transformed code: \n\n",code, "\n\noutput: ")
            res = compile(code,'<string>','exec')
            exec(res, self.env)
        elif self.execution_mode == Execution.MODULE:
            return self.p_ast



