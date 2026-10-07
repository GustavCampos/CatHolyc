from parser import ast_nodes as A
from semantic.symbols import Symbol, SymbolTable

CAP = "capítulo"
VER = "versículo"
SAL = "salmo"
DOG = "dogma"
NUMERICOS = {CAP, VER}

_ARIT = {"somado_a", "privado_de", "multiplicado_por", "partilhado_entre"}
_REL_NUM = {"exaltado_sobre", "submisso_a", "não_abaixo_de", "não_acima_de"}
_REL_EQ = {"conforme_a", "dissonante_de"}
_LOGIC = {"em_comunhão_com", "ou_porventura"}

_LITERAL_MAP = {"int": CAP, "float": VER, "texto": SAL, "bool": DOG}


class SemanticError(Exception):
    pass


def _err(linha: int, msg: str) -> SemanticError:
    return SemanticError(f"Erro semântico: linha {linha} — {msg}")


def _norm_tipo(t: str) -> str:
    return _LITERAL_MAP.get(t, t)


def _compativel(dest: str, src: str) -> bool:
    if dest == src:
        return True
    # int → float promote
    return dest == VER and src == CAP


class Analyzer:
    def __init__(self) -> None:
        self.tabela = SymbolTable()

    def analyze(self, prog: A.Programa) -> SymbolTable:
        self.tabela.push()  # global scope = program body
        for cmd in prog.comandos:
            self._cmd(cmd)
        return self.tabela

    # ---- commands ----

    def _cmd(self, node: object) -> None:
        if isinstance(node, A.DeclConst):
            self._decl_const(node)
        elif isinstance(node, A.DeclVar):
            self._decl_var(node)
        elif isinstance(node, A.Atribuicao):
            self._atrib(node.nome, node.valor, node.linha)
        elif isinstance(node, A.Se):
            self._se(node)
        elif isinstance(node, A.Enquanto):
            t = self._tipo(node.condicao)
            if t != DOG:
                raise _err(node.linha, f"ESEM condição deve ser do tipo dogma, encontrado {t}")
            self._bloco(node.corpo)
        elif isinstance(node, A.Para):
            # init/incremento referem-se a variável já declarada (Atribuicao)
            self._atrib(node.init.nome, node.init.valor, node.init.linha)
            t = self._tipo(node.condicao)
            if t != DOG:
                raise _err(node.linha, f"ESEM condição deve ser do tipo dogma, encontrado {t}")
            self._atrib(node.incremento.nome, node.incremento.valor, node.incremento.linha)
            self._bloco(node.corpo)
        elif isinstance(node, A.ParaCada):
            col = self.tabela.lookup(node.colecao)
            if col is None:
                raise _err(node.linha, f"ESEM identificador desconhecido '{node.colecao}'")
            if col.tipo != SAL:
                raise _err(
                    node.linha,
                    f"ESEM em_cada suporta apenas salmo em V1, encontrado {col.tipo}",
                )
            self.tabela.push()
            try:
                self.tabela.declare(Symbol(node.variavel, SAL, False, node.linha))
            except ValueError:
                raise _err(node.linha, f"ESEM redeclaração de '{node.variavel}'")
            try:
                for c in node.corpo:
                    self._cmd(c)
            finally:
                self.tabela.pop()
        elif isinstance(node, A.Saida):
            self._tipo(node.expressao)  # qualquer tipo
        elif isinstance(node, A.Entrada):
            sym = self.tabela.lookup(node.variavel)
            if sym is None:
                raise _err(node.linha, f"ESEM identificador desconhecido '{node.variavel}'")
            if sym.const:
                raise _err(node.linha, f"ESEM atribuição a constante '{node.variavel}'")
        else:
            raise _err(getattr(node, "linha", 0), f"ESEM nó desconhecido {type(node).__name__}")

    def _bloco(self, cmds: list) -> None:
        self.tabela.push()
        try:
            for c in cmds:
                self._cmd(c)
        finally:
            self.tabela.pop()

    def _decl_const(self, node: A.DeclConst) -> None:
        if node.nome in self.tabela.current():
            raise _err(node.linha, f"ESEM redeclaração de '{node.nome}'")
        if node.valor is None:
            raise _err(node.linha, f"ESEM const sem inicialização: '{node.nome}'")
        dest = _norm_tipo(node.tipo)
        src = self._tipo(node.valor)
        if not _compativel(dest, src):
            raise _err(
                node.linha,
                f"ESEM tipos incompatíveis: não é possível atribuir {src} a {dest} ('{node.nome}')",
            )
        self.tabela.declare(Symbol(node.nome, dest, True, node.linha))

    def _decl_var(self, node: A.DeclVar) -> None:
        if node.nome in self.tabela.current():
            raise _err(node.linha, f"ESEM redeclaração de '{node.nome}'")
        dest = _norm_tipo(node.tipo)
        if node.valor is not None:
            src = self._tipo(node.valor)
            if not _compativel(dest, src):
                raise _err(
                    node.linha,
                    f"ESEM tipos incompatíveis: não é possível atribuir {src} a {dest} ('{node.nome}')",
                )
        self.tabela.declare(Symbol(node.nome, dest, False, node.linha))

    def _atrib(self, nome: str, valor: object, linha: int) -> None:
        sym = self.tabela.lookup(nome)
        if sym is None:
            raise _err(linha, f"ESEM identificador desconhecido '{nome}'")
        if sym.const:
            raise _err(linha, f"ESEM atribuição a constante '{nome}'")
        src = self._tipo(valor)
        if not _compativel(sym.tipo, src):
            raise _err(
                linha,
                f"ESEM tipos incompatíveis: não é possível atribuir {src} a {sym.tipo} ('{nome}')",
            )

    def _se(self, node: A.Se) -> None:
        t = self._tipo(node.condicao)
        if t != DOG:
            raise _err(node.linha, f"ESEM condição deve ser do tipo dogma, encontrado {t}")
        self._bloco(node.entao)
        for ramo in node.senaoSe:
            tr = self._tipo(ramo.condicao)
            if tr != DOG:
                raise _err(ramo.linha, f"ESEM condição deve ser do tipo dogma, encontrado {tr}")
            self._bloco(ramo.bloco)
        if node.senao is not None:
            self._bloco(node.senao)

    # ---- expressions → canonical type ----

    def _tipo(self, expr: object) -> str:
        if isinstance(expr, A.Literal):
            return _LITERAL_MAP[expr.tipo]
        if isinstance(expr, A.Identificador):
            sym = self.tabela.lookup(expr.nome)
            if sym is None:
                raise _err(expr.linha, f"ESEM identificador desconhecido '{expr.nome}'")
            return sym.tipo
        if isinstance(expr, A.OperacaoUnaria):
            if expr.operador == "não_seja":
                t = self._tipo(expr.operando)
                if t != DOG:
                    raise _err(
                        expr.linha,
                        f"ESEM operador lógico 'não_seja' exige operando do tipo dogma, encontrado {t}",
                    )
                return DOG
            if expr.operador == "privado_de":  # menos unário
                t = self._tipo(expr.operando)
                if t not in NUMERICOS:
                    raise _err(
                        expr.linha,
                        f"ESEM operação aritmética 'privado_de' exige operando numérico (capítulo/versículo), encontrado {t}",
                    )
                return t
            raise _err(expr.linha, f"ESEM operador unário desconhecido '{expr.operador}'")
        if isinstance(expr, A.OperacaoBinaria):
            op = expr.operador
            lt = self._tipo(expr.esquerda)
            rt = self._tipo(expr.direita)
            if op in _ARIT:
                if lt not in NUMERICOS or rt not in NUMERICOS:
                    raise _err(
                        expr.linha,
                        f"ESEM operação aritmética '{op}' exige operandos numéricos (capítulo/versículo), encontrado {lt} e {rt}",
                    )
                return VER if VER in (lt, rt) else CAP
            if op == "dízimo_de":
                if lt != CAP or rt != CAP:
                    raise _err(
                        expr.linha,
                        f"ESEM 'dízimo_de' exige operandos do tipo capítulo (int), encontrado {lt} e {rt}",
                    )
                return CAP
            if op in _REL_NUM:
                if lt not in NUMERICOS or rt not in NUMERICOS:
                    raise _err(
                        expr.linha,
                        f"ESEM operador relacional '{op}' exige operandos numéricos, encontrado {lt} e {rt}",
                    )
                return DOG
            if op in _REL_EQ:
                if lt in NUMERICOS and rt in NUMERICOS:
                    return DOG
                if lt == rt:
                    return DOG
                raise _err(
                    expr.linha,
                    f"ESEM operador '{op}' exige operandos de mesmo tipo, encontrado {lt} e {rt}",
                )
            if op in _LOGIC:
                if lt != DOG or rt != DOG:
                    raise _err(
                        expr.linha,
                        f"ESEM operador lógico '{op}' exige operandos do tipo dogma, encontrado {lt} e {rt}",
                    )
                return DOG
            raise _err(expr.linha, f"ESEM operador desconhecido '{op}'")
        raise _err(getattr(expr, "linha", 0), "ESEM expressão desconhecida")


def analyze(prog: A.Programa) -> SymbolTable:
    return Analyzer().analyze(prog)
