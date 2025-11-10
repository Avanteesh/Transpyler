from enum import Enum

class Grammar(Enum):
    LEFT_BRACE = 'LEFT_BRACE'
    RIGHT_BRACE = 'RIGHT_BRACE'
    NAME = 'NAME'
    RESERVED_NAME = 'RESERVED_NAME'
    LOGICAL_NOT = 'LOGICAL_NOT'
    LOGICAL_AND = 'LOGICAL_AND'
    LOGICAL_OR = 'LOGICAL_OR'
    NUMERIC_LITERAL = 'NUMERIC_LITERAL'
    STRING_LITERAL = 'STRING_LITERAL'
    ASSIGNMENT_OP = 'ASSIGNMENT'
    L_SHIFT_OP = 'L_SHIFT_OP'
    R_SHIFT_OP = 'R_SHIFT_OP'
    RETURN_OP = 'RETURN_OP'
    BITWISE_OR = 'BITWISE_OR'
    UNARY_FLIP = 'UNARY_FLIP'
    PRODUCT_OP = 'PRODUCT_OP'
    POWER_OP = 'POWER_OP'
    SEMICOLON = 'SEMICOLON'
    PLUS_OP = 'PLUS_OP'
    MINUS_OP = 'MINUS_OP'
    BITWISE_XOR = 'BITWISE_XOR'
    NULL_COAL = 'NULL_COAL'
    DIVISION_OP = 'DIVISION'
    FLOOR_DIV_OP = 'FLOOR_DIV'
    MODULO_OP = 'MODULO_OP'
    COMMA = 'COMMA'
    BITWISE_AND = 'BITWISE_AND'
    GREATER_THAN_OP = 'GREATER_THAN'
    GREATER_OR_EQUAL_OP = 'GREATER_OR_EQUAL'
    LESS_THAN_OP = 'LESS_THAN'
    LESS_OR_EQUAL_OP = 'LESS_OR_EQUAL'
    EQUALITY_OP = 'EQUALITY'
    NOT_EQUAL_OP = 'NOT_EQUAL'
    UNARY_PLUS_OP = 'UNARY_PLUS'
    UNARY_MINUS_OP = 'UNARY_MINUS'
    LINE_END = 'LINE_END'
    LIST_LEFT_BRACE = 'LIST_LEFT_BRACE'
    LIST_RIGHT_BRACE = 'LIST_RIGHT_BRACE'
    DOT = 'DOT'

RESERVED_WORDS = {
  "funcdef","as","do","done","fun",
  "Null","True","False","if","else", "elif",
  "Infinity", "fun","Enum","import","until",
  "break","continue","exit","class","struct",
  "yield","from","mutable"
}

NAMED_OPERATORS = {
    "not": Grammar.LOGICAL_NOT,
    "and": Grammar.LOGICAL_AND,
    "or":Grammar.LOGICAL_OR,
    "xor":Grammar.BITWISE_XOR,
    "mod":Grammar.MODULO_OP
}


