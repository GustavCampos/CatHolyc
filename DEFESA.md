# CatHolyc — Roteiro de Defesa (M6)

## 1. Pipeline (1 slide)

```
.holy → tokenize() → parse() → analyze() → generate() → .py → --run
lexer/      parser/     semantic/     codegen/        cli.py
```

## 2. Produção → Função → Nó AST (tabela-mestra)

| Produção (G) | Função (`parser/parser.py`) | Nó AST (`parser/ast_nodes.py`) |
|---|---|---|
| `Programa ::= em_nome_do_pai Bloco assim_seja...` | `parsePrograma` | `Programa { comandos, linha }` |
| `Bloco ::= { Comando }` | `parseBloco` (loop em `FIRST(Comando)`) | sem nó — `list[Comando]` achatada no pai |
| `Tipo ::= capítulo/versículo/salmo/dogma` | `parseTipo` | `str` (lexema) dentro de `DeclConst/DeclVar` |
| `DeclConst ::= mandamento Tipo IDENT seja Expr amém` | `parseDeclConst` | `DeclConst { tipo, nome ($ strip), valor }` |
| `DeclVar ::= preceito Tipo IDENT [seja Expr] amém` | `parseDeclVar` | `DeclVar { tipo, nome, valor? }` |
| `Atribuicao ::= IDENT seja Expr amém` | `parseAtribuicao` | `Atribuicao { nome, valor }` |
| `ComandoSe ::= caso Expr Bloco {doutra_sorte_caso ...} [doutra_sorte Bloco] amém_senhor` | `parseSe` | `Se { condicao, entao, senaoSe: [RamoSenaoSe], senao? }` |
| `ComandoEnquanto` | `parseEnquanto` | `Enquanto { condicao, corpo }` |
| `ComandoPara ::= peregrine Atr Expr amém Atr Bloco amém_senhor` | `parsePara` | `Para { init, condicao, incremento, corpo }` |
| `ComandoParaCada ::= em_cada IDENT IDENT Bloco amém_senhor` | `parseParaCada` | `ParaCada { variavel, colecao, corpo }` |
| `Cessai ::= cessai amém` | `parseCessai` | `Cessai { }` |
| `Perseverai ::= perseverai amém` | `parsePerseverai` | `Perseverai { }` |
| `DefFuncao ::= oficio Tipo IDENT {Tipo IDENT} Bloco amém_senhor` | `parseDefFuncao` | `DefFuncao { tipo, nome, params: [Param], corpo }` |
| `Retorne ::= retorne [ExpressaoOu] amém` | `parseRetorne` | `Retorne { valor? }` |
| `ComandoSaida` | `parseSaida` | `Saida { expressao }` |
| `ComandoEntrada` | `parseEntrada` | `Entrada { variavel }` |
| `ExpressaoOu ::= ExpressaoE {ou_porventura ...}` | `parseExpressaoOu` | `OperacaoBinaria { ou_porventura }` ou repasse |
| `ExpressaoE` | `parseExpressaoE` | `OperacaoBinaria { em_comunhão_com }` ou repasse |
| `ExpressaoNao ::= [não_seja] ExpressaoRel` | `parseExpressaoNao` | `OperacaoUnaria { não_seja }` ou repasse |
| `ExpressaoRel ::= ExpressaoAdd [OpRel ...]` | `parseExpressaoRel` | `OperacaoBinaria { relacional }` ou repasse |
| `ExpressaoAdd` | `parseExpressaoAdd` | `OperacaoBinaria { somado_a/privado_de }` |
| `ExpressaoMul` | `parseExpressaoMul` | `OperacaoBinaria { multiplicado_por/partilhado_entre/dízimo_de }` |
| `Fator ::= IDENT` | `parseFator` | `Identificador { nome }` |
| `Fator ::= Chamada` (`IDENT ( args )`, `,`-separados, `$` mantido) | `parseFator` (lookahead `IDENT+LPAREN`) | `Chamada { nome, args }` |
| `Fator ::= NUM_INT/NUM_REAL/TEXTO/verdade/falsidade` | `parseFator` | `Literal { tipo, valor }` |
| `Fator ::= ( ExpressaoOu )` | `parseFator` | transparente — retorna `ExpressaoOu` interno |
| `Fator ::= privado_de Fator` | `parseFator` | `OperacaoUnaria { privado_de }` |

Regras de decisão LL(1): `atual()` basta — `mandamento→DeclConst`, `preceito→DeclVar`,
`IDENT→Atribuicao`, `caso→Se`, `enquanto/ peregrine/ em_cada/ proclame/ confesse` análogos.
Sem backtracking; `Bloco` para diante de `amém_senhor / doutra_sorte* / EOF / assim_seja...`.

## 3. Walkthrough — condição do exemplo (fala 60s)

Fonte (`tests/programs/exemplo_readme.holy`, linha 8):

