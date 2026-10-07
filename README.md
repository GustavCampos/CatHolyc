![CatHolyc Logo](images/LOGO.jpg)

# 1 Escopo e Vocabulário da Linguagem

## 1. Tipos primitivos

| C | Linguagem | Significado |
|---|---|---|
| `int` | `capítulo` | Número inteiro |
| `float` / `double` | `versículo` | Número real |
| `char*` | `salmo` | Texto |
| `bool` | `dogma` | Valor lógico |

## 2. Declarações

| C | Linguagem | Função |
|---|---|---|
| `const` | `mandamento` | Declara uma constante |
| Variável | `preceito` | Declara uma variável |

## 3. Atribuição

| C | Linguagem |
|---|---|
| `=` | `seja` |

## 4. Expressões aritméticas

| C | Linguagem | Significado |
|---|---|---|
| `+` | `somado_a` | Soma |
| `-` | `privado_de` | Subtração |
| `*` | `multiplicado_por` | Multiplicação |
| `/` | `partilhado_entre` | Divisão |
| `%` | `dízimo_de` | Resto da divisão |

## 5. Operadores relacionais

| C | Linguagem | Significado |
|---|---|---|
| `>` | `exaltado_sobre` | Maior que |
| `<` | `submisso_a` | Menor que |
| `>=` | `não_abaixo_de` | Maior ou igual |
| `<=` | `não_acima_de` | Menor ou igual |
| `==` | `conforme_a` | Igual |
| `!=` | `dissonante_de` | Diferente |

## 6. Operadores lógicos

| C | Linguagem | Significado |
|---|---|---|
| `&&` | `em_comunhão_com` | E lógico |
| `\|\|` | `ou_porventura` | OU lógico |
| `!` | `não_seja` | Negação |

## 7. Estruturas de decisão

| C | Linguagem |
|---|---|
| `if` | `caso` |
| `else if` | `doutra_sorte_caso` |
| `else` | `doutra_sorte` |

## 8. Estruturas de repetição

| C | Linguagem |
|---|---|
| `while` | `enquanto` |
| `for` | `peregrine` |
| `for each` | `em_cada` |

## 9. Comandos de entrada e saída

| C | Linguagem | Função |
|---|---|---|
| `printf` | `proclame` | Saída de dados |
| `scanf` | `confesse` | Entrada de dados |

## 10. Valores booleanos

| C | Linguagem |
|---|---|
| `true` | `verdade` |
| `false` | `falsidade` |

## 11. Delimitação

| Elemento | Linguagem | Função |
|---|---|---|
| Início do programa | `em_nome_do_pai` | Inicia o programa |
| Fim de comando | `amém` | Finaliza uma instrução |
| Fim de bloco | `amém_senhor` | Finaliza um bloco |
| Fim do programa | `assim_seja_em_seu_nome_amem` | Finaliza o programa |

## 12. Exemplo

```text
em_nome_do_pai

mandamento capítulo maioridade seja 18 amém

preceito capítulo idade seja 21 amém
preceito dogma estudante seja verdade amém

caso idade exaltado_sobre maioridade em_comunhão_com estudante conforme_a verdade
    proclame "É maior de idade e estudante." amém
doutra_sorte
    proclame "A condição não foi satisfeita." amém
amém_senhor

assim_seja_em_seu_nome_amem
```
---

# 2. Especificação Léxica

Esta seção especifica formalmente os elementos reconhecidos pelo analisador léxico da linguagem, relacionando a implementação aos conceitos de **alfabeto**, **palavra** e **linguagem regular** apresentados em MENEZES (2011). Segundo essa fundamentação teórica, um alfabeto (Σ) é um conjunto finito e não vazio de símbolos; uma palavra (ou cadeia) é uma sequência finita de símbolos de Σ, pertencente a Σ*; e uma linguagem é um subconjunto de Σ*, aqui definida por expressões regulares — cada categoria de *token* corresponde a uma linguagem regular reconhecida por um autômato finito determinístico (AFD) que compõe o analisador léxico.

## 2.1 Alfabeto (Σ)

O alfabeto da linguagem é definido como a união dos seguintes subconjuntos de símbolos:

Σ = Σ_letras ∪ Σ_dígitos ∪ Σ_especiais ∪ Σ_brancos

