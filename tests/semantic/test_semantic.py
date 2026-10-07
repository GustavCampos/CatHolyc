import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lexer.lexer import tokenize
from parser.parser import parse
from semantic.analyzer import SemanticError, analyze


def check(src: str):
    toks, errs = tokenize(src)
    assert errs == []
    prog = parse(toks)
    return analyze(prog)


def check_fails(src: str, frag: str):
    with pytest.raises(SemanticError, match=frag):
        check(src)


def P(body: str) -> str:
    return f"em_nome_do_pai {body} assim_seja_em_seu_nome_amem"


def test_valid_readme():
    src = (Path(__file__).parents[1] / "programs" / "exemplo_readme.holy").read_text(encoding="utf-8")
    toks, errs = tokenize(src)
    assert errs == []
    analyze(parse(toks))


def test_valid_int_to_float_promote():
    check(P("preceito versículo x seja 18 amém"))


def test_valid_shadow_inner_scope():
    check(
        P(
            "preceito capítulo x seja 1 amém "
            "caso verdade preceito capítulo x seja 2 amém proclame x amém amém_senhor"
        )
    )


def test_redeclare_same_scope():
    check_fails(
        P("preceito capítulo x amém preceito capítulo x amém"),
        "redeclaração",
    )


def test_undeclared_use():
    check_fails(P("x seja 1 amém"), "identificador desconhecido")


def test_const_reassign():
    check_fails(
        P("mandamento capítulo c seja 1 amém c seja 2 amém"),
        "atribuição a constante",
    )


def test_int_to_salmo():
    check_fails(
        P("preceito salmo s seja 18 amém"),
        "tipos incompatíveis",
    )


def test_non_dogma_condition():
    check_fails(
        P("preceito capítulo x seja 1 amém caso x proclame 1 amém amém_senhor"),
        "deve ser do tipo dogma",
    )


def test_logic_on_int():
    check_fails(
        P(
            "preceito capítulo x seja 1 amém "
            "preceito capítulo y seja 2 amém "
            "caso x em_comunhão_com y proclame 1 amém amém_senhor"
        ),
        "operador lógico",
    )


def test_aritmetica_em_salmo():
    check_fails(
        P('preceito salmo s seja "a" amém proclame s somado_a s amém'),
        "aritmética",
    )


def test_dizimo_exige_int():
    check_fails(
        P("preceito versículo x seja 1.5 amém proclame x dízimo_de x amém"),
        "dízimo_de",
    )


def test_confesse_const():
    check_fails(
        P("mandamento capítulo c seja 1 amém confesse c amém"),
        "atribuição a constante",
    )


def test_em_cada_apenas_salmo():
    check_fails(
        P(
            "preceito capítulo n seja 5 amém "
            "em_cada c n proclame c amém amém_senhor"
        ),
        "em_cada suporta apenas salmo",
    )


def test_em_cada_salmo_ok():
    check(P('preceito salmo t seja "oi" amém em_cada c t proclame c amém amém_senhor'))
