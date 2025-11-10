class NewAST:
    pass

class Module(NewAST):
    def __init__(self, body):
        self.body = body

class Constant(NewAST):
    def __init__(self, value):
        self.value = value

class NamedExp(NewAST):
    def __init__(self, name):
        self.name = name

class Expr(NewAST):
    def __init__(self,value=None):
        self.value = value

class BinaryExp(NewAST):
    def __init__(self, op,left=None,right=None):
        self.op = op
        self.left = left
        self.right = right

class ComparatorExp(NewAST):
    def __init__(self,op,left=None):
        self.op = [op]
        self.left = left
        self.comparator = []

class ArgumentObject(NewAST):
    def __init__(self,arg_name):
        self.arg_name = arg_name
        self.__default_value = None 

class FunctionCall(NewAST):
    def __init__(self,function_name):
        self.function_name = function_name
        self.arguments = []

class BooleanExp(NewAST):
    def __init__(self, op,left=None,right=None):
        self.op = op
        self.left = left
        self.right = right

class UnaryExp(NewAST):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class ListObj(NewAST):
    def __init__(self):
        self.elts = []

class AssignmentExpr(NewAST):
    def __init__(self):
        self.target = []
        self.value = []

class FunctionDef(NewAST):
    def __init__(self, function_name):
        self.function_name = function_name
        self.arg_list = []
        self.body = []

class AnonymousFuncExp(NewAST):
    def __init__(self):
        self.arg_list = []
        self.expression = None

class Attribute(NewAST):
    def __init__(self, value):
        self.attr = None
        self.value = value

class EnumDef(NewAST):
    def __init__(self, name):
        self.enum_name = name
        self.constants = []
        self.values = []

class StructDef(NewAST):
    def __init__(self, name, mutable):
        self.struct_name = name
        self.mutable = mutable  # structs are immutable by default
        self.variables = []
        self.values = []

class ClassDef(NewAST):
    def __init__(self, class_name):
        self.class_name = class_name
        self.bases = []
        self.body = []

class IfStatement(NewAST):
    def __init__(self, condition):
        self.condition = condition
        self.body = []
        self.orelse = []

class UntilLoop(NewAST):
    def __init__(self, condition):
        self.condition = condition
        self.body = []

class Return(NewAST):
    """
    return statement!
    """
    def __init__(self, value=None):
        self.value = value

class Break(NewAST):
    """
    break statement
    """
    def __init__(self):
        pass

class Continue(NewAST):
    """
    continue statement
    """
    def __init__(self):
        pass

class FromImport(NewAST):
    def __init__(self, module):
        self.module = module
        self.names = []

class Exit(NewAST):
    """
    terminate the whole program with exit call!
    """
    def __init__(self, call_arg=0):
        self.call_arg = call_arg