| Subconjunto | Símbolos | Uso |
|---|---|---|
| Σ_letras | `a`–`z`, `A`–`Z` | formação de palavras reservadas e identificadores |
| Σ_dígitos | `0`–`9` | formação de literais numéricos e parte de identificadores |
| Σ_especiais | `_` `+` `-` `*` `/` `%` `=` `>` `<` `!` `&` `|` `(` `)` `"` `.` `,` | operadores, delimitadores e pontuação |
| Σ_brancos | espaço (` `), tabulação (`\t`), quebra de linha (`\n`, `\r\n`) | separadores, descartados na formação de tokens |

Observação: o caractere `_` (sublinhado) integra a classe de formação de identificadores e palavras reservadas, já que todo o vocabulário da linguagem é construído por composição de palavras unidas por `_` (ex.: `doutra_sorte_caso`, `amém_senhor`). Por simplificação notacional, letras acentuadas do português (à, é, í, ó, ú, ã, õ, â, ê) também integram Σ_letras, pois ocorrem em palavras reservadas como `em_comunhão_com` e `não_abaixo_de`.

Toda cadeia de entrada é, portanto, um elemento de Σ*, e cada categoria de token definida abaixo é uma linguagem regular Lᵢ ⊆ Σ*. O analisador léxico reconhece a linguagem L = L₁ ∪ L₂ ∪ ... ∪ Lₙ (união das linguagens de todos os tokens) e classifica cada palavra reconhecida (lexema) na categoria correspondente.

## 2.2 Tabela de Tokens

| Categoria | Expressão Regular / Padrão | Exemplo de Lexema | Descrição |
|---|---|---|---|
| PALAVRA_RESERVADA | ver Tabela 2.3 (conjunto fechado de literais) | `caso`, `enquanto`, `capítulo` | Palavras com significado fixo na linguagem; têm prioridade sobre IDENTIFICADOR quando o lexema coincide |
| IDENTIFICADOR | `[a-zA-Zà-ú_][a-zA-Zà-ú0-9_]*` | `idade`, `maioridade`, `estudante` | Nome de variável ou constante definido pelo usuário, desde que não coincida com uma palavra reservada |
| NUM_INTEIRO | `[0-9]+` | `18`, `21` | Literal do tipo `capítulo` (int) |
| NUM_REAL | `[0-9]+\.[0-9]+` | `3.14`, `0.5` | Literal do tipo `versículo` (float/double) |
| LITERAL_TEXTO | `"([^"\n\\]|\\.)*"` | `"É maior de idade e estudante."` | Literal do tipo `salmo` (char*); sequência entre aspas duplas, sem quebra de linha, com suporte a escape (`\"`, `\\`) |
| LITERAL_BOOLEANO | `verdade|falsidade` | `verdade` | Literal do tipo `dogma` (bool); tratado como palavra reservada |
| OP_ATRIBUICAO | `seja` | `seja` | Operador de atribuição (`=`) |
| OP_ARITMETICO | `somado_a|privado_de|multiplicado_por|partilhado_entre|dízimo_de` | `somado_a` | Operadores `+ - * / %` |
| OP_RELACIONAL | `exaltado_sobre|submisso_a|não_abaixo_de|não_acima_de|conforme_a|dissonante_de` | `conforme_a` | Operadores `> < >= <= == !=` |
| OP_LOGICO | `em_comunhão_com|ou_porventura|não_seja` | `em_comunhão_com` | Operadores `&& || !` |
| DELIM_INICIO_PROG | `em_nome_do_pai` | `em_nome_do_pai` | Marca o início do programa |
| DELIM_FIM_CMD | `amém` | `amém` | Marca o fim de um comando (`;`) |
| DELIM_FIM_BLOCO | `amém_senhor` | `amém_senhor` | Marca o fim de um bloco (`}`) |
| DELIM_FIM_PROG | `assim_seja_em_seu_nome_amem` | `assim_seja_em_seu_nome_amem` | Marca o fim do programa |
| BRANCO | `[ \t]+` | — | Espaço/tabulação; descartado, não gera token |
| QUEBRA_LINHA | `\r\n|\n` | — | Incrementa o contador de linhas; descartada, não gera token |
| COMENTÁRIO | `glosa\(([^)]*)\)` ou `\|>.*?<\|` (bloco, DOTALL não-guloso) | `glosa(explica o versículo)`, `\|> anota <\|` | Comentário de linha/bloco; descartado, não gera token; `\|>` sem `<\|` ⇒ erro léxico |
| ERRO_LEXICO | qualquer cadeia de Σ* não reconhecida pelas regras acima | `#`, `@`, `12.`, `"texto não fechado` | Símbolo ou lexema inválido; gera mensagem de erro (ver 2.6) |

