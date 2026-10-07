# CatHolyc → Python Transpiler Spec

## 1 Goal
- Input: UTF-8 `.holy` source using vocab README §1
- Output: readable Python3 script, behavior-preserving
- Pipeline: Lexer → Parser + AST → Semantic check → Python emit → CLI run
- Non-goals V1: functions, arrays, structs, modules, optimizer, LSP

## 2 Pipeline
```
source text
→ Lexer ⇒ Token list
→ Parser ⇒ Programa AST
→ Semantic ⇒ SymbolTable + annotated AST / errors
→ CodeGen ⇒ Python source string
→ CLI ⇒ write .py, optionally run via interpreter
```

## 3 Layout
```
lexer/
  Token.py
  TokenType.py
  lexer.py
parser/
  ast_nodes.py
  parser.py
semantic/
  symbols.py
  analyzer.py
codegen/
  py_generator.py
tests/
  lexer/
  parser/
  semantic/
  e2e/
  programs/*.holy + *.expected_stdout + *.expected_py
cli.py
SPEC.md
```

## 4 Lexer
- API: `tokenize(source: str) -> tuple[list[Token], list[LexError]]`
- Handle `\r\n`, `\n`; track `line`, `col`
- Skip: `[ \t]+`, newlines count only, `glosa(...)` + `|> ... <|` comments (both discarded, newlines inside count)
- Identifiers require PHP-style `$` prefix: `\$[A-Za-zÀ-Úà-ú_][A-Za-zÀ-Úà-ú0-9_]*` ⇒ `IDENTIFIER` (lexeme keeps `$`, e.g. `$idade`); bare words without `$` are never identifiers
- Word chars: `[A-Za-zÀ-Úà-ú0-9_]` plus `$` only as identifier first char
- Longest match mandatory:
  - Consume maximal word run, then reserved lookup
  - Resolves `amém` vs `amém_senhor`, `doutra_sorte` vs `doutra_sorte_caso`
  - `$`-form bypasses reserved lookup: `$caso` ⇒ `IDENTIFIER`, not keyword
- Priority per position:
  0. comments (discarded, no token; newlines inside update `line`/`col`):
     - `glosa\([^)]*\)` ⇒ skip to `)`; V1 no nesting, single-line use
     - `\|>.*?<\|` (DOTALL, non-greedy) ⇒ block skip to first `<|`; V1 no nesting; unterminated `|>` ⇒ lex error, panic-mode resume after `|>`
  1. string `"([^"\n\\]|\\.)*"` ⇒ `TEXT_LITERAL`; unterminated ⇒ error
  2. number `[0-9]+\.[0-9]+` ⇒ `NUMBER_REAL`, else `[0-9]+` ⇒ `NUMBER_INT`; `12.` ⇒ error
  3. `$` + word run ⇒ `IDENTIFIER` (lexeme includes `$`); lone `$` or `$` + non-letter ⇒ `ERRO_LEXICO`; `$caso` stays identifier
  4. word run ⇒ reserved lookup ⇒ else `ERRO_LEXICO` (bare non-reserved words are errors, not identifiers)
  5. `(` `)` ⇒ `LPAREN` `RPAREN`; `,` ⇒ `COMMA` (argument separator for `oficio` calls)
  6. else ⇒ `ERRO_LEXICO`
- Reserved map: exact strings README §2.3, including accented forms `não_*`, `em_comunhão_com`, plus `cessai`, `perseverai`, `oficio`, `retorne`
- Errors: collect, panic-mode resume
- Append `EOF` token at end
- Extend `TokenType` with `LPAREN`, `RPAREN`, `COMMA`, `EOF`

## 5 Parser + AST
- Recursive descent, LL(1), no backtrack
- Cursor + `atual()` + `consome(expected)`
- Entry: `parse(tokens) -> Programa`
- IDENT in source is `$`-prefixed (`$idade`); parser strips `$` via `_nome_ident()` so AST `nome` is bare (`idade`); Python emit has no `$`
- Functions map 1:1 to nonterminals README §3:
  `parsePrograma, parseBloco, parseComando, parseDeclConst, parseDeclVar, parseAtribuicao, parseSe, parseEnquanto, parsePara, parseParaCada, parseCessai, parsePerseverai, parseDefFuncao, parseRetorne, parseSaida, parseEntrada, parseExpressaoOu/E/Nao/Rel/Add/Mul, parseFator`