```
caso $idade exaltado_sobre $maioridade em_comunhão_com $estudante conforme_a verdade
```

Derivação: `ExpressaoOu → ExpressaoE` encontra `em_comunhão_com` (nível E),
lado esquerdo reduz `exaltado_sobre` (nível Rel, mais interno), lado direito
reduz `conforme_a`. AST real (`--dump-ast`):

```
OperacaoBinaria { em_comunhão_com,
  esquerda: OperacaoBinaria { exaltado_sobre, idade, maioridade },
  direita:  OperacaoBinaria { conforme_a, estudante, Literal bool true } }
```

Ponto a defender: precedência embutida na cadeia de chamadas
(`parseExpressaoOu → E → Nao → Rel → Add → Mul → Fator`); `2 somado_a 3
multiplicado_por 4` vira `2 somado_a (3 multiplicado_por 4)` sem tabela de
precedência em runtime. `$` removido em `_nome_ident()`; Python emite sem `$`.

## 4. Bloco e `amém_senhor` (pergunta clássica)

- `amém` = fim de comando (`;`); `amém_senhor` = fim de bloco (`}`), fecha
  **todos** os contextos (`caso / enquanto / peregrine / em_cada`).
- Cada `parseX` de bloco consome seu `amém_senhor` final; codegen só desempilha.
- Demo: `python cli.py tests/programs/exemplo_readme.holy --dump-tokens`
  mostra `AMEM_SENHOR` único fechando `caso+doutra_sorte`.

## 5. Semântica em 30s

Escopos em pilha (`SymbolTable`), global = corpo do programa; `caso/enquanto/
peregrine/em_cada` empilham. Regras-âncora: const exige init, sem redeclaração
no mesmo escopo, uso exige declaração, const imutável, `int→float` promove e
o resto é estrito, condição `dogma`, aritmética numérica, `dízimo_de` só
`capítulo`, `em_cada` V1 só `salmo`. Erro: `Erro semântico: linha N — ...`,
fail-fast.

## 6. Codegen em 30s

`generate(prog)`: `mandamento→UPPER`, `seja→=`, `partilhado_entre→//` se
`capítulo×capítulo` senão `/` (Python `/` sempre float; `//` difere de C só em
negativos — fora do E2E, `--strict` acusa), `peregrine→while` (init + `while`
+ incremento no fim), `em_cada→for`, `proclame→print`, `confesse→int/float/
input()/teste-dogma`. `preceito` sem init = zero padrão (`--strict` acusa).

## 7. Provas vivas (rode na defesa)

```
python -m pytest -q                                   # 128 passed
python cli.py tests/programs/exemplo_readme.holy --dump-tokens | head -8
python cli.py tests/programs/exemplo_readme.holy --dump-ast | head -20
python cli.py tests/programs/caso.holy --emit-py-only
python cli.py tests/programs/caso.holy --run
python cli.py tests/programs/caso.holy --emit-py-only --strict   # sai 0
python cli.py tests/programs/funcao_soma.holy --emit-py-only --run
python cli.py tests/programs/laco_cessai.holy --run -o /tmp/laco.py
echo 'em_nome_do_pai
preceito capítulo $x amém
proclame $x amém
assim_seja_em_seu_nome_amem' | python cli.py /dev/stdin --emit-py-only --strict  # sai 1 (aviso vira erro)
```

## 8. Perguntas prováveis + resposta curta

- *Por que sem recursão à esquerda?* Repetições `{ }` no lugar de
  `E ::= E op E`; descida recursiva não entra em loop, 1 lookahead decide.
- *Longest match onde?* `amém` prefixo de `amém_senhor`,
  `doutra_sorte` de `doutra_sorte_caso`; lexer consome run máximo, depois
  lookup em `RESERVED_MAP`; `$caso` desvia do lookup (identificador).
- *Por que `$` obrigatório?* Palavra sem `$` nunca é identificador — vira
  erro léxico; elimina ambiguidade reservada × variável.
- *Parênteses na AST?* Não há nó; só guiam parsing.
- *`cessai` fora de laço?* Erro semântico por contador de profundidade; `oficio`
  aninhado zera a base (não herda laço externo). Vale em `em_cada` também.
- *Por que `,` virou token?* Chamadas `$f(a, b)` precisam de separador; `,`
  já estava em Σ mas gerava erro léxico — agora emite `COMMA`.
- *Escrita em variável externa dentro de `oficio`?* Barrada (só leitura):
  Python criaria local silencioso, divergindo da semântica Holy.
- *`retorne` sem valor?* Permitido (saída antecipada → `return` nu);
  com valor, tipo deve casar com o declarado (`int→float` promove).
- *Abertos (open decisions)?* `peregrine` header C-style reaproveitando
  `Atribuicao+amém`; `em_cada` restrito a `salmo`; `versículo=float`;
  comentário `glosa(...)/|> <|`; divisão `//` documentada.
