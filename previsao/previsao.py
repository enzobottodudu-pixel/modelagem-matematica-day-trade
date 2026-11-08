"""Modelo de previsão: treina com os 2 primeiros meses de cada ativo e testa no último mês.

Treino: 12/07 a 09/09/2026. Teste: 10/09 a 09/10/2026 (o mesmo corte do backtest, em backtest/dados.py).
Candles de 1 h (timeframe de 1 hora), os 9 ativos do TCC.

O modelo (regressão linear):
- olha as 3 últimas variações do preço (em %) e tenta adivinhar a variação da próxima hora;
- a conta é: variação prevista = a + b1 × última + b2 × penúltima + b3 × antepenúltima;
- os números a, b1, b2 e b3 são escolhidos só com os dados do treino (mínimos quadrados);
- no teste, a cada hora, preço previsto = último preço real × (1 + variação prevista).

Para comparar, o "palpite ingênuo": a próxima hora fecha no mesmo preço da última.

Rodar: py -3.14 previsao.py   →   salva as imagens em previsao/imagens/, a tabela em RESULTADOS.md
e as previsões do teste em previsoes_teste.csv (usadas por simulacao.py).
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parent / "backtest"))
from dados import ATIVOS, carregar, treino_e_teste

TIMEFRAME = "1h"
VOLTAS = 3  # quantas variações passadas o modelo olha
NOMES = {"EURUSD": "EUR/USD", "SPY": "SPY", "NQ": "NQ", "IBOV": "IBOV", "PETR4": "PETR4", "ITUB4": "ITUB4",
         "BTCUSD": "BTC/USD", "TESLA": "Tesla", "MGLU3": "MGLU3"}
MOEDA = {"EURUSD": "US$", "SPY": "US$", "NQ": "pontos", "IBOV": "pontos", "PETR4": "R$", "ITUB4": "R$",
         "BTCUSD": "US$", "TESLA": "US$", "MGLU3": "R$"}
PRETO, LARANJA, CINZA = "#222222", "#e66101", "#9e9e9e"
(PASTA / "imagens").mkdir(exist_ok=True)


def virgula(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",")  # 52.3 -> "52,3"


def preco(v, _=None):
    if v >= 1000:
        return f"{v:,.0f}".replace(",", ".")  # 86000 -> "86.000"
    return virgula(v, 3 if v < 5 else 0 if v == int(v) else 1)  # 1.172 -> "1,172"


def tabela_de_voltas(variacao):
    """Monta as colunas 'última', 'penúltima', ... para cada hora."""
    return pd.concat({f"v{k}": variacao.shift(k) for k in range(VOLTAS)}, axis=1)


resultados, previsoes = [], []
for ativo in ATIVOS:
    candles = carregar(ativo, TIMEFRAME)
    candles["variacao"] = candles["Close"].pct_change()  # variação de cada hora: 0.01 = +1%
    entradas = tabela_de_voltas(candles["variacao"])
    candles["alvo"] = candles["variacao"].shift(-1)  # o que o modelo tenta adivinhar: a variação da próxima hora
    candles["dia_seguinte"] = candles["dia"].shift(-1)  # para saber se a próxima hora ainda é o mesmo dia
    treino, teste = treino_e_teste(candles.join(entradas))

    # 1) TREINO: acha a, b1, b2, b3 que erram menos nos 2 primeiros meses
    t = treino.dropna(subset=[*entradas.columns, "alvo"])
    x = np.column_stack([np.ones(len(t)), t[entradas.columns]])
    pesos = np.linalg.lstsq(x, t["alvo"], rcond=None)[0]

    # 2) TESTE: a cada hora do último mês, prevê o preço da hora seguinte
    s = teste.dropna(subset=[*entradas.columns, "alvo"])
    prevista = np.column_stack([np.ones(len(s)), s[entradas.columns]]) @ pesos
    real_seguinte = s["Close"] * (1 + s["alvo"])  # o preço que de fato aconteceu na hora seguinte
    previsto = s["Close"] * (1 + prevista)

    # 3) NOTAS: erro médio do modelo, erro do palpite ingênuo e acerto da direção (subiu ou caiu)
    erro_modelo = (abs(previsto - real_seguinte) / real_seguinte).mean() * 100
    erro_ingenuo = (abs(s["Close"] - real_seguinte) / real_seguinte).mean() * 100
    mexeu = s["alvo"] != 0
    acerto = (np.sign(prevista[mexeu]) == np.sign(s["alvo"][mexeu])).mean() * 100
    resultados.append((ativo, len(t), len(s), erro_modelo, erro_ingenuo, acerto, pesos))
    previsoes.append(s[["dia", "dia_seguinte", "Close", "alvo"]].assign(ativo=ativo, prevista=prevista))

    # 4) GRÁFICO: em cima, o preço real e o previsto; embaixo, a variação real e a prevista de cada hora
    n = len(s)
    fig, (ax, axv) = plt.subplots(2, 1, figsize=(13, 7.5), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]})
    ax.plot(range(n), real_seguinte.to_numpy(), color=PRETO, linewidth=1.6, label="real")
    ax.plot(range(n), previsto.to_numpy(), color=LARANJA, linewidth=1.3, linestyle="--", label="previsto pelo modelo")
    baixo, alto = ax.get_ylim()
    ax.set_ylim(baixo, alto + (alto - baixo) * 0.12)  # espaço vazio em cima para a legenda não cobrir as linhas
    ax.legend(loc="upper left", fontsize=10, frameon=False, ncol=2)
    ax.set_ylabel(f"{NOMES[ativo]} ({MOEDA[ativo]})")
    ax.yaxis.set_major_formatter(preco)
    ax.grid(axis="y", alpha=0.3)

    axv.bar(range(n), s["alvo"].to_numpy() * 100, color=CINZA, width=0.8, label="variação real")
    axv.plot(range(n), prevista * 100, color=LARANJA, linewidth=1.5, label="variação prevista")
    axv.axhline(0, color=PRETO, linewidth=0.8)
    baixo, alto = axv.get_ylim()
    axv.set_ylim(baixo, alto + (alto - baixo) * 0.25)
    axv.legend(loc="upper left", fontsize=9.5, frameon=False, ncol=2)
    axv.set_ylabel("variação na hora (%)")
    axv.yaxis.set_major_formatter(lambda v, _: virgula(v))
    axv.grid(axis="y", alpha=0.3)

    # no eixo de baixo, o primeiro candle de alguns dias, com distância parecida entre eles
    primeiros = pd.Series(range(n), index=s["dia"].to_numpy()).groupby(level=0).first()
    marcas, ultima = [], -n
    for dia, posicao in primeiros.items():
        if posicao - ultima >= n / 11:
            marcas.append((posicao, f"{dia:%d/%m}"))
            ultima = posicao
    axv.set_xticks([m[0] for m in marcas], [m[1] for m in marcas], fontsize=9)
    axv.set_xlim(-1, n)
    for a in (ax, axv):
        for lado in ("top", "right"):
            a.spines[lado].set_visible(False)

    ax.set_title(f"{NOMES[ativo]}: preço real × previsto pelo modelo no teste (10/09 a 09/10/2026)\n"
                 f"candles de 1 h (timeframe de 1 hora), regressão linear com as {VOLTAS} últimas variações, "
                 "treinada de 12/07 a 09/09/2026\n"
                 f"erro médio: modelo {virgula(erro_modelo, 2)}%, repetir o último preço {virgula(erro_ingenuo, 2)}%"
                 f"  |  acertou se subia ou caía em {virgula(acerto)}% das horas",
                 fontsize=11.5, fontweight="bold", loc="left")
    fig.tight_layout()
    fig.savefig(PASTA / "imagens" / f"previsao_{ativo}.png", dpi=170)
    plt.close(fig)

# as previsões do teste, para a simulação com capital (simulacao.py)
pd.concat(previsoes).to_csv(PASTA / "previsoes_teste.csv")

# a tabela com as notas de todos os ativos
linhas = [
    "# Modelo de previsão: treino nos 2 primeiros meses, teste no último mês",
    "",
    (f"Candles de 1 h. Treino: 12/07 a 09/09/2026. Teste: 10/09 a 09/10/2026. Regressão linear com as {VOLTAS} "
     "últimas variações. Gerado por `previsao.py`."),
    "",
    ("| Ativo | Horas no treino | Horas no teste | Erro médio do modelo | Erro de repetir o último preço "
     "| Acerto da direção | a, b1, b2, b3 |"),
    "|---|---|---|---|---|---|---|",
]
for ativo, nt, ns, em, ei, ac, p in resultados:
    pesos_txt = ", ".join(virgula(v, 4 if k == 0 else 3) for k, v in enumerate(p * [100, 1, 1, 1]))
    linhas.append(f"| {NOMES[ativo]} | {nt} | {ns} | {virgula(em, 3)}% | {virgula(ei, 3)}% | {virgula(ac)}% "
                  f"| {pesos_txt} |")
linhas += ["", ("O valor de a está em %. Acerto da direção: % das horas em que o modelo acertou se o preço subia "
                "ou caía (sem contar as horas em que o preço ficou parado).")]
(PASTA / "RESULTADOS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
print("\n".join(linhas))