## 2.3 Classes de Palavras da Linguagem

**a) Palavras reservadas** — conjunto finito e fechado, com prioridade de reconhecimento sobre identificadores:

`capítulo`, `versículo`, `salmo`, `dogma`, `mandamento`, `preceito`, `seja`, `somado_a`, `privado_de`, `multiplicado_por`, `partilhado_entre`, `dízimo_de`, `exaltado_sobre`, `submisso_a`, `não_abaixo_de`, `não_acima_de`, `conforme_a`, `dissonante_de`, `em_comunhão_com`, `ou_porventura`, `não_seja`, `caso`, `doutra_sorte_caso`, `doutra_sorte`, `enquanto`, `peregrine`, `em_cada`, `proclame`, `confesse`, `verdade`, `falsidade`, `em_nome_do_pai`, `amém`, `amém_senhor`, `assim_seja_em_seu_nome_amem`

**b) Identificadores** — L_id = { w ∈ Σ* | w = letra (letra | dígito | `_`)*, w ∉ palavras_reservadas }. Ex.: `idade`, `maioridade`, `estudante`.

**c) Literais numéricos**
- Inteiro (`capítulo`): L_int = `[0-9]+`
- Real (`versículo`): L_real = `[0-9]+\.[0-9]+`

**d) Literais de texto** (`salmo`): L_texto = `"` (Σ − {`"`, quebra de linha})\* `"`, com tratamento de escape para aspas internas.

**e) Operadores**: atribuição, aritméticos, relacionais e lógicos, conforme Tabela 2.2 — todos representados por palavras-chave (não por símbolos soltos), o que os torna, sintaticamente, um subconjunto das palavras reservadas.

**f) Delimitadores**: `em_nome_do_pai` (início de programa), `amém` (fim de comando), `amém_senhor` (fim de bloco), `assim_seja_em_seu_nome_amem` (fim de programa). Delimitadores adicionais de agrupamento, como `(` e `)`, podem ser incorporados a Σ_especiais caso o grupo opte por permitir expressões entre parênteses.

## 2.4 Espaços em Branco, Quebras de Linha e Comentários

Espaços (` `), tabulações (`\t`) e quebras de linha (`\n` ou `\r\n`) pertencem à linguagem regular `[ \t\r\n]+`, mas **não geram token**: são consumidos e descartados pelo analisador léxico entre o reconhecimento de dois lexemas. A quebra de linha, entretanto, incrementa um contador interno de linha, usado para localizar erros léxicos e sintáticos.

O vocabulário original da linguagem não define uma sintaxe de comentários. Como o item é opcional, propõe-se, para fins de formalização, duas convenções equivalentes, ambas descartadas sem gerar token, de forma análoga aos espaços em branco: (1) comentários delimitados pela palavra-chave `glosa` seguida de conteúdo entre parênteses — `glosa(comentário)` — reconhecidos por `glosa\([^)]*\)`, sem aninhamento; (2) comentários de bloco delimitados por `|>` (abertura) e `<|` (fechamento) — `|> comentário <|` — reconhecidos por `\|>.*?<\|` (DOTALL, não-guloso, primeira ocorrência de `<|` fecha), sem aninhamento em V1, podendo conter quebras de linha (contador de linha/coluna atualizado). `|>` sem `<|` de fechamento ⇒ erro léxico com panic-mode. `glosa` só inicia comentário se seguida imediatamente de `(`; caso contrário vale maximal munch como identificador.

## 2.5 Estratégia de Maior Casamento (Longest Match)

O analisador léxico utiliza a estratégia de **maximal munch** (maior casamento): ao iniciar o reconhecimento de um lexema formado por letras/dígitos/`_`, o autômato continua consumindo caracteres de Σ_letras ∪ Σ_dígitos ∪ {`_`} enquanto o próximo caractere mantiver uma transição válida, parando somente diante de um separador (branco, quebra de linha ou símbolo de Σ_especiais que não pertença ao próprio lexema). Somente após atingir esse ponto de parada o lexema completo é comparado à tabela de palavras reservadas.