- `Chamada` decided in `parseFator` by lookahead `IDENT + LPAREN`; calls keep `$` prefix (`$soma(2, 3)`)
- `Bloco` = loop while `atual() in FIRST(Comando)`; return `list[Comando]`; emit no node
- Expressions return left-assoc `OperacaoBinaria` chains; `não_seja` ⇒ `OperacaoUnaria`; parens transparent; `privado_de Fator` ⇒ unary minus
- AST nodes (dataclasses, each with `linha: int`):
```python
@dataclass
class Programa:
    comandos: list
@dataclass
class DeclConst:
    tipo: str; nome: str; valor: object; linha: int
@dataclass
class DeclVar:
    tipo: str; nome: str; valor: object | None; linha: int
@dataclass
class Atribuicao:
    nome: str; valor: object; linha: int
@dataclass
class Se:
    condicao: object; entao: list; senaoSe: list; senao: list | None; linha: int
@dataclass
class Enquanto:
    condicao: object; corpo: list; linha: int
@dataclass
class Para:
    init: object; condicao: object; incremento: object; corpo: list; linha: int
@dataclass
class ParaCada:
    variavel: str; colecao: str; corpo: list; linha: int
@dataclass
class Saida:
    expressao: object; linha: int
@dataclass
class Entrada:
    variavel: str; linha: int
@dataclass
class Cessai:
    linha: int
@dataclass
class Perseverai:
    linha: int
@dataclass
class Param:
    tipo: str; nome: str; linha: int
@dataclass
class DefFuncao:
    tipo: str; nome: str; params: list; corpo: list; linha: int
@dataclass
class Retorne:
    valor: object | None; linha: int
@dataclass
class Chamada:
    nome: str; args: list; linha: int
@dataclass
class OperacaoBinaria:
    operador: str; esquerda: object; direita: object; linha: int
@dataclass
class OperacaoUnaria:
    operador: str; operando: object; linha: int
@dataclass
class Identificador:
    nome: str; linha: int
@dataclass
class Literal:
    tipo: str; valor: object; linha: int
```
- Errors: fail-fast on first error

## 6 Block rule
- `amém_senhor` closes all block contexts
- Structures using close:
```
caso ... [doutra_sorte_caso ...]* [doutra_sorte ...] amém_senhor
enquanto ... amém_senhor
peregrine ... amém_senhor
em_cada ... amém_senhor
```
- No separate loop-close symbol needed
- Parser: each block parser consumes trailing `amém_senhor`
- Python emit: `amém_senhor` ⇒ dedent only, emit nothing

## 7 Semantic
- Symbol table: stacked scopes; global scope = program body; `caso/enquanto/peregrine/em_cada` push new scope
- Rules:
  - `mandamento` requires init; missing ⇒ `ESEM const sem inicialização`
  - no redeclare same scope ⇒ `ESEM redeclaração`
  - use-before-decl ⇒ `ESEM identificador desconhecido`
  - assignment to const ⇒ `ESEM atribuição a constante`
  - types: `capítulo=int`, `versículo=float`, `salmo=str`, `dogma=bool`
  - assignment compatible: allow `int→float` promote, else strict
  - condition in `caso/enquanto/peregrine` must be `dogma`
  - arithmetic on numerics only; `dízimo_de` ints only; `salmo` no arithmetic
  - relational: numerics compare numerics; `conforme_a/dissonante_de` allow same-type incl strings/bool
  - logic operands must be `dogma`
  - `proclame`: any single `ExpressaoOu`
  - `confesse`: target must be declared `preceito` variable, not const
  - `em_cada` V1: restrict to iteration over `salmo`; other types ⇒ `ESEM em_cada suporta apenas salmo em V1`
  - `cessai`/`perseverai` only inside loop (`enquanto/peregrine/em_cada`); nested `oficio` does not inherit outer loop (depth barrier) ⇒ `ESEM 'cessai'/'perseverai' fora de laço`
  - `oficio` shares namespace with variables (same-scope redeclare forbidden); oficio name is const (no assignment) ⇒ `ESEM atribuição a oficio`
  - `retorne` only inside `oficio`; valued return must match declared type (`int→float` promotes); bare `retorne` always valid (early exit)
  - call: target must be declared `oficio` (not plain variable); exact arity; per-arg compatibility
  - inside `oficio`, writing (`seja`, `confesse`) to outer-scope variables is forbidden (V1: read-only; Python would silently create a local)
- Type inference: literals ⇒ own type; identifier ⇒ table type; binary ⇒ result type table (numeric promote, relational/logic ⇒ `dogma`)

