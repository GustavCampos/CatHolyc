from dataclasses import dataclass

from .TokenType import TokenType


@dataclass
class Token:
    tipo: TokenType
    lexema: str
    linha: int
    coluna: int


@dataclass
class LexError:
    lexema: str
    linha: int
    coluna: int

    def __str__(self) -> str:
        return (
            f"Erro léxico: símbolo ou lexema inválido '{self.lexema}' "
            f"na linha {self.linha}, coluna {self.coluna}"
        )
