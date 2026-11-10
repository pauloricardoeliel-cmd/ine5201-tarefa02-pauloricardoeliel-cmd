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