## 8 Python CodeGen
- Module API: `generate(programa: Programa) -> str`
- Indent: 4 spaces; maintain indent stack; `amém_senhor` pops stack
- Mapping:
  - `capítulo` ⇒ `int`; `versículo` ⇒ `float`; `salmo` ⇒ `str`; `dogma` ⇒ `bool`
  - `mandamento/preceito x seja E` ⇒ `x = E` (source `$x`, AST/emit bare `x`); const via UPPER convention + semantic enforcement then erase
  - `seja` ⇒ `=`
  - `somado_a/privado_de/multiplicado_por/partilhado_entre/dízimo_de` ⇒ `+ - * / %`; note `/` semantic: Python `/` always float; emit `//` when both operands `int` and source intent = integer division, or document difference; decide per project and keep consistent
  - `exaltado_sobre/submisso_a/não_abaixo_de/não_acima_de/conforme_a/dissonante_de` ⇒ `> < >= <= == !=`; strings compare with `==` directly
  - `em_comunhão_com/ou_porventura/não_seja` ⇒ `and or not`
  - `verdade/falsidade` ⇒ `True/False`
  - `caso/doutra_sorte_caso/doutra_sorte` ⇒ `if/elif/else:` + indent
  - `enquanto` ⇒ `while cond:` + indent
  - `peregrine` C-style ⇒ desugar to `while` loop in generator
  - `em_cada v col` ⇒ `for v in col:` native
  - `cessai`/`perseverai` ⇒ `break`/`continue`
  - `oficio T f T p...` ⇒ `def f(p, ...):` (name as-written, no UPPER; nestable)
  - `retorne E` / bare `retorne` ⇒ `return E` / `return`
  - `$f(a, b)` ⇒ `f(a, b)`
  - `proclame E` ⇒ `print(E)`
  - `confesse x` ⇒ `x = input()` + cast: `int(input())`, `float(input())`, `input()` per declared type
  - `em_nome_do_pai / assim_seja_em_seu_nome_amem` ⇒ emit header comment + top-level script, optional `if __name__ == "__main__":` wrapper disabled by default
  - `amém` ⇒ newline, emit nothing extra
- Preserve line trace: optional `# linha N` comments
- Example:
```python
# em_nome_do_pai
MAIORIDADE = 18
idade = 21
estudante = True
if idade > MAIORIDADE and estudante == True:
    print("É maior de idade e estudante.")
else:
    print("A condição não foi satisfeita.")
```

## 9 CLI
```
python cli.py program.holy [-o out.py] [--dump-tokens] [--dump-ast] [--emit-py-only] [--run] [--strict]
```
- Exit codes: `0` success, `1` lexical/syntactic/semantic error, `2` IO/usage error
- `--run`: write temp `.py`, execute via interpreter subprocess, forward stdout
- All errors to stderr, Portuguese, same formats §§10

## 10 Errors
```
Erro léxico: símbolo ou lexema inválido '<lex>' na linha <N>, coluna <C>
Erro sintático: linha <N> — encontrado '<lex>' (<cat>), esperado '<exp>'
Erro semântico: linha <N> — <msg>
```
- Lexer: collect multiple, panic-mode resume
- Parser/Semantic: fail-fast first error

## 11 Tests
  - Lexer golden: reserved full list, `$`-identifier / bare-word-error / lone-`$` / `$caso`-is-identifier, longest-match pairs, numbers, strings + escapes, errors `# @ 12. "aberto`, line/col tracking
- Parser golden: README example + each command + precedence test `2 somado_a 3 multiplicado_por 4` + parens + `doutra_sorte_caso` chain + missing `amém` error
- Semantic negative: redeclare, undeclared use, const reassign, int→salmo assign, non-dogma condition, logic on int, `cessai` outside loop, `retorne` outside `oficio`, return-type mismatch, arity mismatch, call of non-oficio, write to outer-scope var inside `oficio`
- E2E: run 7 programs: hello, vars/const, caso, enquanto countdown, peregrine sum, laco_cessai (break/continue), funcao_soma (oficio calls); diff stdout vs expected
- Store under `tests/programs/*.holy + *.expected_stdout + *.expected_py`

## 12 Milestones
- M1 Lexer done: extend `TokenType` with `LPAREN RPAREN EOF`; implement `lexer/lexer.py` + reserved table; line/col; tests pass; README example tokenizes zero errors
- M2 Parser + AST done: create `parser/ast_nodes.py`; implement `parser/parser.py`; dump AST JSON; tests pass; README example parses to expected `Se` shape
- M3 Semantic done: implement `semantic/symbols.py`, `semantic/analyzer.py`; 8 negative cases rejected; valid example passes
- M4 Python CodeGen done: implement `codegen/py_generator.py`; mapping §8; 5 E2E programs run with matching stdout
- M5 CLI + E2E done: implement `cli.py` flags §9; exit codes; `--run` works end-to-end
- M6 Polish + defense done: unify error format; add `--dump-tokens/ast`; docs: formal sections 5-7 (semântica, codegen, testes); slides mapping production→function→AST node
- M7 Loop control + functions done: `cessai/perseverai` (break/continue, loop-depth check); `oficio/retorne` (nested defs, bare return, `,` args, `$` calls, arity/type checks, no outer writes); 2 new E2E programs

## 13 Open decisions
- `peregrine` header exact syntax: proposal `peregrine Init Cond amém Incr Bloco amém_senhor` — confirm, else adjust parser + codegen together
- `versículo` maps to `float` (`double` equivalent) for `input()/print()` simplicity
- `em_cada` V1 limited to `salmo`; postpone arrays
- Comments: adopt `glosa(...)`
- Integer division: choose `//` vs `/` mapping explicitly before M4; document choice
