"""CatHolyc → Python generator (M4, SPEC §8).

Decisions (SPEC §13 resolved here, kept consistent):
- ``partilhado_entre`` emits ``//`` when both operands are statically
  ``capítulo`` (int), else ``/``. Rationale: Python ``/`` always yields
  float, so plain ``/`` would change int-division intent; ``//`` preserves
  it for positives (note: ``//`` floors, C truncates — differs only for
  negative operands; E2E avoids those; documented V1 limitation).
- ``mandamento`` (const) names emit UPPER_CASE; references resolve via a
  scope-aware env that mirrors ``semantic/analyzer.py`` push/pop, so
  shadowing still binds correctly. Semantic const enforcement happens in
  M3; here the distinction is erased to plain assignment.
- ``peregrine`` desugars to ``while``: emit init, then
  ``while cond:`` + body + incremento (last in loop).
- ``confesse x`` emits ``int(input())`` / ``float(input())`` /
  ``input()`` / membership-test for ``dogma`` (verdade/true/1/sim).
- Uninitialized ``preceito`` gets a zero default (0 / 0.0 / "" / False);
  Python needs a binding and Holy leaves it undefined (V1).
- Header emits ``# em_nome_do_pai``; ``amém``/``amém_senhor`` only affect
  newlines/indent, emit nothing.
"""

import json

from parser import ast_nodes as A

CAP = "capítulo"
VER = "versículo"
SAL = "salmo"
DOG = "dogma"

_LITERAL_MAP = {"int": CAP, "float": VER, "texto": SAL, "bool": DOG}

_BIN_OP = {
    "somado_a": "+",
    "privado_de": "-",
    "multiplicado_por": "*",
    "dízimo_de": "%",
    "exaltado_sobre": ">",
    "submisso_a": "<",
    "não_abaixo_de": ">=",
    "não_acima_de": "<=",
    "conforme_a": "==",
    "dissonante_de": "!=",
    "em_comunhão_com": "and",
    "ou_porventura": "or",
}

# precedence: higher binds tighter (mirrors Python for our operator subset)
_PREC = {
    "ou_porventura": 1,
    "em_comunhão_com": 2,
    "não_seja": 3,
    "exaltado_sobre": 4,
    "submisso_a": 4,
    "não_abaixo_de": 4,
    "não_acima_de": 4,
    "conforme_a": 4,
    "dissonante_de": 4,
    "somado_a": 5,
    "privado_de": 5,
    "multiplicado_por": 6,
    "partilhado_entre": 6,
    "dízimo_de": 6,
}
_UNARY_MINUS_PREC = 7


def _norm_tipo(t: str) -> str:
    return _LITERAL_MAP.get(t, t)


_ZERO_DEFAULT = {CAP: "0", VER: "0.0", SAL: '""', DOG: "False"}


