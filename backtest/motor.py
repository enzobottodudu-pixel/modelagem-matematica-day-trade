"""
MOTOR DO BACKTEST — vamos construir em pedaços, um de cada vez.

PEDAÇO 1: o resultado de UMA operação (a fórmula do retorno da seção 4.1).
PEDAÇO 2: andar pelos candles de um dia, um por um, decidindo quando entrar e quando sair.
PEDAÇO 3: usar um dia DE VERDADE (PETR4, 5 minutos) no lugar dos números inventados.
PEDAÇO 4: stop e alvo (olhando a máxima e a mínima de cada candle).
PEDAÇO 5: sair pelo sinal da estratégia (cruzamento contrário e lado da média lenta).
PEDAÇO 6: os 3 jeitos de entrar (A abertura, B fechamento, C recuo até a média rápida).
PEDAÇO 7: horários (só o pregão normal, no dados.py; e sem novas entradas na última hora).
PEDAÇO 8: vários dias seguidos (o treino inteiro), juntando todas as operações.
"""

import pandas as pd
from custos import custo_percentual
from dados import carregar, treino_e_teste
from desenho import salvar_painel, salvar_pedaco1, salvar_pedaco8


# ---------------------------------------------------------------------------
# PEDAÇO 1
# ---------------------------------------------------------------------------
def resultado_operacao(direcao, preco_entrada, preco_saida, custo):
    """Devolve quanto a operação ganhou ou perdeu, em %, já tirando o custo."""
    if direcao == "compra":
        # Comprou barato e vendeu caro: ganha quando o preço SOBE
        retorno = (preco_saida - preco_entrada) / preco_entrada * 100
    else:
        # Vendeu primeiro e recomprou depois: ganha quando o preço CAI
        retorno = (preco_entrada - preco_saida) / preco_entrada * 100
    return retorno - custo


# ---------------------------------------------------------------------------
# PEDAÇO 2 (e as partes que os pedaços 4, 5 e 6 acrescentaram)
# ---------------------------------------------------------------------------
def abrir_operacao(direcao, entrada, i, tipo_entrada, stop, alvo, candle, mostrar=True):
    """Cria a operação e já calcula o PREÇO do stop e do alvo (pedaço 4)."""
    op = {"direcao": direcao, "entrada": entrada, "candle_entrada": i, "tipo_entrada": tipo_entrada}
    if direcao == "compra":  # na compra: stop ABAIXO, alvo ACIMA
        op["preco_stop"] = entrada * (1 - stop / 100) if stop else None
        op["preco_alvo"] = entrada * (1 + alvo / 100) if alvo else None
    else:  # na venda é ao contrário: stop ACIMA, alvo ABAIXO
        op["preco_stop"] = entrada * (1 + stop / 100) if stop else None
        op["preco_alvo"] = entrada * (1 - alvo / 100) if alvo else None
    if mostrar:
        quando = candle.get("horario", f"candle {i}")  # mostra o horário, se o candle tiver
        print(f"  {quando}: ENTROU ({direcao}, {tipo_entrada}) a {entrada:.2f}")
    return op


