"""
ESTRATÉGIA: CRUZAMENTO DE MÉDIAS MÓVEIS EXPONENCIAIS — o "jogador".

Ele olha os candles e escreve, no FIM de cada candle, o que a estratégia diz:
  "compra"  quando a média RÁPIDA cruza a LENTA para CIMA
  "venda"   quando a média RÁPIDA cruza a LENTA para BAIXO
  "nada"    no resto do tempo

Quem abre e fecha as operações é o motor (motor.py). As regras estão em REGRAS_cruzamento_medias.md.
"""


def preparar(tabela, rapida, lenta):
    """Acrescenta à tabela de candles as médias e os sinais da estratégia.

    rapida, lenta: quantos candles cada média usa (ex.: 9 e 21)
    Colunas novas: media_rapida, media_lenta, sinal e lado_media_lenta.
    """
    tabela = tabela.copy()
    fechamento = tabela["Close"]

    # MME (média móvel exponencial): MME = preço × k + MME anterior × (1 − k), com k = 2 / (N + 1)
    # A conta segue de um dia para o outro (decisão 9: as médias "não zeram" no começo do dia).
    tabela["media_rapida"] = fechamento.ewm(span=rapida, adjust=False).mean()
    tabela["media_lenta"] = fechamento.ewm(span=lenta, adjust=False).mean()

    # Quem está por cima, a rápida ou a lenta? E no candle anterior?
    rapida_em_cima = tabela["media_rapida"] > tabela["media_lenta"]
    antes_em_cima = rapida_em_cima.shift(1, fill_value=False)
    cruzou_para_cima = rapida_em_cima & ~antes_em_cima
    cruzou_para_baixo = ~rapida_em_cima & antes_em_cima

    sinais = []
    for numero, (cima, baixo) in enumerate(zip(cruzou_para_cima, cruzou_para_baixo)):
        if numero < lenta:  # "aquecimento": nos primeiros candles a média ainda não tem candles suficientes
            sinais.append("nada")
        elif cima:
            sinais.append("compra")
        elif baixo:
            sinais.append("venda")
        else:
            sinais.append("nada")
    tabela["sinal"] = sinais

    # Para a saída pela média lenta (decisão 5): o candle FECHOU acima ou abaixo da média lenta?
    tabela["lado_media_lenta"] = ["acima" if f > m else "abaixo" for f, m in zip(fechamento, tabela["media_lenta"])]
    return tabela


if __name__ == "__main__":
    import pandas as pd
    from custos import custo_percentual
    from dados import carregar, treino_e_teste
    from desenho import salvar_painel
    from metricas import boletim, mostrar_boletim
    from motor import simular_dia, simular_periodo, tabela_para_candles

    # 1) PETR4, 5 minutos, médias de 9 e 21. As médias são calculadas nos 90 dias e só DEPOIS o treino é separado:
    #    assim, no começo do teste, a média já vem "aquecida" pelos candles anteriores (sem olhar o futuro).
    tabela = preparar(carregar("PETR4", "5min"), rapida=9, lenta=21)
    treino, teste = treino_e_teste(tabela)
    print(
        f"Sinais no treino: {sum(treino['sinal'] == 'compra')} de compra e {sum(treino['sinal'] == 'venda')} de venda"
    )

    # 2) A versão mais simples: entrada A, sem stop, sem alvo, sem a regra da média lenta, sem horário-limite
    caderno = simular_periodo("PETR4", "5min", treino)
    print()
    mostrar_boletim(boletim(caderno), "PETR4, 5 min, TREINO, médias 9/21, versão mais simples")

    # 3) Um dia para ver com os olhos: as duas médias, os cruzamentos e as operações
    dia = treino[treino["dia"] == pd.Timestamp("2026-07-15").date()]
    candles = tabela_para_candles(dia)
    ops = simular_dia(candles, list(dia["sinal"]), custo_percentual("PETR4", candles[0]["abertura"]), mostrar=False)
    caminho = salvar_painel(
        [
            (
                candles,
                ops,
                "PETR4, 5 min, 15/07/2026 — MME 9 (azul) e MME 21 (laranja); entrada A, sai no cruzamento contrário",
                list(dia["media_rapida"]),
                list(dia["media_lenta"]),
            )
        ],
        "Cruzamento de médias: um dia de verdade",
        "estrategia_medias_um_dia.png",
    )
    print()
    print("Imagem salva:", caminho.name)
