"""
Calculadora com interface gráfica
INE5201 - Introdução à Ciência da Computação com Python - UFSC
Tarefa 02

Dupla:
    Matheus da Silva Farani (24202994)
    Paulo Ricardo Eliel Mendes Peres dos Santos (24100434)

Como usar:
    Clique nos botões ou use o teclado (números, + - * / . Enter,
    Backspace e Esc). Clique em um item do histórico para reaproveitar
    o resultado.
"""

from decimal import Decimal, ROUND_HALF_UP

import FreeSimpleGUI as sg

# ============================== Constantes ==============================

OPERADORES = '+-*/'
MAX_CARACTERES = 18             # limite do display (evita overflow)
MAX_HISTORICO = 10              # quantos cálculos o histórico guarda
LIMITE_RESULTADO = Decimal('1e15')         # acima disso: número muito grande
CASAS_DECIMAIS = Decimal('0.0000000001')   # resultados com até 10 casas

# Cores
COR_DISPLAY = '#1E1E1E'
COR_TEXTO_DISPLAY = '#FFFFFF'
COR_ERRO = '#FF6B6B'
COR_NUMERO = ('#FFFFFF', '#3A3A3A')     # (texto, fundo)
COR_OPERADOR = ('#FFFFFF', '#F39C12')
COR_LIMPAR = ('#FFFFFF', '#C0392B')
COR_IGUAL = ('#FFFFFF', '#27AE60')

# Mensagens de erro
ERRO_DIVISAO = 'Erro: Divisão por zero'
ERRO_EXPRESSAO = 'Erro: Expressão inválida'
ERRO_GRANDE = 'Erro: Número muito grande'


# ============================== Entrada no display ==============================

def numero_atual(expressao):
    """Retorna o número que está sendo digitado (depois do último operador).

    O '-' no início da expressão é sinal de número negativo, não operador,
    por isso a busca começa na posição 1.
    """
    inicio = 0
    for i in range(1, len(expressao)):
        if expressao[i] in OPERADORES:
            inicio = i + 1
    return expressao[inicio:].lstrip('-')


def adicionar_digito(expressao, digito):
    """Acrescenta um dígito, trocando um '0' sozinho (evita '007')."""
    if numero_atual(expressao) == '0':
        return expressao[:-1] + digito
    return expressao + digito


def adicionar_ponto(expressao):
    """Acrescenta o ponto decimal, no máximo um por número."""
    atual = numero_atual(expressao)
    if '.' in atual:
        return expressao
    if atual == '':
        return expressao + '0.'
    return expressao + '.'


def adicionar_operador(expressao, operador):
    """Acrescenta um operador validando a entrada.

    - No início só é aceito '-' (número negativo).
    - Dois operadores seguidos: o novo substitui o anterior.
    """
    if expressao in ('', '-'):
        return '-' if operador == '-' else expressao
    if expressao[-1] in OPERADORES:
        return expressao[:-1] + operador
    return expressao + operador


# ============================== Cálculo ==============================

def separar_tokens(expressao):
    """Transforma '12.5+3*-' em [Decimal('12.5'), '+', Decimal('3'), ...].

    Lança ValueError se a expressão estiver mal formada
    (por exemplo, terminar em operador).
    """
    tokens = []
    numero = ''
    for i, caractere in enumerate(expressao):
        if caractere.isdigit() or caractere == '.':
            numero += caractere
        elif caractere == '-' and i == 0:
            numero = '-'                        # sinal de número negativo
        elif caractere in OPERADORES:
            tokens.append(converter_numero(numero))
            tokens.append(caractere)
            numero = ''
        else:
            raise ValueError(f'Caractere inválido: {caractere}')
    tokens.append(converter_numero(numero))
    return tokens


def converter_numero(texto):
    """Converte o texto em Decimal ou lança ValueError."""
    if texto in ('', '-', '.', '-.'):
        raise ValueError('Número ausente')
    return Decimal(texto)


def formatar_numero(valor):
    """Arredonda para 10 casas e tira os zeros à direita (2.50 -> 2.5)."""
    if abs(valor) >= LIMITE_RESULTADO:
        raise OverflowError('Resultado grande demais para o display')
    valor = valor.quantize(CASAS_DECIMAIS, rounding=ROUND_HALF_UP)
    texto = format(valor.normalize(), 'f')
    return '0' if texto == '-0' else texto


def calcular(expressao):
    """Calcula a expressão respeitando a precedência (* e / antes de + e -).

    Usa Decimal em vez de float para que 0.1 + 0.2 dê 0.3.
    Lança ZeroDivisionError, OverflowError ou ValueError;
    quem chama decide qual mensagem mostrar.
    """
    tokens = separar_tokens(expressao)

    # 1ª passada: resolve * e / da esquerda para a direita
    parcial = [tokens[0]]
    for i in range(1, len(tokens), 2):
        operador, numero = tokens[i], tokens[i + 1]
        if operador == '*':
            parcial[-1] = parcial[-1] * numero
        elif operador == '/':
            if numero == 0:
                raise ZeroDivisionError('Divisão por zero')
            parcial[-1] = parcial[-1] / numero
        else:
            parcial.append(operador)
            parcial.append(numero)

    # 2ª passada: resolve + e -
    resultado = parcial[0]
    for i in range(1, len(parcial), 2):
        operador, numero = parcial[i], parcial[i + 1]
        if operador == '+':
            resultado = resultado + numero
        else:
            resultado = resultado - numero

    return formatar_numero(resultado)