def simular_dia(
    candles,
    sinais,
    custo,
    stop=None,
    alvo=None,
    lado_media_lenta=None,
    entrada="A",
    media_rapida=None,
    sem_entrada_ultima_hora=False,
    sinal_anterior="nada",
    mostrar=True,
):
    """Anda pelos candles de UM dia e devolve a lista de operações feitas.

    candles: lista de candles do dia, cada um com "abertura", "maxima", "minima" e "fechamento"
    sinais:  o que a estratégia disse no FIM de cada candle: "compra", "venda" ou "nada"
    stop:    em %, quanto aceita perder antes de sair (None = sem stop)              -> PEDAÇO 4
    alvo:    em %, quanto quer ganhar para sair (None = sem alvo)                     -> PEDAÇO 4
    lado_media_lenta: para cada candle, se ele FECHOU "acima" ou "abaixo" da média lenta
             (None = não usar essa regra de saída)                                  -> PEDAÇO 5
    entrada: "A" = abertura do próximo candle; "B" = fechamento do candle do sinal;
             "C" = espera o preço voltar até a média rápida                         -> PEDAÇO 6
    media_rapida: o valor da média rápida em cada candle (só a entrada C usa)       -> PEDAÇO 6
    sem_entrada_ultima_hora: True = não abre operação nova na última hora do dia   -> PEDAÇO 7
             (cada candle precisa da marca "ultima_hora": True ou False)
    sinal_anterior: o sinal do ÚLTIMO candle do dia anterior (entra na abertura de hoje) -> PEDAÇO 8
    mostrar: True = escreve cada entrada e saída na tela                             -> PEDAÇO 8
    """
    operacoes = []  # caderno onde o motor anota cada operação terminada
    aberta = None  # operação aberta agora (None = nenhuma)
    ordem_c = None  # entrada C: a direção que está esperando o recuo (None = nenhuma)

    for i in range(len(candles)):  # i = número do candle: 0, 1, 2, 3...
        candle = candles[i]
        ultimo_do_dia = i == len(candles) - 1
        entrou_agora_c = False
        # PEDAÇO 7: pode abrir operação nova neste candle? (não, se for a última hora e a regra estiver ligada)
        pode_entrar = not (sem_entrada_ultima_hora and candle.get("ultima_hora", False))

        # 1) ENTRAR NO COMEÇO OU NO MEIO DO CANDLE (entradas A e C)
        # PEDAÇO 8: no 1º candle, o "candle anterior" é o último de ONTEM; e um dia de 1 candle só pode entrar
        sinal_antes = sinais[i - 1] if i > 0 else sinal_anterior
        dia_de_um_candle = len(candles) == 1
        if aberta is None and (not ultimo_do_dia or dia_de_um_candle) and pode_entrar:
            # A: o candle ANTERIOR terminou com sinal -> entra na ABERTURA deste
            if entrada == "A" and sinal_antes != "nada":
                aberta = abrir_operacao(sinal_antes, candle["abertura"], i, "abertura", stop, alvo, candle, mostrar)
            # C: existe uma ordem esperando o recuo -> o preço chegou na média rápida?
            #    (usa a média do candle anterior, que já era conhecida quando este começou)
            elif entrada == "C" and ordem_c is not None and i > 0:
                limite = media_rapida[i - 1]
                if ordem_c == "compra" and candle["minima"] <= limite:
                    preco = min(candle["abertura"], limite)  # se já abriu abaixo, compra na abertura
                    aberta = abrir_operacao("compra", preco, i, "recuo", stop, alvo, candle, mostrar)
                elif ordem_c == "venda" and candle["maxima"] >= limite:
                    preco = max(candle["abertura"], limite)
                    aberta = abrir_operacao("venda", preco, i, "recuo", stop, alvo, candle, mostrar)
                if aberta is not None:
                    ordem_c, entrou_agora_c = None, True

        saida, motivo = None, None

        # 2) STOP e ALVO (PEDAÇO 4): o preço passou pela MÍNIMA e pela MÁXIMA do candle
        #    Se os dois forem atingidos no mesmo candle, conta o STOP (o caso pior, para não exagerar o lucro).
        #    Se o candle já ABRIR depois do stop ou do alvo (um "gap"), sai na abertura.
        #    Na entrada C, no candle em que entrou, só confere o stop: não dá para saber se a máxima veio antes.
        if aberta is not None:
            p_stop, p_alvo = aberta["preco_stop"], aberta["preco_alvo"]
            if entrou_agora_c:
                p_alvo = None
            if aberta["direcao"] == "compra":
                if p_stop is not None and candle["minima"] <= p_stop:
                    saida, motivo = min(candle["abertura"], p_stop), "stop"
                elif p_alvo is not None and candle["maxima"] >= p_alvo:
                    saida, motivo = max(candle["abertura"], p_alvo), "alvo"
            else:
                if p_stop is not None and candle["maxima"] >= p_stop:
                    saida, motivo = max(candle["abertura"], p_stop), "stop"
                elif p_alvo is not None and candle["minima"] <= p_alvo:
                    saida, motivo = min(candle["abertura"], p_alvo), "alvo"

        # 3) SINAL DA ESTRATÉGIA (PEDAÇO 5): olha o FECHAMENTO deste candle
        if aberta is not None and motivo is None:
            direcao = aberta["direcao"]
            # a) cruzamento contrário: comprado e veio sinal de venda (ou vendido e veio sinal de compra)
            if (direcao == "compra" and sinais[i] == "venda") or (direcao == "venda" and sinais[i] == "compra"):
                saida, motivo = candle["fechamento"], "cruzamento contrário"
            # b) fechou do outro lado da média lenta: comprado e fechou ABAIXO dela (ou vendido e fechou ACIMA)
            elif lado_media_lenta is not None and (
                (direcao == "compra" and lado_media_lenta[i] == "abaixo")
                or (direcao == "venda" and lado_media_lenta[i] == "acima")
            ):
                saida, motivo = candle["fechamento"], "fechou do outro lado da média lenta"

        # 4) FIM DO DIA: no último candle, fecha no FECHAMENTO o que ainda estiver aberto (é day trade)
        if aberta is not None and motivo is None and ultimo_do_dia:
            saida, motivo = candle["fechamento"], "fim do dia"

        # 5) ANOTAR a operação no caderno, se ela fechou neste candle
        if motivo is not None:
            resultado = resultado_operacao(aberta["direcao"], aberta["entrada"], saida, custo)
            if mostrar:
                quando = candle.get("horario", f"candle {i}")
                print(f"  {quando}: SAIU a {saida:.2f} ({motivo}) -> resultado {resultado:.2f}%")
            operacoes.append({**aberta, "saida": saida, "candle_saida": i, "motivo": motivo, "resultado": resultado})
            aberta = None

        # 6) NO FIM DO CANDLE, um sinal novo (PEDAÇO 6)
        if sinais[i] != "nada" and not ultimo_do_dia and aberta is None and pode_entrar:
            # B: entra no próprio FECHAMENTO do candle do sinal
            if entrada == "B":
                aberta = abrir_operacao(sinais[i], candle["fechamento"], i, "fechamento", stop, alvo, candle, mostrar)
            # C: não entra ainda; deixa uma ordem esperando o preço voltar até a média rápida
            #    (um sinal novo troca a ordem antiga)
            elif entrada == "C":
                ordem_c = sinais[i]

    return operacoes


