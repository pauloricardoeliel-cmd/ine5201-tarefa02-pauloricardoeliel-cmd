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


# ============================== Interface gráfica ==============================

def botao(texto, chave, cores):
    return sg.Button(texto, key=chave, size=(5, 2), font=('Helvetica', 16, 'bold'),
                     button_color=cores, expand_x=True, pad=(3, 3))


def criar_layout():
    """Monta a calculadora (à esquerda) e o histórico (à direita)."""
    def numero(digito):
        return botao(digito, digito, COR_NUMERO)

    def operador(simbolo):
        return botao(simbolo, simbolo, COR_OPERADOR)

    teclado = [
        [botao('C', '-LIMPAR-', COR_LIMPAR), botao('←', '-APAGAR-', COR_OPERADOR),
         operador('/')],
        [numero('7'), numero('8'), numero('9'), operador('*')],
        [numero('4'), numero('5'), numero('6'), operador('-')],
        [numero('1'), numero('2'), numero('3'), operador('+')],
        [numero('0'), numero('.'), botao('=', '-IGUAL-', COR_IGUAL)],
    ]

    calculadora = [
        [sg.Text('', key='-CONTA-', size=(26, 1), justification='right',
                 font=('Consolas', 12), background_color=COR_DISPLAY,
                 text_color='#AAAAAA', pad=(3, 0))],
        [sg.Text('0', key='-DISPLAY-', size=(24, 1), justification='right',
                 font=('Consolas', 22, 'bold'), background_color=COR_DISPLAY,
                 text_color=COR_TEXTO_DISPLAY, pad=(3, (0, 6)))],
        [sg.Text('', key='-AVISO-', size=(30, 1), font=('Helvetica', 10),
                 text_color=COR_ERRO)],
        *teclado,
    ]

    historico = [
        [sg.Text('Histórico', font=('Helvetica', 14, 'bold'))],
        [sg.Listbox([], key='-HISTORICO-', size=(28, 14), font=('Consolas', 11),
                    enable_events=True, no_scrollbar=True,
                    background_color=COR_DISPLAY, text_color=COR_TEXTO_DISPLAY)],
                            [sg.Text('Clique em um item para reusar', font=('Helvetica', 9))],
        [sg.Button('Limpar histórico', key='-LIMPAR_HIST-', expand_x=True)],
    ]

    return [[sg.Column(calculadora), sg.VSeparator(),
             sg.Column(historico, vertical_alignment='top')]]


def atualizar_display(window, valor, cor=COR_TEXTO_DISPLAY):
    window['-DISPLAY-'].update(valor if valor else '0', text_color=cor)


def mostrar_aviso(window, texto=''):
    window['-AVISO-'].update(texto)


def tratar_erro(window, estado, mensagem):
    """Mostra o erro no display e prepara para começar uma conta nova."""
    estado['expressao'] = ''
    estado['resultado_na_tela'] = True
    atualizar_display(window, mensagem, COR_ERRO)


def adicionar_ao_historico(window, historico, expressao, resultado):
    """Guarda o cálculo no topo da lista, mantendo só os MAX_HISTORICO últimos."""
    historico.insert(0, f'{expressao} = {resultado}')
    del historico[MAX_HISTORICO:]
    window['-HISTORICO-'].update(historico)


def traduzir_evento(event):
    """Converte clique ou tecla em um símbolo da calculadora, ou None."""
    if not isinstance(event, str):
        return None
    if event in ('-LIMPAR-', '-APAGAR-', '-IGUAL-'):
        return event
    if len(event) == 1:
        if event in '0123456789.' or event in OPERADORES:
            return event
        if event == ',':                # vírgula do teclado numérico
            return '.'
        if event in ('=', '\r'):        # '\r' é o Enter no Windows
            return '-IGUAL-'
        return None
    if event.startswith('Return'):
        return '-IGUAL-'
    if event.startswith('BackSpace'):
        return '-APAGAR-'
    if event.startswith('Escape'):
        return '-LIMPAR-'
    return None


def processar_entrada(window, estado, historico, simbolo):
    """Aplica um botão/tecla ao estado da calculadora."""
    expressao = estado['expressao']
    mostrar_aviso(window)

    if simbolo == '-LIMPAR-':
        estado['expressao'] = ''
        estado['resultado_na_tela'] = False
        window['-CONTA-'].update('')
        atualizar_display(window, '')
        return

    if simbolo == '-APAGAR-':
        if estado['resultado_na_tela']:
            expressao = ''
        estado['expressao'] = expressao[:-1]
        estado['resultado_na_tela'] = False
        atualizar_display(window, estado['expressao'])
        return

    if simbolo == '-IGUAL-':
        tem_operador = any(c in OPERADORES for c in expressao[1:])
        if not expressao or not tem_operador:
            return
        try:
            resultado = calcular(expressao)
        except ZeroDivisionError:
            tratar_erro(window, estado, ERRO_DIVISAO)
        except OverflowError:
            tratar_erro(window, estado, ERRO_GRANDE)
        except (ValueError, ArithmeticError):
            tratar_erro(window, estado, ERRO_EXPRESSAO)
        else:
            adicionar_ao_historico(window, historico, expressao, resultado)
            window['-CONTA-'].update(f'{expressao} =')
            estado['expressao'] = resultado
            estado['resultado_na_tela'] = True
            atualizar_display(window, resultado)
        return

    # Dígito ou ponto depois de um resultado começa uma conta nova;
    # operador depois de um resultado continua a conta a partir dele.
    if estado['resultado_na_tela'] and simbolo not in OPERADORES:
        expressao = ''
    if simbolo in OPERADORES:
        nova = adicionar_operador(expressao, simbolo)
    elif simbolo == '.':
        nova = adicionar_ponto(expressao)
    else:
        nova = adicionar_digito(expressao, simbolo)

    if len(nova) > MAX_CARACTERES:
        mostrar_aviso(window, f'Limite de {MAX_CARACTERES} caracteres')
        return

    estado['expressao'] = nova
    estado['resultado_na_tela'] = False
    window['-CONTA-'].update('')
    atualizar_display(window, nova)


# ============================== Programa principal ==============================

def main():
    sg.theme('Black')
    window = sg.Window('INE5201 - Calculadora', criar_layout(), finalize=True,
                       return_keyboard_events=True)
    estado = {'expressao': '', 'resultado_na_tela': False}
    historico = []

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == '-LIMPAR_HIST-':
            historico.clear()
            window['-HISTORICO-'].update(historico)
            continue

        if event == '-HISTORICO-':
            selecionado = values['-HISTORICO-']
            if selecionado:
                resultado = selecionado[0].split(' = ')[-1]
                estado['expressao'] = resultado
                estado['resultado_na_tela'] = True
                atualizar_display(window, resultado)
            continue

        simbolo = traduzir_evento(event)
        if simbolo is not None:
            processar_entrada(window, estado, historico, simbolo)

    window.close()


if __name__ == '__main__':
    main()
