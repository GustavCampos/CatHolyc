import subprocess
import sys
from pathlib import Path

import pytest

CLI = Path(__file__).resolve().parents[2] / "cli.py"
PROGRAMS_DIR = Path(__file__).resolve().parents[1] / "programs"
GOLDENS = ["hello", "vars_const", "caso", "enquanto_countdown", "peregrine_sum", "laco_cessai", "funcao_soma"]


def run_cli(*argv: str, cwd: Path | None = None):
    return subprocess.run([sys.executable, str(CLI), *argv],
                          capture_output=True, text=True, cwd=cwd, timeout=30)


@pytest.mark.parametrize("name", GOLDENS)
def test_emit_py_only_matches_golden(name: str):
    r = run_cli(str(PROGRAMS_DIR / f"{name}.holy"), "--emit-py-only")
    assert r.returncode == 0, r.stderr
    expected = (PROGRAMS_DIR / f"{name}.expected_py").read_text(encoding="utf-8")
    assert r.stdout == expected


@pytest.mark.parametrize("name", GOLDENS)
def test_run_stdout_matches_golden(name: str, tmp_path: Path):
    r = run_cli(str(PROGRAMS_DIR / f"{name}.holy"), "--run",
                "-o", str(tmp_path / f"{name}.py"))
    assert r.returncode == 0, r.stderr
    expected = (PROGRAMS_DIR / f"{name}.expected_stdout").read_text(encoding="utf-8")
    assert r.stdout == expected


def test_sidecar_default(tmp_path: Path):
    src = tmp_path / "prog.holy"
    src.write_text("em_nome_do_pai\nproclame \"oi\" amém\n"
                   "assim_seja_em_seu_nome_amem\n", encoding="utf-8")
    r = run_cli(str(src))
    assert r.returncode == 0, r.stderr
    out = tmp_path / "prog.py"
    assert out.exists()
    assert "print" in out.read_text(encoding="utf-8")


def test_output_flag(tmp_path: Path):
    src = tmp_path / "prog.holy"
    src.write_text("em_nome_do_pai\nproclame \"oi\" amém\n"
                   "assim_seja_em_seu_nome_amem\n", encoding="utf-8")
    out = tmp_path / "custom.py"
    r = run_cli(str(src), "-o", str(out))
    assert r.returncode == 0, r.stderr
    assert out.exists()


def test_dump_tokens(tmp_path: Path):
    r = run_cli(str(PROGRAMS_DIR / "hello.holy"), "--dump-tokens",
                "--emit-py-only", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "proclame" in r.stdout


def test_dump_ast(tmp_path: Path):
    r = run_cli(str(PROGRAMS_DIR / "hello.holy"), "--dump-ast",
                "--emit-py-only", cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert '"_tipo": "Programa"' in r.stdout


def test_lex_error_exit_1(tmp_path: Path):
    src = tmp_path / "bad.holy"
    src.write_text("em_nome_do_pai\n#ops\nassim_seja_em_seu_nome_amem\n",
                   encoding="utf-8")
    r = run_cli(str(src), "--emit-py-only")
    assert r.returncode == 1
    assert "Erro léxico" in r.stderr


def test_syntax_error_exit_1(tmp_path: Path):
    src = tmp_path / "bad.holy"
    src.write_text("em_nome_do_pai\npreceito capítulo $x 1 amém\n"
                   "assim_seja_em_seu_nome_amem\n", encoding="utf-8")
    r = run_cli(str(src), "--emit-py-only")
    assert r.returncode == 1
    assert "Erro sintático" in r.stderr


def test_semantic_error_exit_1(tmp_path: Path):
    src = tmp_path / "bad.holy"
    src.write_text("em_nome_do_pai\nproclame $ndef amém\n"
                   "assim_seja_em_seu_nome_amem\n", encoding="utf-8")
    r = run_cli(str(src), "--emit-py-only")
    assert r.returncode == 1
    assert "Erro semântico" in r.stderr


def test_missing_file_exit_2(tmp_path: Path):
    r = run_cli(str(tmp_path / "nao_existe.holy"), "--emit-py-only")
    assert r.returncode == 2


def test_strict_rejects_uninitialized(tmp_path: Path):
    src = tmp_path / "w.holy"
    src.write_text("em_nome_do_pai\npreceito capítulo $x amém\n"
                   "proclame $x amém\nassim_seja_em_seu_nome_amem\n",
                   encoding="utf-8")
    ok = run_cli(str(src), "--emit-py-only")
    assert ok.returncode == 0, ok.stderr
    assert "Aviso" in ok.stderr
    strict = run_cli(str(src), "--emit-py-only", "--strict")
    assert strict.returncode == 1
    assert "strict" in strict.stderr.lower() or "Aviso" in strict.stderr


def test_strict_passes_on_clean_goldens(tmp_path: Path):
    for name in GOLDENS:
        r = run_cli(str(PROGRAMS_DIR / f"{name}.holy"), "--emit-py-only",
                    "--strict", cwd=tmp_path)
        assert r.returncode == 0, (name, r.stderr)
