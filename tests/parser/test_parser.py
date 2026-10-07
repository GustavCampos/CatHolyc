import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lexer.lexer import tokenize
from parser import ast_nodes as A
from parser.parser import ParserError, parse


def parse_src(src: str) -> A.Programa:
    toks, errs = tokenize(src)
    assert errs == []
    return parse(toks)


def test_readme_example_se_shape():
    src = (
        Path(__file__).parents[1] / "programs" / "exemplo_readme.holy"
    ).read_text(encoding="utf-8")
    prog = parse_src(src)
    assert isinstance(prog, A.Programa)
    assert len(prog.comandos) == 4
    assert isinstance(prog.comandos[0], A.DeclConst)
    assert prog.comandos[0].nome == "maioridade"
    assert isinstance(prog.comandos[3], A.Se)
    se = prog.comandos[3]
    # raiz em_comunhão_com, filhas relacionais
    assert isinstance(se.condicao, A.OperacaoBinaria)
    assert se.condicao.operador == "em_comunhão_com"
    assert se.condicao.esquerda.operador == "exaltado_sobre"
    assert se.condicao.direita.operador == "conforme_a"
    assert len(se.entao) == 1 and isinstance(se.entao[0], A.Saida)
    assert se.senao is not None and len(se.senao) == 1


def test_decl_var_sem_init_e_atribuicao():
    prog = parse_src(
        "em_nome_do_pai preceito capítulo x amém x seja 1 amém assim_seja_em_seu_nome_amem"
    )
    assert isinstance(prog.comandos[0], A.DeclVar)
    assert prog.comandos[0].valor is None
    assert isinstance(prog.comandos[1], A.Atribuicao)


def test_precedencia_soma_mult():
    prog = parse_src(
        "em_nome_do_pai proclame 2 somado_a 3 multiplicado_por 4 amém assim_seja_em_seu_nome_amem"
    )
    expr = prog.comandos[0].expressao
    assert isinstance(expr, A.OperacaoBinaria)
    assert expr.operador == "somado_a"
    assert isinstance(expr.direita, A.OperacaoBinaria)
    assert expr.direita.operador == "multiplicado_por"


def test_parenteses_transparente():
    prog = parse_src(
        "em_nome_do_pai proclame ( 2 somado_a 3 ) multiplicado_por 4 amém assim_seja_em_seu_nome_amem"
    )
    expr = prog.comandos[0].expressao
    assert expr.operador == "multiplicado_por"
    assert expr.esquerda.operador == "somado_a"


def test_doutra_sorte_caso_chain():
    prog = parse_src(
        "em_nome_do_pai caso verdade proclame 1 amém "
        "doutra_sorte_caso falsidade proclame 2 amém "
        "doutra_sorte_caso verdade proclame 3 amém "
        "doutra_sorte proclame 4 amém amém_senhor assim_seja_em_seu_nome_amem"
    )
    se = prog.comandos[0]
    assert isinstance(se, A.Se)
    assert len(se.senaoSe) == 2
    assert se.senao is not None


def test_enquanto_para_paracada_entrada():
    prog = parse_src(
        "em_nome_do_pai "
        "enquanto verdade proclame 1 amém amém_senhor "
        "peregrine i seja 0 amém i submisso_a 10 amém i seja i somado_a 1 amém proclame i amém amém_senhor "
        "em_cada c texto proclame c amém amém_senhor "
        "confesse x amém "
        "assim_seja_em_seu_nome_amem"
    )
    assert isinstance(prog.comandos[0], A.Enquanto)
    assert isinstance(prog.comandos[1], A.Para)
    assert isinstance(prog.comandos[2], A.ParaCada)
    assert isinstance(prog.comandos[3], A.Entrada)


def test_unarios_nao_e_menos():
    prog = parse_src(
        "em_nome_do_pai proclame não_seja verdade amém proclame privado_de 5 amém assim_seja_em_seu_nome_amem"
    )
    assert isinstance(prog.comandos[0].expressao, A.OperacaoUnaria)
    assert isinstance(prog.comandos[1].expressao, A.OperacaoUnaria)


def test_missing_amem_error():
    toks, errs = tokenize("em_nome_do_pai preceito capítulo idade 21 amém assim_seja_em_seu_nome_amem")
    assert errs == []
    with pytest.raises(ParserError, match="Erro sintático"):
        parse(toks)


def test_missing_amem_senhor_error():
    toks, errs = tokenize("em_nome_do_pai caso verdade proclame 1 amém assim_seja_em_seu_nome_amem")
    assert errs == []
    with pytest.raises(ParserError):
        parse(toks)
