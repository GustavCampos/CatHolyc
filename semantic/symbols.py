from dataclasses import dataclass, field


@dataclass
class Symbol:
    nome: str
    tipo: str  # canonical: capítulo | versículo | salmo | dogma
    const: bool
    linha: int


class SymbolTable:
    """Stacked scopes. scopes[0] = global. declare = current scope only."""

    def __init__(self) -> None:
        self.scopes: list[dict[str, Symbol]] = []

    def push(self) -> None:
        self.scopes.append({})

    def pop(self) -> None:
        self.scopes.pop()

    @property
    def depth(self) -> int:
        return len(self.scopes)

    def current(self) -> dict[str, Symbol]:
        return self.scopes[-1]

    def declare(self, sym: Symbol) -> None:
        """Insert into current scope. Raises ValueError if redeclared."""
        if sym.nome in self.scopes[-1]:
            raise ValueError(f"redeclaração de '{sym.nome}'")
        self.scopes[-1][sym.nome] = sym

    def lookup(self, nome: str) -> Symbol | None:
        for scope in reversed(self.scopes):
            if nome in scope:
                return scope[nome]
        return None

    def depth_of(self, nome: str) -> int | None:
        """Índice do escopo que declara `nome` (0 = global); None se ausente."""
        for i in range(len(self.scopes) - 1, -1, -1):
            if nome in self.scopes[i]:
                return i
        return None