Essa estratégia é indispensável porque, nesta linguagem, diversas palavras reservadas compartilham prefixo — o análogo direto do clássico problema `=` vs. `==` da linguagem C:

- `amém` (fim de comando) é prefixo de `amém_senhor` (fim de bloco). Sem maior casamento, o lexer reconheceria `amém` e pararia antes de `_senhor`, produzindo um token incorreto.
- `doutra_sorte` (`else`) é prefixo de `doutra_sorte_caso` (`else if`). O mesmo problema ocorreria: sem consumir a cadeia inteira, `doutra_sorte_caso` seria erroneamente fragmentado em `doutra_sorte` + identificador inválido `caso` (que, por sua vez, colidiria com a palavra reservada `caso`, do `if`).

Por isso, o AFD correspondente permanece em estado de aceitação "provisória" ao reconhecer `amém` ou `doutra_sorte`, mas só finaliza o lexema quando o caractere seguinte deixa de pertencer a Σ_letras ∪ Σ_dígitos ∪ {`_`}; a categorização final (palavra reservada vs. identificador, e qual palavra reservada) é decidida por *lookup* na tabela de símbolos apenas sobre a cadeia máxima obtida.

O mesmo princípio aplica-se, por completude, a literais numéricos: `18` e `18.5` compartilham prefixo `18`, e o lexer só decide entre NUM_INTEIRO e NUM_REAL após verificar se o caractere seguinte é `.` seguido de dígito.

## 2.6 Tratamento de Erros Léxicos

Quando o analisador léxico encontra um caractere que não inicia nenhuma transição válida em Σ (por exemplo `#`, `@`, `$`), ou uma cadeia que inicia um padrão válido mas não o completa corretamente (por exemplo um literal de texto sem aspas de fechamento, ou um número como `12.` sem dígitos após o ponto), ele reporta um **erro léxico** e interrompe o reconhecimento daquele lexema, emitindo mensagem no formato:

```
Erro léxico: símbolo ou lexema inválido '<lexema>' na linha <N>
```

onde `<N>` é o número de linha corrente, obtido pelo contador incrementado a cada quebra de linha consumida (seção 2.4). Após reportar o erro, o analisador aplica recuperação em modo pânico (*panic mode*): descarta o caractere ou lexema inválido e retoma o reconhecimento a partir do próximo caractere, permitindo que outros erros na mesma entrada sejam identificados em uma única execução, em vez de interromper o processo no primeiro erro encontrado.

---

# 3. Especificação Sintática — GLC

A sintaxe da linguagem é especificada pela Gramática Livre de Contexto **G = (V, T, P, S)**, apresentada em notação **EBNF**. As produções foram construídas de forma a **evitar recursão à esquerda**, permitindo implementação direta por um *parser* preditivo de descida recursiva (LL(1)), e a **preservar a precedência** entre operadores lógicos, relacionais, aditivos e multiplicativos por meio do encadeamento hierárquico de não terminais de expressão.

## 3.1 Definição formal de G = (V, T, P, S)

**V (não terminais):**

```
V = { Programa, Bloco, Comando, DeclConst, DeclVar, Tipo,
      Atribuicao, ComandoSe, ComandoEnquanto, ComandoPara, ComandoParaCada,
      ComandoSaida, ComandoEntrada,
      ExpressaoOu, ExpressaoE, ExpressaoNao, ExpressaoRel, OpRel,
      ExpressaoAdd, OpAdd, ExpressaoMul, OpMul, Fator }
```

**T (terminais)** — correspondem exatamente aos tokens definidos na Especificação Léxica (seção 2):

```
T = { em_nome_do_pai, assim_seja_em_seu_nome_amem,
      mandamento, preceito, capítulo, versículo, salmo, dogma,
      seja, amém, amém_senhor,
      caso, doutra_sorte_caso, doutra_sorte, enquanto, peregrine, em_cada,
      proclame, confesse, verdade, falsidade,
      somado_a, privado_de, multiplicado_por, partilhado_entre, dízimo_de,
      exaltado_sobre, submisso_a, não_abaixo_de, não_acima_de, conforme_a, dissonante_de,
      em_comunhão_com, ou_porventura, não_seja,
      "(", ")",
      IDENT, NUM_INT, NUM_REAL, TEXTO }
```

