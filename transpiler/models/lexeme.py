from typing import Union
from dataclasses import dataclass
from transpiler.grammar import Grammar

@dataclass
class Lexeme:
    lexeme: Union[str, int, float, None]
    lex_type: Grammar
