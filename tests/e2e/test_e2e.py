import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from codegen.py_generator import generate
from lexer.lexer import tokenize
from parser.parser import parse
from semantic.analyzer import analyze

PROGRAMS = ["hello", "vars_const", "caso", "enquanto_countdown", "peregrine_sum", "laco_cessai", "funcao_soma"]
BASE = Path(__file__).resolve().parents[1] / "programs"


@pytest.mark.parametrize("name", PROGRAMS)
def test_py_match_golden(name: str):
    src = (BASE / f"{name}.holy").read_text(encoding="utf-8")
    toks, errs = tokenize(src)
    assert errs == []
    prog = parse(toks)
    analyze(prog)
    assert generate(prog) == (BASE / f"{name}.expected_py").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", PROGRAMS)
def test_stdout_match_golden(name: str):
    py = (BASE / f"{name}.expected_py").read_text(encoding="utf-8")
    r = subprocess.run([sys.executable, "-c", py], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, r.stderr
    assert r.stdout == (BASE / f"{name}.expected_stdout").read_text(encoding="utf-8")
