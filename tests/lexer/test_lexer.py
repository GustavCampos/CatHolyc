import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from lexer.lexer import tokenize
from lexer.TokenType import RESERVED_MAP, TokenType


def test_reserved_full_list():
    for lex, tipo in RESERVED_MAP.items():
        toks, errs = tokenize(lex)
        assert errs == []
        assert toks[0].tipo == tipo
        assert toks[0].lexema == lex


def test_longest_match_amem():
    toks, errs = tokenize("amém_senhor")
    assert errs == []
    assert toks[0].tipo == TokenType.AMEM_SENHOR


def test_longest_match_doutra():
    toks, errs = tokenize("doutra_sorte_caso")
    assert errs == []
    assert toks[0].tipo == TokenType.DOUTRA_SORTE_CASO
    toks, _ = tokenize("doutra_sorte")
    assert toks[0].tipo == TokenType.DOUTRA_SORTE


def test_numbers():
    toks, errs = tokenize("18 18.5")
    assert errs == []
    assert toks[0].tipo == TokenType.NUMBER_INT
    assert toks[1].tipo == TokenType.NUMBER_REAL


def test_number_trailing_dot_error():
    _, errs = tokenize("12.")
    assert len(errs) == 1


def test_string_and_escape():
    toks, errs = tokenize(r'"a \"b\" c"')
    assert errs == []
    assert toks[0].tipo == TokenType.TEXT_LITERAL


def test_unterminated_string_error():
    _, errs = tokenize('"aberto')
    assert len(errs) == 1


def test_invalid_symbols_collect():
    _, errs = tokenize("# @")
    assert len(errs) == 2


def test_line_col_tracking():
    toks, _ = tokenize("18\n21")
    assert toks[0].linha == 1
    assert toks[1].linha == 2


def test_crlf_counts_once():
    toks, _ = tokenize("18\r\n21")
    assert toks[1].linha == 2


def test_glosa_comment_skipped():
    toks, errs = tokenize("18 glosa(explica) 21")
    assert errs == []
    assert [t.lexema for t in toks if t.tipo != TokenType.EOF] == ["18", "21"]


def test_glosa_like_identifier():
    toks, errs = tokenize("glosario")
    assert errs == []
    assert toks[0].tipo == TokenType.IDENTIFIER


def test_block_comment_inline():
    toks, errs = tokenize("18 |> anota <| 21")
    assert errs == []
    assert [t.lexema for t in toks if t.tipo != TokenType.EOF] == ["18", "21"]


def test_block_comment_multiline_counts_lines():
    toks, errs = tokenize("18 |> a\nb <| 21")
    assert errs == []
    assert toks[1].lexema == "21"
    assert toks[1].linha == 2


def test_block_comment_unterminated_error():
    toks, errs = tokenize("18 |> aberto")
    assert len(errs) == 1
    assert toks[0].lexema == "18"


def test_comment_inside_string_not_comment():
    toks, errs = tokenize('"|> nao comentario <|"')
    assert errs == []
    assert toks[0].tipo == TokenType.TEXT_LITERAL


def test_readme_example_zero_errors():
    src = Path(__file__).parents[1] / "programs" / "exemplo_readme.holy"
    toks, errs = tokenize(src.read_text(encoding="utf-8"))
    assert errs == []
    assert toks[-1].tipo == TokenType.EOF
    names = [t.tipo for t in toks]
    assert TokenType.EM_NOME_DO_PAI in names
    assert TokenType.ASSIM_SEJA_EM_SEU_NOME_AMEM in names


def test_eof_appended():
    toks, errs = tokenize("")
    assert errs == []
    assert toks[-1].tipo == TokenType.EOF
