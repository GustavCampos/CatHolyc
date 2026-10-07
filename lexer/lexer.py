from .Token import LexError, Token
from .TokenType import RESERVED_MAP, TokenType


def _is_word_start(c: str) -> bool:
    if c == "_":
        return True
    if "A" <= c <= "Z" or "a" <= c <= "z":
        return True
    # accented letters ( źró: SPEC Σ_letras incl. à-ú etc.)
    # exclude symbols like × ÷ (isalpha() False anyway)
    return "\u00c0" <= c <= "\u00ff" and c.isalpha()


def _is_word_part(c: str) -> bool:
    if _is_word_start(c):
        return True
    return "0" <= c <= "9"


def _advance_span(source: str, text: str, linha: int, coluna: int) -> tuple[int, int]:
    """Update (linha, coluna) after consuming text, handling \\r\\n, \\n, \\r."""
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\r" and i + 1 < n and text[i + 1] == "\n":
            linha += 1
            coluna = 1
            i += 2
        elif c == "\n" or c == "\r":
            linha += 1
            coluna = 1
            i += 1
        else:
            coluna += 1
            i += 1
    return linha, coluna


def tokenize(source: str) -> tuple[list[Token], list[LexError]]:
    tokens: list[Token] = []
    errors: list[LexError] = []
    n = len(source)
    i = 0
    linha = 1
    coluna = 1

    def cur_col() -> int:
        return coluna

    while i < n:
        c = source[i]

        # newlines: \r\n single break, else \n / lone \r
        if c == "\r" and i + 1 < n and source[i + 1] == "\n":
            i += 2
            linha += 1
            coluna = 1
            continue
        if c == "\n" or c == "\r":
            i += 1
            linha += 1
            coluna = 1
            continue
        if c == " " or c == "\t":
            i += 1
            coluna += 1
            continue

        # 0. comments (discarded)
        if source.startswith("|>", i):
            close = source.find("<|", i + 2)
            if close == -1:
                errors.append(LexError("|>", linha, coluna))
                i += 2
                coluna += 2
                continue
            span = source[i : close + 2]
            linha, coluna = _advance_span(source, span, linha, coluna)
            i = close + 2
            continue
        if source.startswith("glosa(", i):
            close = source.find(")", i + 6)
            if close == -1:
                errors.append(LexError("glosa(", linha, coluna))
                i += 6
                coluna += 6
                continue
            span = source[i : close + 1]
            linha, coluna = _advance_span(source, span, linha, coluna)
            i = close + 1
            continue

        # 1. string
        if c == '"':
            start_line, start_col = linha, cur_col()
            j = i + 1
            closed = False
            while j < n:
                cj = source[j]
                if cj == "\n" or cj == "\r":
                    break
                if cj == "\\" and j + 1 < n and source[j + 1] not in ("\n", "\r"):
                    j += 2
                    continue
                if cj == '"':
                    closed = True
                    break
                j += 1
            if closed:
                lex = source[i : j + 1]
                tokens.append(Token(TokenType.TEXT_LITERAL, lex, start_line, start_col))
                coluna += len(lex)
                i = j + 1
            else:
                lex = source[i:j]
                errors.append(LexError(lex, start_line, start_col))
                coluna += len(lex)
                i = j
            continue

        # 2. number
        if "0" <= c <= "9":
            start_line, start_col = linha, cur_col()
            j = i
            while j < n and "0" <= source[j] <= "9":
                j += 1
            if j < n and source[j] == ".":
                if j + 1 < n and "0" <= source[j + 1] <= "9":
                    j += 1
                    while j < n and "0" <= source[j] <= "9":
                        j += 1
                    lex = source[i:j]
                    tokens.append(Token(TokenType.NUMBER_REAL, lex, start_line, start_col))
                    coluna += len(lex)
                    i = j
                else:
                    lex = source[i : j + 1]  # e.g. "12."
                    errors.append(LexError(lex, start_line, start_col))
                    coluna += len(lex)
                    i = j + 1
            else:
                lex = source[i:j]
                tokens.append(Token(TokenType.NUMBER_INT, lex, start_line, start_col))
                coluna += len(lex)
                i = j
            continue

        # 3. word run (maximal munch) + reserved lookup
        if _is_word_start(c):
            start_line, start_col = linha, cur_col()
            j = i
            while j < n and _is_word_part(source[j]):
                j += 1
            lex = source[i:j]
            tipo = RESERVED_MAP.get(lex, TokenType.IDENTIFIER)
            tokens.append(Token(tipo, lex, start_line, start_col))
            coluna += len(lex)
            i = j
            continue

        # 4. parens
        if c == "(":
            tokens.append(Token(TokenType.LPAREN, c, linha, coluna))
            i += 1
            coluna += 1
            continue
        if c == ")":
            tokens.append(Token(TokenType.RPAREN, c, linha, coluna))
            i += 1
            coluna += 1
            continue

        # 5. invalid
        errors.append(LexError(c, linha, coluna))
        i += 1
        coluna += 1

    tokens.append(Token(TokenType.EOF, "", linha, coluna))
    return tokens, errors
