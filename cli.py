#!/usr/bin/env python3
"""CatHolyc CLI (M5, SPEC §9-10).

Pipeline: source .holy → Lexer → Parser → Semantic → CodeGen → .py file / --run.

Usage:
    python cli.py program.holy [-o out.py] [--dump-tokens] [--dump-ast]
                               [--emit-py-only] [--run] [--strict]

Behavior:
- No -o and no --emit-py-only ⇒ sidecar file next to input (program.holy → program.py).
- --emit-py-only ⇒ print generated Python to stdout, write no file.
  Combines with --run (print + run from a temp file).
- --run ⇒ write generated code to a temp .py, execute with the current
  interpreter, inherit stdin (confesse/input() works), forward stdout/stderr.
  Runtime failure propagates the program's exit code.
- --strict ⇒ V1 portability warnings become errors (exit 1).
  Warnings: preceito without init (zero default), partilhado_entre on
  capítulo×capítulo (emits //, floors unlike C truncation for negatives).
- Exit codes: 0 success, 1 lexical/syntactic/semantic (or --strict/runtime)
  error, 2 IO/usage error. All diagnostics go to stderr in Portuguese.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import asdict, is_dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from codegen.py_generator import generate
from lexer.lexer import tokenize
from parser import ast_nodes as A
from parser.parser import ParserError, parse
from semantic.analyzer import SemanticError, analyze

CAP = "capítulo"
VER = "versículo"
SAL = "salmo"
DOG = "dogma"
_LITERAL_MAP = {"int": CAP, "float": VER, "texto": SAL, "bool": DOG}


def node_to_json(o):
    if is_dataclass(o):
        d = {k: node_to_json(v) for k, v in asdict(o).items()}
        d["_tipo"] = type(o).__name__
        return d
    if isinstance(o, (list, tuple)):
        return [node_to_json(x) for x in o]
    if isinstance(o, dict):
        return {k: node_to_json(v) for k, v in o.items()}
    return o


def collect_warnings(prog: A.Programa) -> list[str]:
    """V1 portability notes promoted to errors under --strict."""
    warnings: list[str] = []
    scopes: list[dict] = [{}]

    def lookup(nome: str):
        for scope in reversed(scopes):
            if nome in scope:
                return scope[nome]
        return None

    def tipo_of(expr) -> str | None:
        if isinstance(expr, A.Literal):
            return _LITERAL_MAP.get(expr.tipo, expr.tipo)
        if isinstance(expr, A.Identificador):
            return lookup(expr.nome)
        if isinstance(expr, A.OperacaoUnaria):
            if expr.operador == "não_seja":
                return DOG
            if expr.operador == "privado_de":
                return tipo_of(expr.operando)
            return None
        if isinstance(expr, A.OperacaoBinaria):
            op = expr.operador
            if op in ("somado_a", "privado_de", "multiplicado_por", "partilhado_entre"):
                lt, rt = tipo_of(expr.esquerda), tipo_of(expr.direita)
                if lt == VER or rt == VER:
                    return VER
                if lt == CAP and rt == CAP:
                    return CAP
                return None
            if op == "dízimo_de":
                return CAP
            if op in (
                "exaltado_sobre", "submisso_a", "não_abaixo_de", "não_acima_de",
                "conforme_a", "dissonante_de", "em_comunhão_com", "ou_porventura",
            ):
                return DOG
            return None
        return None

    def check_expr(expr) -> None:
        if isinstance(expr, A.OperacaoBinaria) and expr.operador == "partilhado_entre":
            if tipo_of(expr.esquerda) == CAP and tipo_of(expr.direita) == CAP:
                warnings.append(
                    f"Aviso: linha {expr.linha} — 'partilhado_entre' entre "
                    f"capítulo emite '//' (divisão inteira; difere de C para "
                    f"operandos negativos)"
                )
        for child in getattr(expr, "__dict__", {}).values():
            walk_expr(child)

    def walk_expr(o) -> None:
        if isinstance(o, (A.OperacaoBinaria, A.OperacaoUnaria)):
            check_expr(o)  # checks node, then recurses into children itself
        elif isinstance(o, (list, tuple)):
            for x in o:
                walk_expr(x)

    def walk_cmds(cmds: list) -> None:
        for cmd in cmds:
            if isinstance(cmd, A.DeclConst):
                scopes[-1][cmd.nome] = {"tipo": _LITERAL_MAP.get(cmd.tipo, cmd.tipo)}
                walk_expr(cmd.valor)
            elif isinstance(cmd, A.DeclVar):
                scopes[-1][cmd.nome] = {"tipo": _LITERAL_MAP.get(cmd.tipo, cmd.tipo)}
                if cmd.valor is None:
                    warnings.append(
                        f"Aviso: linha {cmd.linha} — preceito '{cmd.nome}' sem "
                        f"inicialização usa valor zero padrão"
                    )
                else:
                    walk_expr(cmd.valor)
            elif isinstance(cmd, A.Atribuicao):
                walk_expr(cmd.valor)
            elif isinstance(cmd, A.Se):
                walk_expr(cmd.condicao)
                scopes.append({})
                walk_cmds(cmd.entao)
                scopes.pop()
                for ramo in cmd.senaoSe:
                    walk_expr(ramo.condicao)
                    scopes.append({})
                    walk_cmds(ramo.bloco)
                    scopes.pop()
                if cmd.senao is not None:
                    scopes.append({})
                    walk_cmds(cmd.senao)
                    scopes.pop()
            elif isinstance(cmd, A.Enquanto):
                walk_expr(cmd.condicao)
                scopes.append({})
                walk_cmds(cmd.corpo)
                scopes.pop()
            elif isinstance(cmd, A.Para):
                walk_expr(cmd.init.valor)
                walk_expr(cmd.condicao)
                walk_expr(cmd.incremento.valor)
                scopes.append({})
                walk_cmds(cmd.corpo)
                scopes.pop()
            elif isinstance(cmd, A.ParaCada):
                scopes.append({})
                scopes[-1][cmd.variavel] = {"tipo": SAL}
                walk_cmds(cmd.corpo)
                scopes.pop()
            elif isinstance(cmd, A.Saida):
                walk_expr(cmd.expressao)
            # Entrada has no expression to walk

    walk_cmds(prog.comandos)
    return warnings


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cli.py",
        description="Compila CatHolyc (.holy) para Python e opcionalmente executa.",
    )
    p.add_argument("fonte", help="arquivo fonte .holy")
    p.add_argument("-o", "--output", default=None, help="arquivo .py de saída "
                   "(padrão: mesmo nome do fonte com extensão .py)")
    p.add_argument("--dump-tokens", action="store_true",
                   help="imprime tokens (linha:col TIPO 'lexema') e continua")
    p.add_argument("--dump-ast", action="store_true",
                   help="imprime AST em JSON e continua")
    p.add_argument("--emit-py-only", action="store_true",
                   help="imprime Python gerado no stdout, não grava arquivo")
    p.add_argument("--run", action="store_true",
                   help="executa o Python gerado (stdin herdado, stdout repassado)")
    p.add_argument("--strict", action="store_true",
                   help="avisos de portabilidade V1 viram erros (saída 1)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    src_path = Path(args.fonte)

    try:
        source = src_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Erro de IO: não foi possível ler '{src_path}': {e}", file=sys.stderr)
        return 2

    tokens, lex_errs = tokenize(source)
    if args.dump_tokens:
        for t in tokens:
            print(f"{t.linha}:{t.coluna} {t.tipo.name} {t.lexema!r}")
    if lex_errs:
        for e in lex_errs:
            print(str(e), file=sys.stderr)
        return 1

    try:
        prog = parse(tokens)
    except ParserError as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.dump_ast:
        print(json.dumps(node_to_json(prog), ensure_ascii=False, indent=2))

    try:
        analyze(prog)
    except SemanticError as e:
        print(str(e), file=sys.stderr)
        return 1

    warnings = collect_warnings(prog)
    for w in warnings:
        print(w, file=sys.stderr)
    if args.strict and warnings:
        print("Erro: modo --strict trata avisos como erros", file=sys.stderr)
        return 1

    py_code = generate(prog)

    if args.emit_py_only:
        sys.stdout.write(py_code)
    else:
        out_path = Path(args.output) if args.output else src_path.with_suffix(".py")
        try:
            out_path.write_text(py_code, encoding="utf-8")
        except OSError as e:
            print(f"Erro de IO: não foi possível escrever '{out_path}': {e}",
                  file=sys.stderr)
            return 2

    if args.run:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                         encoding="utf-8") as tmp:
            tmp.write(py_code)
            tmp_path = tmp.name
        try:
            r = subprocess.run([sys.executable, tmp_path], stdin=None,
                               capture_output=True, text=True)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        if r.stdout:
            sys.stdout.write(r.stdout)
        if r.stderr:
            sys.stderr.write(r.stderr)
        if r.returncode != 0:
            print(f"Erro de execução: programa retornou código {r.returncode}",
                  file=sys.stderr)
            return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
