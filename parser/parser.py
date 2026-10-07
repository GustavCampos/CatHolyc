from lexer.Token import Token
from lexer.TokenType import TokenType
from parser import ast_nodes as A


class ParserError(Exception):
    pass


def _fmt_error(tok: Token, esperado: str) -> str:
    lex = tok.lexema if tok.lexema != "" else "EOF"
    return (
        f"Erro sintático: linha {tok.linha} — "
        f"encontrado '{lex}' ({tok.tipo.name}), esperado '{esperado}'"
    )


FIRST_COMANDO = {
    TokenType.MANDAMENTO,
    TokenType.PRECEITO,
    TokenType.IDENTIFIER,
    TokenType.CASO,
    TokenType.ENQUANTO,
    TokenType.PEREGRINE,
    TokenType.EM_CADA,
    TokenType.PROCLAME,
    TokenType.CONFESSE,
}

_TIPOS = {
    TokenType.CAPITULO,
    TokenType.VERSICULO,
    TokenType.SALMO,
    TokenType.DOGMA,
}

_OP_REL = {
    TokenType.EXALTADO_SOBRE,
    TokenType.SUBMISSO_A,
    TokenType.NAO_ABAIXO_DE,
    TokenType.NAO_ACIMA_DE,
    TokenType.CONFORME_A,
    TokenType.DISSONANTE_DE,
}

_OP_ADD = {TokenType.SOMADO_A, TokenType.PRIVADO_DE}
_OP_MUL = {
    TokenType.MULTIPLICADO_POR,
    TokenType.PARTILHADO_ENTRE,
    TokenType.DIZIMO_DE,
}