# ---------------------------------------------------------------------------
# PEDAÇO 3
# ---------------------------------------------------------------------------
def candles_de_um_dia(ativo, timeframe, data):
    """Pega os candles reais de UM dia e põe no mesmo formato do pedaço 2."""
    tabela = carregar(ativo, timeframe)  # todos os candles dos 90 dias (do dados.py)
    tabela_do_dia = tabela[tabela["dia"] == pd.Timestamp(data).date()]  # só o dia pedido

    return tabela_para_candles(tabela_do_dia)


def tabela_para_candles(tabela_do_dia):
    """Transforma as linhas da tabela no formato de candle que o motor entende."""
    candles = []
    for horario, linha in tabela_do_dia.iterrows():  # uma linha da tabela = um candle
        candles.append(
            {
                "horario": horario.strftime("%H:%M"),
                "abertura": linha["Open"],
                "maxima": linha["High"],
                "minima": linha["Low"],
                "fechamento": linha["Close"],
                "ultima_hora": linha["ultima_hora"],  # pedaço 7
            }
        )
    return candles


# ---------------------------------------------------------------------------
# PEDAÇO 8
# ---------------------------------------------------------------------------
def simular_periodo(
    ativo, timeframe, tabela, stop=None, alvo=None, usar_media_lenta=False, entrada="A", sem_entrada_ultima_hora=False
):
    """Roda o motor em TODOS os dias da tabela, um depois do outro, e junta as operações num caderno só.

    A tabela precisa de uma coluna "sinal" (o que a estratégia disse no fim de cada candle) e, se for usar,
    das colunas "media_rapida" (entrada C) e "lado_media_lenta" (saída pela média lenta).
    """
    caderno = []
    sinal_de_ontem = "nada"
    for dia, tabela_do_dia in tabela.groupby("dia"):  # um dia de cada vez, em ordem
        candles = tabela_para_candles(tabela_do_dia)
        custo = custo_percentual(ativo, candles[0]["abertura"], timeframe)  # custo pelo preço do dia
        operacoes = simular_dia(
            candles,
            list(tabela_do_dia["sinal"]),
            custo,
            stop=stop,
            alvo=alvo,
            lado_media_lenta=list(tabela_do_dia["lado_media_lenta"]) if usar_media_lenta else None,
            entrada=entrada,
            media_rapida=list(tabela_do_dia["media_rapida"]) if entrada == "C" else None,
            sem_entrada_ultima_hora=sem_entrada_ultima_hora,
            sinal_anterior=sinal_de_ontem,
            mostrar=False,  # são centenas de operações: não escreve uma por uma
        )
        for op in operacoes:
            op["dia"] = dia
        caderno += operacoes
        sinal_de_ontem = tabela_do_dia["sinal"].iloc[-1]  # o sinal do último candle passa para amanhã
    return caderno