class _Gen:
    def __init__(self, include_line_comments: bool = False) -> None:
        self.lines: list[str] = []
        self.indent = 0
        # scopes mirror analyzer: list of {holy_name: {"tipo", "py"}}
        self.scopes: list[dict] = []
        self.include_lines = include_line_comments

    # -- scope env (mirrors semantic/analyzer.py) --
    def push(self) -> None:
        self.scopes.append({})

    def pop(self) -> None:
        self.scopes.pop()

    def lookup(self, nome: str) -> dict | None:
        for scope in reversed(self.scopes):
            if nome in scope:
                return scope[nome]
        return None

    def _fresh(self, base: str) -> str:
        taken_py = {e["py"] for s in self.scopes for e in s.values()}
        cand = base
        i = 1
        while cand in taken_py:
            cand = f"{base}__{i}"
            i += 1
        return cand

    def declare(self, nome: str, tipo: str, const: bool) -> str:
        base = nome.upper() if const else nome
        # shadow-safe: if visible in outer scope, freshen (Python has no block scope)
        if any(nome in s for s in self.scopes[:-1]):
            py = self._fresh(base)
        elif base in {e["py"] for s in self.scopes for e in s.values()}:
            # avoid clobbering an unrelated identical py name
            py = self._fresh(base)
        else:
            py = base
        self.scopes[-1][nome] = {"tipo": _norm_tipo(tipo), "py": py}
        return py

    def py_name(self, nome: str) -> str:
        e = self.lookup(nome)
        return e["py"] if e else nome

    # -- static type inference (for // decision; mirrors analyzer._tipo) --
    def tipo_of(self, expr: object) -> str | None:
        if isinstance(expr, A.Literal):
            return _norm_tipo(expr.tipo)
        if isinstance(expr, A.Identificador):
            e = self.lookup(expr.nome)
            return e["tipo"] if e else None
        if isinstance(expr, A.Chamada):
            e = self.lookup(expr.nome)
            return e["tipo"] if e else None
        if isinstance(expr, A.OperacaoUnaria):
            if expr.operador == "não_seja":
                return DOG
            if expr.operador == "privado_de":
                return self.tipo_of(expr.operando)
            return None
        if isinstance(expr, A.OperacaoBinaria):
            op = expr.operador
            if op in ("somado_a", "privado_de", "multiplicado_por", "partilhado_entre"):
                lt, rt = self.tipo_of(expr.esquerda), self.tipo_of(expr.direita)
                if lt == VER or rt == VER:
                    return VER
                if lt == CAP and rt == CAP:
                    return CAP
                return None
            if op == "dízimo_de":
                return CAP
            if op in (
                "exaltado_sobre",
                "submisso_a",
                "não_abaixo_de",
                "não_acima_de",
                "conforme_a",
                "dissonante_de",
                "em_comunhão_com",
                "ou_porventura",
            ):
                return DOG
            return None
        return None

    # -- emit helpers --
    def emit(self, s: str) -> None:
        self.lines.append("    " * self.indent + s)

    def tag(self, linha: int) -> str:
        return f"  # linha {linha}" if self.include_lines else ""

    # -- program / commands --
    def gen_programa(self, prog: A.Programa) -> str:
        self.emit("# em_nome_do_pai")
        self.push()  # global scope = program body (mirrors analyzer)
        for cmd in prog.comandos:
            self.gen_cmd(cmd)
        self.pop()
        return "\n".join(self.lines) + "\n"

    def gen_cmd(self, node: object) -> None:
        if isinstance(node, A.DeclConst):
            py = self.declare(node.nome, node.tipo, const=True)
            self.emit(f"{py} = {self.gen_expr(node.valor)}{self.tag(node.linha)}")
        elif isinstance(node, A.DeclVar):
            py = self.declare(node.nome, node.tipo, const=False)
            if node.valor is None:
                self.emit(f"{py} = {_ZERO_DEFAULT[_norm_tipo(node.tipo)]}{self.tag(node.linha)}")
            else:
                self.emit(f"{py} = {self.gen_expr(node.valor)}{self.tag(node.linha)}")
        elif isinstance(node, A.Atribuicao):
            self.emit(f"{self.py_name(node.nome)} = {self.gen_expr(node.valor)}{self.tag(node.linha)}")
        elif isinstance(node, A.Se):
            self.emit(f"if {self.gen_expr(node.condicao)}:{self.tag(node.linha)}")
            self.gen_bloco(node.entao)
            for ramo in node.senaoSe:
                self.emit(f"elif {self.gen_expr(ramo.condicao)}:{self.tag(ramo.linha)}")
                self.gen_bloco(ramo.bloco)
            if node.senao is not None:
                self.emit(f"else:{self.tag(node.linha)}")
                self.gen_bloco(node.senao)
        elif isinstance(node, A.Enquanto):
            self.emit(f"while {self.gen_expr(node.condicao)}:{self.tag(node.linha)}")
            self.gen_bloco(node.corpo)
        elif isinstance(node, A.Para):
            # desugar C-style to while (SPEC §8)
            init = node.init
            incr = node.incremento
            self.emit(f"{self.py_name(init.nome)} = {self.gen_expr(init.valor)}{self.tag(init.linha)}")
            self.emit(f"while {self.gen_expr(node.condicao)}:{self.tag(node.linha)}")
            self.indent += 1
            self.push()
            try:
                for c in node.corpo:
                    self.gen_cmd(c)
                self.emit(f"{self.py_name(incr.nome)} = {self.gen_expr(incr.valor)}{self.tag(incr.linha)}")
            finally:
                self.pop()
                self.indent -= 1
        elif isinstance(node, A.ParaCada):
            col = self.py_name(node.colecao)
            self.push()
            # loop var is fresh (V1 iterates salmo → str chars)
            base = node.variavel
            py_v = base
            if self.lookup(base) is not None or any(
                py_v == e["py"] for s in self.scopes for e in s.values()
            ):
                py_v = self._fresh(base)
            self.scopes[-1][node.variavel] = {"tipo": SAL, "py": py_v}
            self.emit(f"for {py_v} in {col}:{self.tag(node.linha)}")
            self.indent += 1
            try:
                if not node.corpo:
                    self.emit("pass")
                for c in node.corpo:
                    self.gen_cmd(c)
            finally:
                self.indent -= 1
                self.pop()
        elif isinstance(node, A.Saida):
            self.emit(f"print({self.gen_expr(node.expressao)}){self.tag(node.linha)}")
        elif isinstance(node, A.Cessai):
            self.emit(f"break{self.tag(node.linha)}")
        elif isinstance(node, A.Perseverai):
            self.emit(f"continue{self.tag(node.linha)}")
        elif isinstance(node, A.DefFuncao):
            # nome como escrito (sem UPPER); params posicionais
            py_f = self.declare(node.nome, node.tipo, const=False)
            py_params = []
            self.push()
            for p in node.params:
                py_params.append(self.declare(p.nome, p.tipo, const=False))
            self.emit(f"def {py_f}({', '.join(py_params)}):{self.tag(node.linha)}")
            self.indent += 1
            try:
                if not node.corpo:
                    self.emit("pass")
                for c in node.corpo:
                    self.gen_cmd(c)
            finally:
                self.indent -= 1
                self.pop()
        elif isinstance(node, A.Retorne):
            if node.valor is None:
                self.emit(f"return{self.tag(node.linha)}")
            else:
                self.emit(f"return {self.gen_expr(node.valor)}{self.tag(node.linha)}")
        elif isinstance(node, A.Entrada):
            e = self.lookup(node.variavel)
            py = e["py"] if e else node.variavel
            t = e["tipo"] if e else None
            if t == CAP:
                rhs = "int(input())"
            elif t == VER:
                rhs = "float(input())"
            elif t == DOG:
                rhs = 'input().strip().lower() in ("verdade", "true", "1", "sim")'
            else:
                rhs = "input()"
            self.emit(f"{py} = {rhs}{self.tag(node.linha)}")
        else:
            raise ValueError(f"nó desconhecido {type(node).__name__}")

    def gen_bloco(self, cmds: list) -> None:
        self.indent += 1
        self.push()
        try:
            if not cmds:
                self.emit("pass")
            for c in cmds:
                self.gen_cmd(c)
        finally:
            self.pop()
            self.indent -= 1

    # -- expressions (precedence-aware, minimal parens) --
    def gen_expr(self, expr: object, parent_prec: int = 0) -> str:
        if isinstance(expr, A.Literal):
            if expr.tipo in ("int", CAP):
                return str(expr.valor)
            if expr.tipo in ("float", VER):
                return repr(float(expr.valor))
            if expr.tipo in ("texto", SAL):
                return json.dumps(expr.valor, ensure_ascii=False)
            if expr.tipo in ("bool", DOG):
                return "True" if expr.valor else "False"
            raise ValueError(f"literal desconhecido {expr.tipo}")
        if isinstance(expr, A.Identificador):
            return self.py_name(expr.nome)
        if isinstance(expr, A.Chamada):
            args = ", ".join(self.gen_expr(a) for a in expr.args)
            return f"{self.py_name(expr.nome)}({args})"
        if isinstance(expr, A.OperacaoUnaria):
            if expr.operador == "não_seja":
                inner = self.gen_expr(expr.operando, _PREC["não_seja"])
                s = f"not {inner}"
                return f"({s})" if _PREC["não_seja"] < parent_prec else s
            if expr.operador == "privado_de":
                inner = self.gen_expr(expr.operando, _UNARY_MINUS_PREC)
                s = f"-{inner}"
                return f"({s})" if _UNARY_MINUS_PREC < parent_prec else s
            raise ValueError(f"operador unário desconhecido '{expr.operador}'")
        if isinstance(expr, A.OperacaoBinaria):
            op = expr.operador
            if op == "partilhado_entre":
                lt, rt = self.tipo_of(expr.esquerda), self.tipo_of(expr.direita)
                pyop = "//" if (lt == CAP and rt == CAP) else "/"
            else:
                try:
                    pyop = _BIN_OP[op]
                except KeyError:
                    raise ValueError(f"operador desconhecido '{op}'")
            prec = _PREC[op]
            l = self.gen_expr(expr.esquerda, prec)
            r = self.gen_expr(expr.direita, prec + 1)  # left-assoc
            s = f"{l} {pyop} {r}"
            return f"({s})" if prec < parent_prec else s
        raise ValueError(f"expressão desconhecida {type(expr).__name__}")


def generate(programa: A.Programa, include_line_comments: bool = False) -> str:
    """Emit readable Python3 for a (semantic-checked) Programa."""
    return _Gen(include_line_comments).gen_programa(programa)
