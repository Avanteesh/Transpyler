class NewAST:
    def __init__(self,line_no: int):
        self.line_no = line_no

class Module(NewAST):
    def __init__(self, body):
        self.body = body

class Constant(NewAST):
    def __init__(self, value, line_no: int):
        super().__init__(line_no)
        self.value = value

class NamedExp(NewAST):
    def __init__(self, name, line_no: int):
        super().__init__(line_no)
        self.name = name

class Expr(NewAST):
    def __init__(self,value=None, line_no: int=1):
        super().__init__(line_no)
        self.value = value

class BinaryExp(NewAST):
    def __init__(self, op,left=None,right=None, line_no: int=1):
        super().__init__(line_no)
        self.op = op
        self.left = left
        self.right = right

class ComparatorExp(NewAST):
    def __init__(self,op,left=None, line_no: int=1):
        super().__init__(line_no)
        self.op = [op]
        self.left = left
        self.comparator = []

class ArgumentObject(NewAST):
    def __init__(self,arg_name: str, line_no: int):
        super().__init__(line_no)
        self.arg_name = arg_name
        self.__default_value = None 

class FunctionCall(NewAST):
    def __init__(self,function_name: str, line_no: int):
        super().__init__(line_no)
        self.function_name = function_name
        self.arguments = []

class BooleanExp(NewAST):
    def __init__(self, op,left=None,right=None, line_no: int=1):
        super().__init__(line_no)
        self.op = op
        self.left = left
        self.right = right

class UnaryExp(NewAST):
    def __init__(self, op, operand, line_no: int):
        super().__init__(line_no)
        self.op = op
        self.operand = operand

class ListObj(NewAST):
    def __init__(self, line_no: int):
        super().__init__(line_no)
        self.elts = []

class AssignmentExpr(NewAST):
    def __init__(self, line_no: int):
        super().__init__(line_no)
        self.target = []
        self.value = []

class FunctionDef(NewAST):
    def __init__(self, function_name: str, line_no: int):
        super().__init__(line_no)
        self.function_name = function_name
        self.arg_list = []
        self.body = []

class AnonymousFuncExp(NewAST):
    def __init__(self, line_no: int):
        super().__init__(line_no)
        self.arg_list = []
        self.expression = None

class Attribute(NewAST):
    def __init__(self, value, line_no: int):
        super().__init__(line_no)
        self.attr = None
        self.value = value

class Slice(NewAST):
    def __init__(self, line_no: int):
        super().__init__(line_no)
        self.start, self.stop, self.step = None, None, None

class Subscript(NewAST):
    def __init__(self, line_no: int):
        super().__init__(line_no)
        self.variable = variable
        self.indexer = None

class EnumDef(NewAST):
    def __init__(self, name: str, line_no: int):
        super().__init__(line_no)
        self.enum_name = name
        self.constants = []
        self.values = []

class StructDef(NewAST):
    def __init__(self, name: str, mutable: bool, line_no: int):
        super().__init__(line_no)
        self.struct_name = name
        self.mutable = mutable  # structs are immutable by default
        self.variables = []
        self.values = []

class ClassDef(NewAST):
    def __init__(self, class_name: str, line_no: int):
        super().__init__(line_no)
        self.class_name = class_name
        self.bases = []
        self.body = []

class IfStatement(NewAST):
    def __init__(self, condition, line_no: int):
        super().__init__(line_no)
        self.condition = condition
        self.body = []
        self.orelse = []

class UntilLoop(NewAST):
    def __init__(self, condition, line_no: int):
        super().__init__(line_no)
        self.condition = condition
        self.body = []

class Return(NewAST):
    """
    return statement!
    """
    def __init__(self, value=None, line_no: int=1):
        super().__init__(line_no)
        self.value = value

class Break(NewAST):
    """
    break statement
    """
    def __init__(self, line_no: int):
        super().__init__(line_no)

class Continue(NewAST):
    """
    continue statement
    """
    def __init__(self, line_no: int):
        super().__init__(line_no)
        pass

class FromImport(NewAST):
    def __init__(self, module, line_no: int):
        super().__init__(line_no)
        self.module = module
        self.names = []

class Exit(NewAST):
    """
    terminate the whole program with exit call!
    """
    def __init__(self, call_arg=0, line_no: int=1):
        super().__init__(line_no)
        self.call_arg = call_arg