# Testes: aperte o botão ▶ (canto de cima, à direita). As imagens vão para backtest/imagens/.
if __name__ == "__main__":
    # Dias inventados, todos com 4 ou 5 candles e compra a 100 (fica fácil conferir de cabeça)
    SINAL_COMPRA = ["compra", "nada", "nada", "nada"]

    dia_2 = [
        {"abertura": 100.0, "maxima": 101.2, "minima": 99.8, "fechamento": 101.0},
        {"abertura": 101.5, "maxima": 102.2, "minima": 101.3, "fechamento": 102.0},
        {"abertura": 102.0, "maxima": 103.2, "minima": 101.8, "fechamento": 103.0},
        {"abertura": 103.0, "maxima": 103.3, "minima": 102.2, "fechamento": 102.5},
        {"abertura": 102.5, "maxima": 104.2, "minima": 102.4, "fechamento": 104.0},
    ]
    dia_a = [  # sobe e bate o ALVO
        {"abertura": 100.0, "maxima": 100.4, "minima": 99.8, "fechamento": 100.0},
        {"abertura": 100.0, "maxima": 101.0, "minima": 99.5, "fechamento": 100.8},
        {"abertura": 100.8, "maxima": 102.3, "minima": 100.5, "fechamento": 102.0},
        {"abertura": 102.0, "maxima": 103.0, "minima": 101.5, "fechamento": 102.5},
    ]
    dia_b = [  # cai e bate o STOP
        {"abertura": 100.0, "maxima": 100.4, "minima": 99.8, "fechamento": 100.0},
        {"abertura": 100.0, "maxima": 100.6, "minima": 99.4, "fechamento": 99.6},
        {"abertura": 99.6, "maxima": 99.9, "minima": 98.7, "fechamento": 98.9},
        {"abertura": 98.9, "maxima": 99.5, "minima": 98.0, "fechamento": 99.0},
    ]
    dia_c = [  # um candle agitado passa pelos DOIS
        {"abertura": 100.0, "maxima": 100.4, "minima": 99.8, "fechamento": 100.0},
        {"abertura": 100.0, "maxima": 102.5, "minima": 98.6, "fechamento": 101.0},
        {"abertura": 101.0, "maxima": 101.5, "minima": 100.5, "fechamento": 101.2},
        {"abertura": 101.2, "maxima": 101.8, "minima": 101.0, "fechamento": 101.5},
    ]
    dia_d = [  # compra, e depois as médias cruzam AO CONTRÁRIO
        {"abertura": 100.0, "maxima": 100.4, "minima": 99.8, "fechamento": 100.0},
        {"abertura": 100.0, "maxima": 101.2, "minima": 99.9, "fechamento": 101.0},
        {"abertura": 101.0, "maxima": 101.1, "minima": 100.2, "fechamento": 100.4},
        {"abertura": 100.4, "maxima": 100.5, "minima": 99.6, "fechamento": 99.7},
        {"abertura": 99.7, "maxima": 99.9, "minima": 99.2, "fechamento": 99.3},
    ]
    dia_e = [  # um candle fecha ABAIXO da média lenta
        {"abertura": 100.0, "maxima": 100.4, "minima": 99.8, "fechamento": 100.0},
        {"abertura": 100.0, "maxima": 100.9, "minima": 99.9, "fechamento": 100.7},
        {"abertura": 100.7, "maxima": 100.8, "minima": 99.5, "fechamento": 99.6},
        {"abertura": 99.6, "maxima": 100.3, "minima": 99.4, "fechamento": 100.1},
    ]
    lado_e = ["acima", "acima", "abaixo", "acima"]

    # Dia real: PETR4, 5 minutos, 15/07/2026
    dia_real = candles_de_um_dia("PETR4", "5min", "2026-07-15")
    custo_petr4 = custo_percentual("PETR4", dia_real[0]["abertura"])

    # Pedaço 6: o MESMO sinal de compra (no fim do candle 1), com os 3 jeitos de entrar
    sinal_f = ["nada", "compra", "nada", "nada", "nada"]
    dia_f = [  # o preço VOLTA até a média rápida depois do sinal
        {"abertura": 100.0, "maxima": 100.5, "minima": 99.8, "fechamento": 100.4},
        {"abertura": 100.4, "maxima": 101.5, "minima": 100.3, "fechamento": 101.4},  # sinal de compra
        {"abertura": 101.5, "maxima": 101.9, "minima": 100.7, "fechamento": 101.6},
        {"abertura": 101.6, "maxima": 101.8, "minima": 100.8, "fechamento": 101.0},  # mínima toca a média
        {"abertura": 101.0, "maxima": 102.2, "minima": 100.9, "fechamento": 102.0},
    ]
    media_f = [100.2, 100.6, 100.9, 100.95, 101.2]
    dia_g = [  # o preço DISPARA e não volta até a média rápida
        {"abertura": 100.0, "maxima": 100.5, "minima": 99.8, "fechamento": 100.4},
        {"abertura": 100.4, "maxima": 101.5, "minima": 100.3, "fechamento": 101.4},  # sinal de compra
        {"abertura": 101.5, "maxima": 102.3, "minima": 101.3, "fechamento": 102.2},
        {"abertura": 102.2, "maxima": 103.0, "minima": 102.1, "fechamento": 102.9},
        {"abertura": 102.9, "maxima": 103.4, "minima": 102.7, "fechamento": 103.2},
    ]
    media_g = [100.2, 100.6, 101.0, 101.5, 102.0]

    def tres_entradas(dia, media, nome):
        """O mesmo dia com as entradas A, B e C, para comparar lado a lado."""
        textos = {
            "A": "A: abertura do próximo candle",
            "B": "B: fechamento do candle do sinal",
            "C": "C: espera voltar até a média rápida",
        }
        return [
            (
                dia,
                simular_dia(dia, sinal_f, 0.09, entrada=jeito, media_rapida=media),
                f"{nome} — {textos[jeito]}",
                media,
            )
            for jeito in ("A", "B", "C")
        ]

    # Pedaço 7: dias de verdade
    spy_dia = candles_de_um_dia("SPY", "5min", "2026-07-15")  # já vem só com o pregão normal (dados.py)
    custo_spy = custo_percentual("SPY", spy_dia[0]["abertura"], "5min")
    petr4_dia = dia_real  # PETR4, 15/07, do pedaço 3
    hora_sinal = [c["horario"] for c in petr4_dia].index("15:55")  # sinal de teste no fim do candle das 15h55
    sinal_tarde = ["nada"] * len(petr4_dia)
    sinal_tarde[hora_sinal] = "compra"

    # Pedaço 8: o treino inteiro da PETR4 (5 minutos), com a regra de teste "compra no 1º candle de cada dia"
    treino_petr4, _ = treino_e_teste(carregar("PETR4", "5min"))
    treino_petr4 = treino_petr4.copy()
    primeiro_do_dia = ~treino_petr4["dia"].duplicated()  # True no 1º candle de cada dia
    treino_petr4["sinal"] = ["compra" if p else "nada" for p in primeiro_do_dia]
    caderno_petr4 = simular_periodo("PETR4", "5min", treino_petr4)
    ganhou = sum(1 for op in caderno_petr4 if op["resultado"] > 0)
    print()
    print("PEDAÇO 8 (treino inteiro da PETR4, 5 minutos, regra de teste: compra no 1º candle de cada dia)")
    print(f"  {len(caderno_petr4)} operações, {ganhou} com lucro e {len(caderno_petr4) - ganhou} com prejuízo")
    print(f"  soma dos resultados: {sum(op['resultado'] for op in caderno_petr4):+.2f}%")

    exemplos_1 = [
        (d, e, sai, 0.09, resultado_operacao(d, e, sai, 0.09))
        for d, e, sai in [("compra", 100, 103), ("venda", 100, 97), ("compra", 100, 95)]
    ]

    imagens = [
        salvar_pedaco1(exemplos_1, "pedaco1_a_conta.png"),
        salvar_painel(
            [
                (
                    dia_2,
                    simular_dia(dia_2, ["compra"] + ["nada"] * 4, 0.09),
                    "Dia inventado: sinal no candle 0 → entra no 1 (101,50) → sai no fim do dia",
                ),
                (
                    dia_2,
                    simular_dia(dia_2, ["nada", "nada", "compra", "nada", "nada"], 0.09),
                    "O mesmo dia com o sinal no candle 2 → entra mais tarde (103,00) e ganha menos",
                ),
            ],
            "Pedaço 2: o motor anda candle por candle",
            "pedaco2_candle_por_candle.png",
        ),
        salvar_painel(
            [
                (
                    dia_real,
                    simular_dia(dia_real, ["compra"] + ["nada"] * (len(dia_real) - 1), custo_petr4),
                    f"PETR4, 5 minutos, 15/07/2026 — regra de teste: compra no 1º candle (custo real {custo_petr4:.3f}%)",
                ),
            ],
            "Pedaço 3: um dia DE VERDADE",
            "pedaco3_dia_real_petr4.png",
        ),
        salvar_painel(
            [
                (dia_a, simular_dia(dia_a, SINAL_COMPRA, 0.09, stop=1, alvo=2), "Dia A: a máxima passa de 102 → ALVO"),
                (dia_b, simular_dia(dia_b, SINAL_COMPRA, 0.09, stop=1, alvo=2), "Dia B: a mínima passa de 99 → STOP"),
                (
                    dia_c,
                    simular_dia(dia_c, SINAL_COMPRA, 0.09, stop=1, alvo=2),
                    "Dia C: um candle passa pelos DOIS → conta o stop (o caso pior)",
                ),
            ],
            "Pedaço 4: stop de 1% (99) e alvo de 2% (102), comprando a 100",
            "pedaco4_stop_e_alvo.png",
        ),
        salvar_painel(
            [
                (
                    dia_d,
                    simular_dia(dia_d, ["compra", "nada", "venda", "nada", "nada"], 0.09),
                    "Dia D: cruzamento contrário → sai da compra e já entra vendendo",
                ),
                (
                    dia_e,
                    simular_dia(dia_e, SINAL_COMPRA, 0.09, lado_media_lenta=lado_e),
                    "Dia E COM a regra: o candle 2 fecha abaixo da média lenta → sai",
                ),
                (dia_e, simular_dia(dia_e, SINAL_COMPRA, 0.09), "Dia E SEM a regra: segura até o fim do dia"),
            ],
            "Pedaço 5: sair pelo sinal da estratégia",
            "pedaco5_saida_pelo_sinal.png",
        ),
        salvar_painel(
            tres_entradas(dia_f, media_f, "Dia F (o preço volta)")
            + tres_entradas(dia_g, media_g, "Dia G (o preço dispara)"),
            "Pedaço 6: os 3 jeitos de entrar, com o mesmo sinal de compra",
            "pedaco6_tres_entradas.png",
            colunas=2,
        ),
        salvar_painel(
            [
                (
                    spy_dia,
                    simular_dia(spy_dia, ["compra"] + ["nada"] * (len(spy_dia) - 1), custo_spy),
                    f"SPY, 5 min, 15/07: só o pregão normal (9h30 às 16h), {len(spy_dia)} candles — preço do índice S&P 500 (≈10× o SPY)",
                ),
                (
                    petr4_dia,
                    simular_dia(petr4_dia, sinal_tarde, custo_petr4),
                    "PETR4, 15/07: sinal às 15h55, SEM a regra → entra às 16h00, já na última hora",
                ),
                (
                    petr4_dia,
                    simular_dia(petr4_dia, sinal_tarde, custo_petr4, sem_entrada_ultima_hora=True),
                    "PETR4, 15/07: o mesmo sinal, COM a regra → não entra (a última hora está bloqueada)",
                ),
            ],
            "Pedaço 7: horários",
            "pedaco7_horarios.png",
        ),
        salvar_pedaco8(
            caderno_petr4,
            "Pedaço 8: o treino inteiro da PETR4 (5 min, 13/07 a 09/09) com a regra de teste",
            "pedaco8_treino_inteiro.png",
        ),
    ]
    print()
    print("Imagens salvas:")
    for caminho in imagens:
        print("  ", caminho.name)