`IDENT`, `NUM_INT`, `NUM_REAL` e `TEXTO` são os terminais “lexicais” definidos por expressão regular na seção 2 (categorias IDENTIFICADOR, NUM_INTEIRO, NUM_REAL e LITERAL_TEXTO), tratados aqui como átomos indivisíveis, já resolvidos pelo analisador léxico.

**S (símbolo inicial):** `S = Programa`

**P (produções):** apresentadas a seguir, organizadas por bloco funcional.

## 3.2 Estrutura do Programa

```
Programa ::= "em_nome_do_pai" Bloco "assim_seja_em_seu_nome_amem"

Bloco    ::= { Comando }

Comando  ::= DeclConst
           | DeclVar
           | Atribuicao
           | ComandoSe
           | ComandoEnquanto
           | ComandoPara
           | ComandoParaCada
           | ComandoSaida
           | ComandoEntrada
```

`Bloco` é definido por repetição (`{ }`), e não por recursão à esquerda (`Bloco ::= Bloco Comando | ε`), justamente para manter a gramática compatível com descida recursiva: o parser implementa `Bloco` como um laço que consome `Comando` enquanto o próximo símbolo pertencer ao conjunto FIRST(Comando).

## 3.3 Declarações, Tipos e Atribuição

```
Tipo       ::= "capítulo" | "versículo" | "salmo" | "dogma"

DeclConst  ::= "mandamento" Tipo IDENT "seja" ExpressaoOu "amém"

DeclVar    ::= "preceito" Tipo IDENT [ "seja" ExpressaoOu ] "amém"

Atribuicao ::= IDENT "seja" ExpressaoOu "amém"
```

`DeclConst` exige inicialização obrigatória (coerente com a semântica de constante); `DeclVar` permite inicialização opcional, indicada por colchetes `[ ]` (0 ou 1 ocorrência).

## 3.4 Estruturas de Decisão

```
ComandoSe ::= "caso" ExpressaoOu Bloco
              { "doutra_sorte_caso" ExpressaoOu Bloco }
              [ "doutra_sorte" Bloco ]
              "amém_senhor"
```

Essa produção reflete diretamente o exemplo de referência do vocabulário: a condição do `caso` (if) é seguida de um `Bloco` sem marcador próprio de abertura (o próprio primeiro `Comando` já delimita o início); zero ou mais ramos `doutra_sorte_caso` (else if) podem ocorrer, cada um com sua condição e bloco; um ramo final opcional `doutra_sorte` (else), sem condição; e a estrutura inteira — incluindo todos os ramos — é fechada por um único `amém_senhor`, exatamente como no exemplo:

```
caso idade exaltado_sobre maioridade em_comunhão_com estudante conforme_a verdade
    proclame "É maior de idade e estudante." amém
doutra_sorte
    proclame "A condição não foi satisfeita." amém
amém_senhor
```

## 3.5 Estruturas de Repetição

```
ComandoEnquanto ::= "enquanto" ExpressaoOu Bloco "amém_senhor"

ComandoPara     ::= "peregrine" Atribuicao ExpressaoOu "amém" Atribuicao Bloco "amém_senhor"

ComandoParaCada ::= "em_cada" IDENT IDENT Bloco "amém_senhor"
```

Observação de projeto: o vocabulário fornecido define apenas o mapeamento lexical de `for` → `peregrine` e `for each` → `em_cada`, sem especificar a sintaxe completa dessas estruturas. O grupo optou por:

- em `ComandoPara`, reaproveitar `Atribuicao` (que já termina em `amém`) para a inicialização e o incremento, e um `ExpressaoOu` terminado por `amém` para a condição — mantendo o uso de `amém` como separador de cláusulas, análogo ao `;` do `for` em C (`peregrine <inicialização> <condição> amém <incremento> <bloco> amém_senhor`);
- em `ComandoParaCada`, dois identificadores consecutivos representam, respectivamente, a variável de iteração e a coleção percorrida (equivalente a um `for each` implícito, sem uma palavra reservada para “em”).

