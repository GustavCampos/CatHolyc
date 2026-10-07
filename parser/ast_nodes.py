from dataclasses import dataclass


@dataclass
class Programa:
    comandos: list
    linha: int = 1


@dataclass
class DeclConst:
    tipo: str
    nome: str
    valor: object
    linha: int


@dataclass
class DeclVar:
    tipo: str
    nome: str
    valor: object | None
    linha: int


@dataclass
class Atribuicao:
    nome: str
    valor: object
    linha: int


@dataclass
class RamoSenaoSe:
    condicao: object
    bloco: list
    linha: int


@dataclass
class Se:
    condicao: object
    entao: list
    senaoSe: list
    senao: list | None
    linha: int


@dataclass
class Enquanto:
    condicao: object
    corpo: list
    linha: int


@dataclass
class Para:
    init: object
    condicao: object
    incremento: object
    corpo: list
    linha: int


@dataclass
class ParaCada:
    variavel: str
    colecao: str
    corpo: list
    linha: int


@dataclass
class Saida:
    expressao: object
    linha: int


@dataclass
class Entrada:
    variavel: str
    linha: int


@dataclass
class OperacaoBinaria:
    operador: str
    esquerda: object
    direita: object
    linha: int


@dataclass
class OperacaoUnaria:
    operador: str
    operando: object
    linha: int


@dataclass
class Identificador:
    nome: str
    linha: int


@dataclass
class Literal:
    tipo: str
    valor: object
    linha: int
