"""2.9.2 — Exemplo da VWAP em candles reais: um dia do ITUB4 com uma venda e uma compra.

03/09/2026, candles de 15 min. A VWAP recomeça na abertura (10h00) e soma preço × volume do dia.
Regra só de exemplo (as regras de verdade saem da reunião com o orientador):
- o candle fecha 0,6% ou mais ACIMA da VWAP → VENDE no fechamento dele;
- o candle fecha 0,6% ou mais ABAIXO da VWAP → COMPRA no fechamento dele;
- alvo: o preço voltar a tocar a VWAP; stop: o preço andar mais 0,6% contra a operação.
Rodar: py -3.14 vwap_exemplo.py   →   salva vwap_exemplo.png nesta pasta.
Dados: Profit Pro (Nelogica), candles de 15 min do ITUB4 com volume (pasta "Dados 90 dias").
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PASTA = Path(__file__).parent
ATIVO = "ITUB4"
DADOS = PASTA.parent / "Dados 90 dias" / ATIVO / f"{ATIVO}_15min.csv"
DIA = "2026-09-03"
LIMITE = 0.006  # 0,6% de distância da VWAP
STOP = 0.006  # stop hipotético: 0,6% contra a operação, a partir da entrada
VERDE, VERMELHO, AZUL, CINZA, LARANJA = "#1a9850", "#d73027", "#2166ac", "#808080", "#e66101"


def reais(v):
    return f"R${v:.2f}".replace(".", ",")  # 48.3 -> "R$48,30"


todos = pd.read_csv(DADOS, parse_dates=["Data"])
c = todos[todos["Data"].astype(str).str.startswith(DIA)].reset_index(drop=True)
n = len(c)

# VWAP: soma de (preço típico × volume) dividida pela soma do volume, desde a abertura
preco_tipico = (c["High"] + c["Low"] + c["Close"]) / 3
vwap = (preco_tipico * c["Volume"]).cumsum() / c["Volume"].cumsum()
distancia = c["Close"] / vwap - 1

# as operações do dia com a regra de exemplo
operacoes = []  # (lado, candle de entrada, preço de entrada, candle de saída, preço de saída, stop, motivo)
aberta = None
for i in range(1, n - 1):
    if aberta is None:
        if distancia[i] >= LIMITE:
            aberta = ("VENDA", i, c["Close"][i], c["Close"][i] * (1 + STOP))
        elif distancia[i] <= -LIMITE:
            aberta = ("COMPRA", i, c["Close"][i], c["Close"][i] * (1 - STOP))
    else:
        lado, ie, pe, stop = aberta
        if (lado == "VENDA" and c["High"][i] >= stop) or (lado == "COMPRA" and c["Low"][i] <= stop):
            operacoes.append((lado, ie, pe, i, stop, stop, "no stop"))
            aberta = None
        elif (lado == "VENDA" and c["Low"][i] <= vwap[i]) or (lado == "COMPRA" and c["High"][i] >= vwap[i]):
            operacoes.append((lado, ie, pe, i, vwap[i], stop, "na VWAP (alvo)"))
            aberta = None

fig, (ax, axv) = plt.subplots(2, 1, figsize=(13, 7.4), sharex=True, gridspec_kw={"height_ratios": [4, 1]})

# faixa de 0,6% acima e abaixo da VWAP (pontilhada) e a própria VWAP
ax.plot(range(n), vwap * (1 + LIMITE), color=CINZA, linestyle=":", linewidth=1.3, zorder=1)
ax.plot(range(n), vwap * (1 - LIMITE), color=CINZA, linestyle=":", linewidth=1.3, zorder=1)
ax.plot(range(n), vwap, color=AZUL, linewidth=2.4, zorder=2)
ax.text(n - 0.4, vwap.iloc[-1], "VWAP", color=AZUL, fontsize=11, fontweight="bold", va="center")
ax.text(n - 0.4, vwap.iloc[-1] * (1 + LIMITE), "+0,6%", color=CINZA, fontsize=9.5, va="center")
ax.text(n - 0.4, vwap.iloc[-1] * (1 - LIMITE), "−0,6%", color=CINZA, fontsize=9.5, va="center")

# os candles do dia e o volume embaixo
for i, k in c.iterrows():
    cor = VERDE if k["Close"] >= k["Open"] else VERMELHO
    ax.vlines(i, k["Low"], k["High"], color=cor, linewidth=1.4, zorder=3)
    ax.bar(i, max(abs(k["Close"] - k["Open"]), 0.005), 0.6, bottom=min(k["Open"], k["Close"]), color=cor,
           zorder=3)
    axv.bar(i, k["Volume"] / 1e6, 0.6, color=cor, alpha=0.6)

# entrada (círculo) e saída (quadrado) de cada operação, com o texto num lugar vazio, fora dos candles
for lado, ie, pe, isai, ps, stop, motivo in operacoes:
    cor = VERMELHO if lado == "VENDA" else VERDE
    lucro = (pe / ps - 1) if lado == "VENDA" else (ps / pe - 1)
    acima = lado == "VENDA"
    # o stop hipotético: um tracinho laranja do candle seguinte à entrada até o da saída
    ax.hlines(stop, ie + 0.3, isai + 0.4, color=LARANJA, linewidth=2, zorder=4)
    ax.text(isai + 0.5, stop, f"stop {reais(stop)}", color=LARANJA, fontsize=9.5, fontweight="bold",
            va="top" if acima else "bottom")
    ax.scatter([ie], [pe], s=140, color="white", edgecolor=cor, linewidth=2.5, zorder=5)
    ax.scatter([isai], [ps], s=150, marker="s", color=cor, edgecolor="black", linewidth=1.8, zorder=6)
    # o texto fica do lado de fora do stop, e a seta desce (ou sobe) pela esquerda do candle da entrada
    y = stop + 0.17 if acima else stop - 0.17
    ax.annotate(f"{lado} a {reais(pe)} ({c['Data'][ie]:%Hh%M})\nsai {motivo} a {reais(ps)} "
                f"({c['Data'][isai]:%Hh%M}): +{lucro * 100:.1f}%".replace(".", ","),
                (ie - 0.15, pe + (0.03 if acima else -0.03)), xytext=(ie - 0.6, y), fontsize=10.5,
                fontweight="bold", color=cor, va="bottom" if acima else "top",
                arrowprops={"arrowstyle": "->", "color": cor, "linewidth": 1.4, "relpos": (0.03, 0 if acima else 1)})

# legenda dos símbolos, no canto vazio de cima à direita
ax.scatter([], [], s=140, color="white", edgecolor="black", linewidth=2.5, label="entrada")
ax.scatter([], [], s=150, marker="s", color="white", edgecolor="black", linewidth=1.8, label="saída")
ax.plot([], [], color=LARANJA, linewidth=2, label="stop (hipotético)")
ax.legend(loc="upper right", fontsize=10, frameon=False)

ax.set_title(f"A VWAP no {ATIVO} em 03/09/2026 (quinta-feira): o preço se afasta da VWAP e volta para ela\n"
             "candles de 15 min (timeframe de 15 minutos), VWAP desde a abertura das 10h00; "
             "alvo e stop hipotéticos, só de exemplo", fontsize=12.5, fontweight="bold", loc="left")
stops = [op[5] for op in operacoes]
ax.set_ylim(min([c["Low"].min(), *stops]) - 0.5, max([c["High"].max(), *stops]) + 0.5)
ax.set_xlim(-0.7, n + 1.2)
ax.set_ylabel(f"{ATIVO} (R$)")
ax.yaxis.set_major_formatter(lambda v, _: f"{v:.2f}".replace(".", ","))
ax.grid(axis="y", alpha=0.3)
axv.set_ylabel("volume\n(milhões)")
axv.set_xticks(range(n), [f"{h:%Hh%M}" for h in c["Data"]], rotation=45, fontsize=8.5)
for a in (ax, axv):
    for lado in ("top", "right"):
        a.spines[lado].set_visible(False)

fig.tight_layout()
fig.savefig(PASTA / "vwap_exemplo.png", dpi=200)
for op in operacoes:
    print(op)
print("salvo vwap_exemplo.png")