Essas decisões devem ser confirmadas/ajustadas pelo grupo conforme a implementação real do parser; a estrutura de `ComandoSe`/`ComandoEnquanto`, baseada diretamente no exemplo do enunciado, é a que possui maior grau de certeza.

## 3.6 Comandos de Entrada e Saída

```
ComandoSaida  ::= "proclame" ExpressaoOu "amém"

ComandoEntrada ::= "confesse" IDENT "amém"
```

## 3.7 Expressões — Precedência e Ausência de Recursão à Esquerda

As expressões são organizadas em uma cadeia de não terminais em ordem crescente de precedência (do nível mais baixo, `ExpressaoOu`, ao mais alto, `Fator`), técnica padrão para expressar precedência sem ambiguidade em GLC:

```
ExpressaoOu  ::= ExpressaoE { "ou_porventura" ExpressaoE }

ExpressaoE   ::= ExpressaoNao { "em_comunhão_com" ExpressaoNao }

ExpressaoNao ::= [ "não_seja" ] ExpressaoRel

ExpressaoRel ::= ExpressaoAdd [ OpRel ExpressaoAdd ]
OpRel        ::= "exaltado_sobre" | "submisso_a"
                | "não_abaixo_de" | "não_acima_de"
                | "conforme_a"    | "dissonante_de"

ExpressaoAdd ::= ExpressaoMul { OpAdd ExpressaoMul }
OpAdd        ::= "somado_a" | "privado_de"

ExpressaoMul ::= Fator { OpMul Fator }
OpMul        ::= "multiplicado_por" | "partilhado_entre" | "dízimo_de"

Fator ::= IDENT
        | NUM_INT
        | NUM_REAL
        | TEXTO
        | "verdade"
        | "falsidade"
        | "(" ExpressaoOu ")"
        | "privado_de" Fator
```

Pontos importantes desta subseção:

1. **Não ambiguidade e precedência.** Cada nível de operador (`ou_porventura` < `em_comunhão_com` < `não_seja` < relacionais < aditivos < multiplicativos, do menor para o maior) só pode combinar operandos do nível imediatamente superior, o que fixa uma única árvore de derivação possível para qualquer expressão válida — eliminando a ambiguidade clássica de gramáticas do tipo `E ::= E op E`. Por exemplo, `2 somado_a 3 multiplicado_por 4` é necessariamente analisado como `2 somado_a (3 multiplicado_por 4)`, pois `ExpressaoMul` (multiplicação) só é alcançada a partir de `ExpressaoAdd` (soma) em um nível mais interno da derivação.
2. **Ausência de recursão à esquerda.** Todas as repetições (`{ }`) substituem produções que, em BNF clássico, seriam recursivas à esquerda (ex.: em vez de `ExpressaoAdd ::= ExpressaoAdd OpAdd ExpressaoMul | ExpressaoMul`, usa-se `ExpressaoAdd ::= ExpressaoMul { OpAdd ExpressaoMul }`). Isso é o que permite implementação direta por descida recursiva sem entrar em looping infinito, já que cada não terminal, ao ser invocado, consome ao menos um símbolo antes de qualquer nova chamada recursiva à esquerda.
3. **Agrupamento com parênteses.** A alternativa `"(" ExpressaoOu ")"` em `Fator` permite reiniciar a precedência dentro de um grupo, possibilitando expressões como `(idade somado_a 1) multiplicado_por 2`.
4. **Extensão de sinal negativo.** A alternativa `"privado_de" Fator` em `Fator` (reutilizando a palavra reservada de subtração como operador unário de negação, ex.: `privado_de 5`) não decorre diretamente do vocabulário fornecido, mas foi incluída para permitir literais numéricos negativos; pode ser removida caso o grupo não a implemente.

## 3.8 Verificação com o Programa de Exemplo

A gramática acima deriva integralmente o programa de exemplo do vocabulário (`em_nome_do_pai ... assim_seja_em_seu_nome_amem`), incluindo:

