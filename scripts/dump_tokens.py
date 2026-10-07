import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lexer.lexer import tokenize


def main() -> int:
    if len(sys.argv) != 2:
        print("uso: dump_tokens.py <arquivo.holy>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        src = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Erro de IO: {e}", file=sys.stderr)
        return 2
    tokens, errors = tokenize(src)
    for t in tokens:
        print(f"{t.linha}:{t.coluna} {t.tipo.name} {t.lexema!r}")
    for e in errors:
        print(str(e), file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
