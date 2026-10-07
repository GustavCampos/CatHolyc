from enum import Enum, auto


class TokenType(Enum):
    # types
    CAPITULO = auto()
    VERSICULO = auto()
    SALMO = auto()
    DOGMA = auto()
    # declarations / assignment
    MANDAMENTO = auto()
    PRECEITO = auto()
    SEJA = auto()
    # arithmetic
    SOMADO_A = auto()
    PRIVADO_DE = auto()
    MULTIPLICADO_POR = auto()
    PARTILHADO_ENTRE = auto()
    DIZIMO_DE = auto()
    # relational
    EXALTADO_SOBRE = auto()
    SUBMISSO_A = auto()
    NAO_ABAIXO_DE = auto()
    NAO_ACIMA_DE = auto()
    CONFORME_A = auto()
    DISSONANTE_DE = auto()
    # logical
    EM_COMUNHAO_COM = auto()
    OU_PORVENTURA = auto()
    NAO_SEJA = auto()
    # control
    CASO = auto()
    DOUTRA_SORTE_CASO = auto()
    DOUTRA_SORTE = auto()
    ENQUANTO = auto()
    PEREGRINE = auto()
    EM_CADA = auto()
    CESSAI = auto()
    PERSEVERAI = auto()
    OFICIO = auto()
    RETORNE = auto()
    PROCLAME = auto()
    CONFESSE = auto()
    # boolean literals
    VERDADE = auto()
    FALSIDADE = auto()
    # delimiters
    EM_NOME_DO_PAI = auto()
    AMEM = auto()
    AMEM_SENHOR = auto()
    ASSIM_SEJA_EM_SEU_NOME_AMEM = auto()
    # lexical
    IDENTIFIER = auto()
    NUMBER_INT = auto()
    NUMBER_REAL = auto()
    TEXT_LITERAL = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    EOF = auto()


RESERVED_MAP: dict[str, TokenType] = {
    "capítulo": TokenType.CAPITULO,
    "versículo": TokenType.VERSICULO,
    "salmo": TokenType.SALMO,
    "dogma": TokenType.DOGMA,
    "mandamento": TokenType.MANDAMENTO,
    "preceito": TokenType.PRECEITO,
    "seja": TokenType.SEJA,
    "somado_a": TokenType.SOMADO_A,
    "privado_de": TokenType.PRIVADO_DE,
    "multiplicado_por": TokenType.MULTIPLICADO_POR,
    "partilhado_entre": TokenType.PARTILHADO_ENTRE,
    "dízimo_de": TokenType.DIZIMO_DE,
    "exaltado_sobre": TokenType.EXALTADO_SOBRE,
    "submisso_a": TokenType.SUBMISSO_A,
    "não_abaixo_de": TokenType.NAO_ABAIXO_DE,
    "não_acima_de": TokenType.NAO_ACIMA_DE,
    "conforme_a": TokenType.CONFORME_A,
    "dissonante_de": TokenType.DISSONANTE_DE,
    "em_comunhão_com": TokenType.EM_COMUNHAO_COM,
    "ou_porventura": TokenType.OU_PORVENTURA,
    "não_seja": TokenType.NAO_SEJA,
    "caso": TokenType.CASO,
    "doutra_sorte_caso": TokenType.DOUTRA_SORTE_CASO,
    "doutra_sorte": TokenType.DOUTRA_SORTE,
    "enquanto": TokenType.ENQUANTO,
    "peregrine": TokenType.PEREGRINE,
    "em_cada": TokenType.EM_CADA,
    "cessai": TokenType.CESSAI,
    "perseverai": TokenType.PERSEVERAI,
    "oficio": TokenType.OFICIO,
    "retorne": TokenType.RETORNE,
    "proclame": TokenType.PROCLAME,
    "confesse": TokenType.CONFESSE,
    "verdade": TokenType.VERDADE,
    "falsidade": TokenType.FALSIDADE,
    "em_nome_do_pai": TokenType.EM_NOME_DO_PAI,
    "amém": TokenType.AMEM,
    "amém_senhor": TokenType.AMEM_SENHOR,
    "assim_seja_em_seu_nome_amem": TokenType.ASSIM_SEJA_EM_SEU_NOME_AMEM,
}
