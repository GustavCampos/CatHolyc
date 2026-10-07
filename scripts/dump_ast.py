import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lexer.lexer import tokenize
from parser.parser import ParserError, parse


def node_to_json(o):
    if is_dataclass(o):
        d = {}
        for k, v in asdict(o).items():
            d[k] = node_to_json(v)
        d["_tipo"] = type(o).__name__
        return d
    if isinstance(o, list):
        return [node_to_json(x) for x in o]
    if isinstance(o, tuple):
        return [node_to_json(x) for x in o]
    if isinstance(o, dict):
        return {k: node_to_json(v) for k, v in o.items()}
    return o


def main() -> int:
    if len(sys.argv) != 2:
        print("uso: dump_ast.py <arquivo.holy>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        src = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Erro de IO: {e}", file=sys.stderr)
        return 2
    tokens, lex_errs = tokenize(src)
    for e in lex_errs:
        print(str(e), file=sys.stderr)
    if lex_errs:
        return 1
    try:
        prog = parse(tokens)
    except ParserError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(json.dumps(node_to_json(prog), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