def _decode_texto(lex: str) -> str:
    inner = lex[1:-1] if len(lex) >= 2 else ""
    out = []
    i = 0
    while i < len(inner):
        if inner[i] == "\\" and i + 1 < len(inner):
            nxt = inner[i + 1]
            mapping = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
            out.append(mapping.get(nxt, nxt))
            i += 2
        else:
            out.append(inner[i])
            i += 1
    return "".join(out)


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def atual(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def consome(self, esperado: TokenType, nome_esperado: str | None = None) -> Token:
        tok = self.atual()
        if tok.tipo is not esperado:
            raise ParserError(_fmt_error(tok, nome_esperado or esperado.name))
        self.pos += 1
        return tok

    # Programa ::= "em_nome_do_pai" Bloco "assim_seja_em_seu_nome_amem"
    def parsePrograma(self) -> A.Programa:
        t0 = self.consome(TokenType.EM_NOME_DO_PAI, "em_nome_do_pai")
        comandos = self.parseBloco()
        self.consome(
            TokenType.ASSIM_SEJA_EM_SEU_NOME_AMEM, "assim_seja_em_seu_nome_amem"
        )
        self.consome(TokenType.EOF, "EOF")
        return A.Programa(comandos=comandos, linha=t0.linha)

    # Bloco ::= { Comando }
    def parseBloco(self) -> list:
        cmds = []
        while self.atual().tipo in FIRST_COMANDO:
            cmds.append(self.parseComando())
        return cmds

    def parseComando(self) -> object:
        t = self.atual().tipo
        if t is TokenType.MANDAMENTO:
            return self.parseDeclConst()
        if t is TokenType.PRECEITO:
            return self.parseDeclVar()
        if t is TokenType.IDENTIFIER:
            return self.parseAtribuicao()
        if t is TokenType.CASO:
            return self.parseSe()
        if t is TokenType.ENQUANTO:
            return self.parseEnquanto()
        if t is TokenType.PEREGRINE:
            return self.parsePara()
        if t is TokenType.EM_CADA:
            return self.parseParaCada()
        if t is TokenType.PROCLAME:
            return self.parseSaida()
        if t is TokenType.CONFESSE:
            return self.parseEntrada()
        raise ParserError(
            _fmt_error(self.atual(), "um comando ou 'amém_senhor'")
        )

    def parseTipo(self) -> str:
        tok = self.atual()
        if tok.tipo not in _TIPOS:
            raise ParserError(_fmt_error(tok, "tipo (capítulo/versículo/salmo/dogma)"))
        self.pos += 1
        return tok.lexema

    # DeclConst ::= "mandamento" Tipo IDENT "seja" ExpressaoOu "amém"
    def parseDeclConst(self) -> A.DeclConst:
        t = self.consome(TokenType.MANDAMENTO, "mandamento")
        tipo = self.parseTipo()
        nome = self.consome(TokenType.IDENTIFIER, "IDENT").lexema
        self.consome(TokenType.SEJA, "seja")
        valor = self.parseExpressaoOu()
        self.consome(TokenType.AMEM, "amém")
        return A.DeclConst(tipo=tipo, nome=nome, valor=valor, linha=t.linha)

    # DeclVar ::= "preceito" Tipo IDENT [ "seja" ExpressaoOu ] "amém"
    def parseDeclVar(self) -> A.DeclVar:
        t = self.consome(TokenType.PRECEITO, "preceito")
        tipo = self.parseTipo()
        nome = self.consome(TokenType.IDENTIFIER, "IDENT").lexema
        valor = None
        if self.atual().tipo is TokenType.SEJA:
            self.pos += 1
            valor = self.parseExpressaoOu()
        self.consome(TokenType.AMEM, "amém")
        return A.DeclVar(tipo=tipo, nome=nome, valor=valor, linha=t.linha)

    # Atribuicao ::= IDENT "seja" ExpressaoOu "amém"
    def parseAtribuicao(self) -> A.Atribuicao:
        nome_tok = self.consome(TokenType.IDENTIFIER, "IDENT")
        self.consome(TokenType.SEJA, "seja")
        valor = self.parseExpressaoOu()
        self.consome(TokenType.AMEM, "amém")
        return A.Atribuicao(nome=nome_tok.lexema, valor=valor, linha=nome_tok.linha)

    # ComandoSe ::= "caso" ExpressaoOu Bloco { "doutra_sorte_caso" ... } [ "doutra_sorte" Bloco ] "amém_senhor"
    def parseSe(self) -> A.Se:
        t = self.consome(TokenType.CASO, "caso")
        cond = self.parseExpressaoOu()
        entao = self.parseBloco()
        ramos = []
        while self.atual().tipo is TokenType.DOUTRA_SORTE_CASO:
            te = self.consome(TokenType.DOUTRA_SORTE_CASO, "doutra_sorte_caso")
            ce = self.parseExpressaoOu()
            be = self.parseBloco()
            ramos.append(A.RamoSenaoSe(condicao=ce, bloco=be, linha=te.linha))
        senao = None
        if self.atual().tipo is TokenType.DOUTRA_SORTE:
            self.pos += 1
            senao = self.parseBloco()
        self.consome(TokenType.AMEM_SENHOR, "amém_senhor")
        return A.Se(condicao=cond, entao=entao, senaoSe=ramos, senao=senao, linha=t.linha)

    # ComandoEnquanto ::= "enquanto" ExpressaoOu Bloco "amém_senhor"
    def parseEnquanto(self) -> A.Enquanto:
        t = self.consome(TokenType.ENQUANTO, "enquanto")
        cond = self.parseExpressaoOu()
        corpo = self.parseBloco()
        self.consome(TokenType.AMEM_SENHOR, "amém_senhor")
        return A.Enquanto(condicao=cond, corpo=corpo, linha=t.linha)

    # ComandoPara ::= "peregrine" Atribuicao ExpressaoOu "amém" Atribuicao Bloco "amém_senhor"
    def parsePara(self) -> A.Para:
        t = self.consome(TokenType.PEREGRINE, "peregrine")
        init = self.parseAtribuicao()
        cond = self.parseExpressaoOu()
        self.consome(TokenType.AMEM, "amém")
        incr = self.parseAtribuicao()
        corpo = self.parseBloco()
        self.consome(TokenType.AMEM_SENHOR, "amém_senhor")
        return A.Para(init=init, condicao=cond, incremento=incr, corpo=corpo, linha=t.linha)

    # ComandoParaCada ::= "em_cada" IDENT IDENT Bloco "amém_senhor"
    def parseParaCada(self) -> A.ParaCada:
        t = self.consome(TokenType.EM_CADA, "em_cada")
        var = self.consome(TokenType.IDENTIFIER, "IDENT").lexema
        col = self.consome(TokenType.IDENTIFIER, "IDENT").lexema
        corpo = self.parseBloco()
        self.consome(TokenType.AMEM_SENHOR, "amém_senhor")
        return A.ParaCada(variavel=var, colecao=col, corpo=corpo, linha=t.linha)

    # ComandoSaida ::= "proclame" ExpressaoOu "amém"
    def parseSaida(self) -> A.Saida:
        t = self.consome(TokenType.PROCLAME, "proclame")
        expr = self.parseExpressaoOu()
        self.consome(TokenType.AMEM, "amém")
        return A.Saida(expressao=expr, linha=t.linha)

    # ComandoEntrada ::= "confesse" IDENT "amém"
    def parseEntrada(self) -> A.Entrada:
        t = self.consome(TokenType.CONFESSE, "confesse")
        var = self.consome(TokenType.IDENTIFIER, "IDENT").lexema
        self.consome(TokenType.AMEM, "amém")
        return A.Entrada(variavel=var, linha=t.linha)

    # ExpressaoOu ::= ExpressaoE { "ou_porventura" ExpressaoE }
    def parseExpressaoOu(self) -> object:
        esq = self.parseExpressaoE()
        while self.atual().tipo is TokenType.OU_PORVENTURA:
            op = self.atual()
            self.pos += 1
            dir_ = self.parseExpressaoE()
            esq = A.OperacaoBinaria(
                operador=op.lexema, esquerda=esq, direita=dir_, linha=op.linha
            )
        return esq

    # ExpressaoE ::= ExpressaoNao { "em_comunhão_com" ExpressaoNao }
    def parseExpressaoE(self) -> object:
        esq = self.parseExpressaoNao()
        while self.atual().tipo is TokenType.EM_COMUNHAO_COM:
            op = self.atual()
            self.pos += 1
            dir_ = self.parseExpressaoNao()
            esq = A.OperacaoBinaria(
                operador=op.lexema, esquerda=esq, direita=dir_, linha=op.linha
            )
        return esq

    # ExpressaoNao ::= [ "não_seja" ] ExpressaoRel
    def parseExpressaoNao(self) -> object:
        if self.atual().tipo is TokenType.NAO_SEJA:
            op = self.atual()
            self.pos += 1
            operando = self.parseExpressaoNao()
            return A.OperacaoUnaria(
                operador=op.lexema, operando=operando, linha=op.linha
            )
        return self.parseExpressaoRel()

    # ExpressaoRel ::= ExpressaoAdd [ OpRel ExpressaoAdd ]
    def parseExpressaoRel(self) -> object:
        esq = self.parseExpressaoAdd()
        if self.atual().tipo in _OP_REL:
            op = self.atual()
            self.pos += 1
            dir_ = self.parseExpressaoAdd()
            return A.OperacaoBinaria(
                operador=op.lexema, esquerda=esq, direita=dir_, linha=op.linha
            )
        return esq

    # ExpressaoAdd ::= ExpressaoMul { OpAdd ExpressaoMul }
    def parseExpressaoAdd(self) -> object:
        esq = self.parseExpressaoMul()
        while self.atual().tipo in _OP_ADD:
            op = self.atual()
            self.pos += 1
            dir_ = self.parseExpressaoMul()
            esq = A.OperacaoBinaria(
                operador=op.lexema, esquerda=esq, direita=dir_, linha=op.linha
            )
        return esq

    # ExpressaoMul ::= Fator { OpMul Fator }
    def parseExpressaoMul(self) -> object:
        esq = self.parseFator()
        while self.atual().tipo in _OP_MUL:
            op = self.atual()
            self.pos += 1
            dir_ = self.parseFator()
            esq = A.OperacaoBinaria(
                operador=op.lexema, esquerda=esq, direita=dir_, linha=op.linha
            )
        return esq

    def parseFator(self) -> object:
        tok = self.atual()
        if tok.tipo is TokenType.IDENTIFIER:
            self.pos += 1
            return A.Identificador(nome=tok.lexema, linha=tok.linha)
        if tok.tipo is TokenType.NUMBER_INT:
            self.pos += 1
            return A.Literal(tipo="int", valor=int(tok.lexema), linha=tok.linha)
        if tok.tipo is TokenType.NUMBER_REAL:
            self.pos += 1
            return A.Literal(tipo="float", valor=float(tok.lexema), linha=tok.linha)
        if tok.tipo is TokenType.TEXT_LITERAL:
            self.pos += 1
            return A.Literal(
                tipo="texto", valor=_decode_texto(tok.lexema), linha=tok.linha
            )
        if tok.tipo is TokenType.VERDADE:
            self.pos += 1
            return A.Literal(tipo="bool", valor=True, linha=tok.linha)
        if tok.tipo is TokenType.FALSIDADE:
            self.pos += 1
            return A.Literal(tipo="bool", valor=False, linha=tok.linha)
        if tok.tipo is TokenType.LPAREN:
            self.pos += 1
            expr = self.parseExpressaoOu()
            self.consome(TokenType.RPAREN, ")")
            return expr
        if tok.tipo is TokenType.PRIVADO_DE:
            self.pos += 1
            operando = self.parseFator()
            return A.OperacaoUnaria(
                operador=tok.lexema, operando=operando, linha=tok.linha
            )
        raise ParserError(_fmt_error(tok, "expressão (identificador, número, texto, verdade/falsidade, '(')"))


def parse(tokens: list[Token]) -> A.Programa:
    return Parser(tokens).parsePrograma()