- duas declarações (`mandamento`/`DeclConst` e `preceito`/`DeclVar`, esta última instanciada duas vezes);
- uma condição composta com um operador relacional (`exaltado_sobre`), um lógico (`em_comunhão_com`) e outro relacional (`conforme_a`), corretamente reduzida via `ExpressaoOu → ExpressaoE → ExpressaoNao ("em_comunhão_com") ExpressaoNao`;
- um `ComandoSe` com ramo `doutra_sorte` e fechamento único por `amém_senhor`;
- dois `ComandoSaida` (`proclame ... amém`) reduzidos a partir de `TEXTO` via a cadeia completa de não terminais de expressão.

Isso confirma que **G corresponde efetivamente à linguagem implementada**, conforme exigido no escopo mínimo.

---

# 4. Analisador Sintático e AST

O parser implementado é um **analisador preditivo por descida recursiva (LL(1))**, escolha coerente com a gramática da seção 3, que foi deliberadamente escrita sem recursão à esquerda e com um único símbolo de *lookahead* suficiente para decidir, em cada ponto, qual produção aplicar. Cada não terminal de G dá origem a uma função de análise homônima, que consome tokens produzidos pelo analisador léxico (seção 2) e devolve um nó da Árvore Sintática Abstrata (AST) — não uma árvore de derivação completa (*parse tree*) com todos os símbolos intermediários da gramática, mas já a representação reduzida usada na etapa de geração de código. Por não se utilizar uma ferramenta geradora (ANTLR, JFlex/CUP, Lex/Yacc), não há uma árvore de derivação bruta a ser convertida à parte: a AST é construída diretamente durante o parsing, um nó por vez.

## 4.1 Estratégia Geral

- O parser mantém um cursor sobre a lista de tokens (cada token com `categoria`, `lexema` e `linha`, produzidos pelo léxico).
- Duas operações básicas: `atual()` (observa o token corrente sem consumi-lo) e `consome(categoriaEsperada)` (verifica se o token atual pertence à categoria esperada; se sim, avança o cursor e o retorna; se não, dispara erro sintático — seção 4.4).
- Cada função de análise corresponde a exatamente um não terminal de V (seção 3.1) e decide qual produção seguir observando `atual()` — nunca é necessário retroceder (*backtracking*), pois a gramática é LL(1): o primeiro token de cada alternativa é suficiente para escolhê-la (ex.: `mandamento` só pode iniciar `DeclConst`; `preceito` só `DeclVar`; `caso` só `ComandoSe`).

## 4.2 Mapeamento Produção → Estrutura da Linguagem → Nó de AST

| Não terminal (G) | Estrutura reconhecida | Nó de AST produzido |
|---|---|---|
| `Programa` | programa completo (`em_nome_do_pai ... assim_seja_em_seu_nome_amem`) | `Programa { comandos: [Comando] }` |
| `Bloco` | sequência de comandos | lista de nós `Comando` (não gera nó próprio; é achatado no pai) |
| `DeclConst` | `mandamento ...` | `DeclConst { tipo, nome, valor }` |
| `DeclVar` | `preceito ...` | `DeclVar { tipo, nome, valor? }` |
| `Atribuicao` | `IDENT seja ... amém` | `Atribuicao { nome, valor }` |
| `ComandoSe` | `caso ... doutra_sorte_caso ... doutra_sorte ... amém_senhor` | `Se { condicao, entao, senaoSe: [(condicao, bloco)], senao? }` |
| `ComandoEnquanto` | `enquanto ... amém_senhor` | `Enquanto { condicao, corpo }` |
| `ComandoPara` | `peregrine ... amém_senhor` | `Para { init, condicao, incremento, corpo }` |
| `ComandoParaCada` | `em_cada ... amém_senhor` | `ParaCada { variavel, colecao, corpo }` |
| `ComandoSaida` | `proclame ... amém` | `Saida { expressao }` |
| `ComandoEntrada` | `confesse ... amém` | `Entrada { variavel }` |
| `ExpressaoOu` … `ExpressaoMul` | operadores lógicos/relacionais/aritméticos | `OperacaoBinaria { operador, esquerda, direita }` (um nó por ocorrência do operador; ausência do operador → apenas o operando do nível superior é retornado, sem criar nó) |
| `ExpressaoNao` (com `não_seja`) | negação lógica | `OperacaoUnaria { operador: "não_seja", operando }` |
| `Fator` (`"(" ExpressaoOu ")"`) | agrupamento | não gera nó próprio — devolve diretamente o nó de `ExpressaoOu` interno (parênteses não aparecem na AST, só influenciam a árvore durante o parsing) |
| `Fator` (`IDENT`) | uso de identificador | `Identificador { nome }` |
| `Fator` (`NUM_INT`/`NUM_REAL`/`TEXTO`/`verdade`/`falsidade`) | literal | `Literal { tipo, valor }` |

