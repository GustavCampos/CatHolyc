import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from codegen.py_generator import generate
from lexer.lexer import tokenize
from parser.parser import parse
from semantic.analyzer import analyze


def gen(src: str) -> str:
    toks, errs = tokenize(src)
    assert errs == []
    prog = parse(toks)
    analyze(prog)
    return generate(prog)


def P(body: str) -> str:
    return f"em_nome_do_pai {body} assim_seja_em_seu_nome_amem"


def test_precedence_sem_parens():
    out = gen(P("preceito capítulo $x seja 2 somado_a 3 multiplicado_por 4 amém"))
    assert "x = 2 + 3 * 4" in out


def test_parens_preservados():
    out = gen(P("preceito capítulo $x seja ( 2 somado_a 3 ) multiplicado_por 4 amém"))
    assert "x = (2 + 3) * 4" in out


def test_operadores_completos():
    out = gen(
        P(
            "preceito capítulo $a seja 7 amém "
            "preceito capítulo $b seja 2 amém "
            "proclame $a privado_de $b amém "
            "proclame $a multiplicado_por $b amém "
            "proclame $a dízimo_de $b amém "
        )
    )
    assert "a - b" in out and "a * b" in out and "a % b" in out


def test_divisao_int_usa_floor():
    out = gen(
        P("preceito capítulo $a seja 7 amém preceito capítulo $b seja 2 amém proclame $a partilhado_entre $b amém")
    )
    assert "a // b" in out


def test_divisao_float_usa_barra():
    out = gen(
        P("preceito versículo $a seja 7.0 amém preceito capítulo $b seja 2 amém proclame $a partilhado_entre $b amém")
    )
    assert "a / b" in out and "//" not in out


def test_relacionais_e_logicos():
    out = gen(
        P(
            "preceito capítulo $a seja 1 amém preceito capítulo $b seja 2 amém "
            "caso $a submisso_a $b em_comunhão_com não_seja $a conforme_a $b proclame 1 amém amém_senhor"
        )
    )
    assert "while" not in out
    assert "if a < b and not a == b:" in out


def test_relacionais_tabela():
    out = gen(
        P(
            "preceito capítulo $a seja 1 amém "
            "caso $a exaltado_sobre 0 proclame 1 amém amém_senhor "
            "caso $a não_abaixo_de 1 proclame 1 amém amém_senhor "
            "caso $a não_acima_de 1 proclame 1 amém amém_senhor "
            "caso $a dissonante_de 2 proclame 1 amém amém_senhor"
        )
    )
    assert "a > 0" in out and "a >= 1" in out and "a <= 1" in out and "a != 2" in out


def test_ou_e_unario_menos():
    out = gen(
        P(
            "preceito dogma $a seja verdade amém preceito dogma $b seja falsidade amém "
            "caso $a ou_porventura $b proclame 1 amém amém_senhor "
            "preceito capítulo $n seja privado_de 5 amém"
        )
    )
    assert "if a or b:" in out
    assert "n = -5" in out
    assert "True" in out and "False" in out


def test_const_upper_e_referencia():
    out = gen(P("mandamento capítulo $c seja 1 amém proclame $c amém"))
    assert "C = 1" in out and "print(C)" in out


def test_dollar_stripped_in_py():
    out = gen(P("preceito capítulo $idade seja 1 amém"))
    assert "$" not in out
    assert "idade = 1" in out


def test_caso_elif_else():
    out = gen(
        P(
            "preceito capítulo $x seja 2 amém "
            "caso $x conforme_a 1 proclame 1 amém "
            "doutra_sorte_caso $x conforme_a 2 proclame 2 amém "
            "doutra_sorte proclame 3 amém amém_senhor"
        )
    )
    assert "if x == 1:" in out and "elif x == 2:" in out and "else:" in out


def test_enquanto():
    out = gen(P("preceito capítulo $n seja 3 amém enquanto $n exaltado_sobre 0 $n seja $n privado_de 1 amém amém_senhor"))
    assert "while n > 0:" in out


def test_peregrine_desugar():
    out = gen(
        P(
            "preceito capítulo $i seja 1 amém preceito capítulo $s seja 0 amém "
            "peregrine $i seja 1 amém $i não_acima_de 5 amém $i seja $i somado_a 1 amém "
            "$s seja $s somado_a $i amém amém_senhor"
        )
    )
    assert "while i <= 5:" in out
    lines = out.splitlines()
    body = lines[lines.index("while i <= 5:") + 1 :]
    assert body[-1].strip() == "i = i + 1"
    assert any(l.strip() == "s = s + i" for l in body)


def test_em_cada():
    out = gen(P('preceito salmo $t seja "oi" amém em_cada $c $t proclame $c amém amém_senhor'))
    assert "for c in t:" in out


def test_confesse_casts():
    out = gen(
        P(
            "preceito capítulo $a amém preceito versículo $b amém "
            "preceito salmo $s amém preceito dogma $d amém "
            "confesse $a amém confesse $b amém confesse $s amém confesse $d amém"
        )
    )
    assert "a = int(input())" in out
    assert "b = float(input())" in out
    assert "s = input()" in out
    assert 'd = input().strip().lower() in ("verdade", "true", "1", "sim")' in out


def test_sem_init_zero_default():
    out = gen(P("preceito capítulo $a amém preceito versículo $b amém preceito salmo $s amém preceito dogma $d amém"))
    assert "a = 0" in out and "b = 0.0" in out and 's = ""' in out and "d = False" in out


def test_string_escape_roundtrip():
    out = gen(P('proclame "a\\"b" amém'))
    assert 'print("a\\"b")' in out


def test_shadow_renomeia():
    out = gen(
        P(
            "preceito capítulo $x seja 1 amém "
            "caso verdade preceito capítulo $x seja 2 amém proclame $x amém amém_senhor "
            "proclame $x amém"
        )
    )
    assert "x = 1" in out
    assert "x__1 = 2" in out
    assert "print(x__1)" in out
    assert out.rstrip().endswith("print(x)")


def test_bloco_vazio_pass():
    out = gen(P("caso verdade amém_senhor"))
    assert "if True:" in out and "pass" in out


def test_cessai_perseverai():
    out = gen(P("enquanto verdade cessai amém perseverai amém amém_senhor"))
    assert "while True:" in out
    assert "break" in out and "continue" in out


def test_def_call_retorne():
    out = gen(
        P(
            "oficio capítulo $soma capítulo $a capítulo $b "
            "retorne $a somado_a $b amém amém_senhor "
            "preceito capítulo $r seja $soma(2, 3) amém "
            "proclame $r amém"
        )
    )
    assert "def soma(a, b):" in out
    assert "return a + b" in out
    assert "r = soma(2, 3)" in out


def test_retorne_nu():
    out = gen(P("oficio salmo $f salmo $s retorne amém amém_senhor"))
    assert "def f(s):" in out
    assert "\n    return\n" in out


def test_def_aninhada():
    out = gen(
        P(
            "oficio capítulo $f capítulo $n "
            "oficio capítulo $g capítulo $m retorne $m amém amém_senhor "
            "retorne $g($n) amém amém_senhor"
        )
    )
    assert "def f(n):" in out
    assert "    def g(m):" in out
    assert "return g(n)" in out
