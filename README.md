![CatHolyc Logo](images/LOGO.jpg)

# Vocabulário da Linguagem

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

# Analisador Léxico

O analisador léxico é responsável por transformar o código-fonte da linguagem em uma sequência de tokens, identificando palavras reservadas, identificadores, literais, operadores e delimitadores. A especificação dos elementos léxicos é baseada nos conceitos de alfabeto, palavras e linguagens regulares apresentados por Menezes (2011).

## Alfabeto da linguagem

O alfabeto $\Sigma$ da linguagem é constituído pelo conjunto finito de símbolos que podem aparecer em um programa válido. Considerando os elementos definidos para a linguagem, o alfabeto pode ser representado por:

$$
\Sigma = L \cup A \cup D \cup E \cup S
$$

onde:

- $L$ representa as letras do alfabeto latino, incluindo as letras acentuadas utilizadas nas palavras reservadas;
- $A$ representa os dígitos de `0` a `9`;
- $D$ representa os delimitadores e símbolos especiais;
- $E$ representa os caracteres utilizados em literais de texto;
- $S$ representa os caracteres de espaço em branco.

As letras utilizadas pela linguagem incluem `a-z`, `A-Z` e os caracteres acentuados presentes nas palavras reservadas, como `á`, `ã`, `é` e `í`. Os dígitos correspondem a `0-9`.

Entre os símbolos especiais utilizados estão:

```text
§  _  (  )  "  \  /
``` 

---

# Tokens da linguagem

Cada unidade léxica reconhecida pelo analisador é associada a um token. A tabela a seguir apresenta os principais tokens da linguagem.# 
| Categoria         | Token               | Padrão                        | Exemplo de lexema             | Descrição                       |
| ----------------- | ------------------- | ----------------------------- | ----------------------------- | ------------------------------- |
| Palavra reservada | `CAPITULO`          | `capítulo`                    | `capítulo`                    | Declaração do tipo inteiro      |
| Palavra reservada | `VERSICULO`         | `versículo`                   | `versículo`                   | Declaração do tipo real         |
| Palavra reservada | `SALMO`             | `salmo`                       | `salmo`                       | Declaração de texto             |
| Palavra reservada | `DOGMA`             | `dogma`                       | `dogma`                       | Declaração de valor booleano    |
| Palavra reservada | `MANDAMENTO`        | `mandamento`                  | `mandamento`                  | Declaração de constante         |
| Palavra reservada | `PRECEITO`          | `preceito`                    | `preceito`                    | Declaração de variável          |
| Palavra reservada | `SEJA`              | `seja`                        | `seja`                        | Operador de atribuição          |
| Palavra reservada | `CASO`              | `caso`                        | `caso`                        | Estrutura condicional `if`      |
| Palavra reservada | `DOUTRA_SORTE_CASO` | `doutra_sorte_caso`           | `doutra_sorte_caso`           | Estrutura condicional `else if` |
| Palavra reservada | `DOUTRA_SORTE`      | `doutra_sorte`                | `doutra_sorte`                | Estrutura condicional `else`    |
| Palavra reservada | `ENQUANTO`          | `enquanto`                    | `enquanto`                    | Estrutura de repetição `while`  |
| Palavra reservada | `PROCLAME`          | `proclame`                    | `proclame`                    | Saída de dados                  |
| Palavra reservada | `CONFESSE`          | `confesse`                    | `confesse`                    | Entrada de dados                |
| Palavra reservada | `VERDADE`           | `verdade`                     | `verdade`                     | Valor booleano verdadeiro       |
| Palavra reservada | `FALSIDADE`         | `falsidade`                   | `falsidade`                   | Valor booleano falso            |
| Palavra reservada | `INICIO_PROGRAMA`   | `em_nome_do_pai`              | `em_nome_do_pai`              | Início do programa              |
| Palavra reservada | `FIM_COMANDO`       | `amém`                        | `amém`                        | Finalização de um comando       |
| Palavra reservada | `FIM_BLOCO`         | `amém_senhor`                 | `amém_senhor`                 | Finalização de um bloco         |
| Palavra reservada | `FIM_PROGRAMA`      | `assim_seja_em_seu_nome_amem` | `assim_seja_em_seu_nome_amem` | Finalização do programa         |