Este mapeamento é o que o grupo deve estar apto a apresentar/defender: para cada função `parseX()`, indicar qual produção de P ela implementa e qual nó de AST ela devolve.

## 4.3 Representação da AST

A seguir, os tipos de nó em notação independente de linguagem (equivalente a *interfaces*/`structs`; deve ser adaptada à linguagem de implementação escolhida pelo grupo):

```
Programa       { comandos: Comando[] }

DeclConst      { tipo: Tipo, nome: string, valor: Expressao }
DeclVar        { tipo: Tipo, nome: string, valor: Expressao | null }
Atribuicao     { nome: string, valor: Expressao }

Se             { condicao: Expressao, entao: Comando[],
                 senaoSe: { condicao: Expressao, bloco: Comando[] }[],
                 senao: Comando[] | null }
Enquanto       { condicao: Expressao, corpo: Comando[] }
Para           { init: Atribuicao, condicao: Expressao,
                 incremento: Atribuicao, corpo: Comando[] }
ParaCada       { variavel: string, colecao: string, corpo: Comando[] }

Saida          { expressao: Expressao }
Entrada        { variavel: string }

// nós de expressão (Expressao = uma das alternativas abaixo)
OperacaoBinaria { operador: string, esquerda: Expressao, direita: Expressao }
OperacaoUnaria  { operador: string, operando: Expressao }
Identificador   { nome: string }
Literal         { tipo: "int"|"float"|"texto"|"bool", valor: any }
```

Todo nó carrega também a **linha** do token que o originou (herdada do token léxico), usada tanto para diagnósticos de erro quanto, posteriormente, para geração de código com rastreabilidade.

## 4.4 Construção da AST — Exemplo

Para a condição `idade exaltado_sobre maioridade em_comunhão_com estudante conforme_a verdade` (seção 3.4), o parser produz:

```
OperacaoBinaria {
  operador: "em_comunhão_com",
  esquerda: OperacaoBinaria { operador: "exaltado_sobre",
                               esquerda: Identificador{"idade"},
                               direita:  Identificador{"maioridade"} },
  direita:  OperacaoBinaria { operador: "conforme_a",
                               esquerda: Identificador{"estudante"},
                               direita:  Literal{tipo:"bool", valor:true} }
}
```

Note que a estrutura reflete exatamente a precedência definida em 3.7: `em_comunhão_com` (nível `ExpressaoE`) fica na raiz, com as duas comparações relacionais (nível mais interno) como filhas — sem qualquer ambiguidade, e sem que o parser precise consultar tabela de precedência em tempo de execução, já que a hierarquia está embutida na própria cadeia de chamadas `parseExpressaoOu → parseExpressaoE → ... → parseFator`.

## 4.5 Tratamento de Erros Sintáticos~

Sempre que `consome(categoriaEsperada)` encontra um token de categoria diferente da esperada, o parser **interrompe imediatamente o processamento** (sem tentativa de recuperação, ao contrário do léxico) e reporta:

```
Erro sintático: linha <N> — token encontrado '<lexema>' (<categoria>), esperado '<elemento esperado>'
```

Exemplos:

- Entrada `preceito capítulo idade 21 amém` (faltando `seja`): `Erro sintático: linha 3 — token encontrado NUM_INT '21', esperado 'seja'`.
- Entrada `caso idade exaltado_sobre maioridade` sem bloco nem `amém_senhor` antes do fim do arquivo: `Erro sintático: linha 5 — token encontrado EOF, esperado um comando ou 'amém_senhor'`.
- Entrada com parêntese não fechado `(idade somado_a 1`: `Erro sintático: linha 4 — token encontrado 'amém', esperado ')'`.

O `<elemento esperado>` deve ser preenchido com o terminal (ou conjunto FIRST do não terminal, quando a produção tiver alternativas) previsto pela gramática no ponto da falha — informação que a própria função `parseX()` já possui, pois é ela quem decide qual `consome(...)` chamar.