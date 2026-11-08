"""2.9.4 — Exemplo do cruzamento de médias em candles reais: um dia da Tesla com uma compra e uma venda.

16/09/2026, candles de 5 min, pregão normal de Nova York (9h30 às 16h00).
Médias móveis exponenciais (MME) de 9 e 21 candles, calculadas com os dias anteriores.
Regra só de exemplo (as regras de verdade saem da reunião com o orientador):
- a MME 9 (rápida) cruza a MME 21 (lenta) para cima → COMPRA no fechamento do candle;
- a MME 9 cruza a MME 21 para baixo → VENDE no fechamento do candle;
- no cruzamento contrário, fecha a operação e já entra no outro sentido ("vira a mão");
- a última operação fecha no fim do dia; stop hipotético: o preço andar 1,5% contra a operação.
Rodar: py -3.14 medias_exemplo.py   →   salva medias_exemplo.png nesta pasta.
Dados: Yahoo Finance, candles de 5 min da Tesla (TSLA) (pasta "Dados 90 dias").
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PASTA = Path(__file__).parent
DADOS = PASTA.parent / "Dados 90 dias" / "TESLA" / "TESLA_5min.csv"
DIA = "2026-09-16"
RAPIDA, LENTA = 9, 21  # períodos das duas médias
STOP = 0.015  # stop hipotético: 1,5% contra a operação, a partir da entrada
VERDE, VERMELHO, AZUL, ROXO, LARANJA = "#1a9850", "#d73027", "#2166ac", "#8e44ad", "#e66101"


def dolares(v):
    return f"US${v:.2f}".replace(".", ",")  # 359.29 -> "US$359,29"


todos = pd.read_csv(DADOS)
todos["Data"] = pd.to_datetime(todos["Data"].str[:19])  # horário de Nova York

# MME = preço × k + MME anterior × (1 − k), com k = 2 ÷ (N + 1); o pandas faz essa conta com span=N
todos["rapida"] = todos["Close"].ewm(span=RAPIDA, adjust=False).mean()
todos["lenta"] = todos["Close"].ewm(span=LENTA, adjust=False).mean()

c = todos[todos["Data"].astype(str).str.startswith(DIA)].reset_index(drop=True)
n = len(c)
acima = c["rapida"] > c["lenta"]  # True quando a rápida está em cima da lenta

# as operações do dia: cada cruzamento abre uma operação e fecha a anterior (vira a mão)
operacoes = []  # (lado, candle de entrada, preço de entrada, candle de saída, preço de saída, stop, motivo)
aberta = None
for i in range(1, n):
    if aberta is not None:
        lado, ie, pe, stop = aberta
        if (lado == "COMPRA" and c["Low"][i] <= stop) or (lado == "VENDA" and c["High"][i] >= stop):
            operacoes.append((lado, ie, pe, i, stop, stop, "no stop"))
            aberta = None
    if acima[i] != acima[i - 1] and i < n - 1:
        if aberta is not None:
            lado, ie, pe, stop = aberta
            operacoes.append((lado, ie, pe, i, c["Close"][i], stop, "no cruzamento"))
        lado = "COMPRA" if acima[i] else "VENDA"
        preco = c["Close"][i]
        aberta = (lado, i, preco, preco * (1 - STOP) if lado == "COMPRA" else preco * (1 + STOP))
if aberta is not None:
    lado, ie, pe, stop = aberta
    operacoes.append((lado, ie, pe, n - 1, c["Close"][n - 1], stop, "no fim do dia"))

fig, ax = plt.subplots(figsize=(14, 7.2))

# os candles do dia
for i, k in c.iterrows():
    cor = VERDE if k["Close"] >= k["Open"] else VERMELHO
    ax.vlines(i, k["Low"], k["High"], color=cor, linewidth=1.1, zorder=3)
    ax.bar(i, max(abs(k["Close"] - k["Open"]), 0.05), 0.65, bottom=min(k["Open"], k["Close"]), color=cor, zorder=3)

# as duas médias, com o nome no fim da linha
ax.plot(range(n), c["rapida"], color=AZUL, linewidth=2.4, zorder=4)
ax.plot(range(n), c["lenta"], color=ROXO, linewidth=2.4, zorder=4)
ax.text(n - 0.3, c["rapida"].iloc[-1], f"MME {RAPIDA}\n(rápida)", color=AZUL, fontsize=10, fontweight="bold",
        va="top")
ax.text(n - 0.3, c["lenta"].iloc[-1], f"MME {LENTA}\n(lenta)", color=ROXO, fontsize=10, fontweight="bold",
        va="bottom")

# entrada (círculo), saída (quadrado) e stop (laranja) de cada operação, com o texto num lugar vazio
for lado, ie, pe, isai, ps, stop, motivo in operacoes:
    cor = VERDE if lado == "COMPRA" else VERMELHO
    lucro = (ps / pe - 1) if lado == "COMPRA" else (pe / ps - 1)
    ax.hlines(stop, ie + 0.5, isai + 0.5, color=LARANJA, linewidth=2, zorder=4)
    ax.text(isai + 0.8, stop, f"stop {dolares(stop)}", color=LARANJA, fontsize=9.5, fontweight="bold", va="center")
    ax.scatter([ie], [pe], s=420, color="white", edgecolor=cor, linewidth=2.8, zorder=6)
    ax.scatter([isai], [ps], s=110, marker="s", color=cor, edgecolor="black", linewidth=1.8, zorder=7)
    porcento = f"{lucro * 100:+.1f}".replace(".", ",")  # 0.59 -> "+0,6"
    texto = (f"{lado} a {dolares(pe)} ({c['Data'][ie]:%Hh%M})\n"
             f"sai {motivo} a {dolares(ps)} ({c['Data'][isai]:%Hh%M}): {porcento}%")
    y = stop - 0.8 if lado == "COMPRA" else stop + 0.8
    ax.text((ie + isai) / 2, y, texto, color=cor, fontsize=10.5, fontweight="bold", ha="center",
            va="top" if lado == "COMPRA" else "bottom")

# legenda dos símbolos
ax.scatter([], [], s=200, color="white", edgecolor="black", linewidth=2.6, label="entrada (cruzamento)")
ax.scatter([], [], s=110, marker="s", color="white", edgecolor="black", linewidth=1.8, label="saída")
ax.plot([], [], color=LARANJA, linewidth=2, label="stop (hipotético)")
ax.legend(loc="upper right", fontsize=10, frameon=False)

ax.set_title("O cruzamento de médias na Tesla em 16/09/2026 (quarta-feira): compra, vira a mão e vende\n"
             f"candles de 5 min (timeframe de 5 minutos), horário de Nova York, MME de {RAPIDA} e de {LENTA} períodos\n"
             "stop hipotético, só de exemplo", fontsize=12.5, fontweight="bold", loc="left")
stops = [op[5] for op in operacoes]
ax.set_ylim(min([c["Low"].min(), *stops]) - 2.5, max([c["High"].max(), *stops]) + 2.5)
ax.set_xlim(-1, n + 6)
ax.set_ylabel("Tesla (US$)")
ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}")
ax.grid(axis="y", alpha=0.3)
ax.set_xticks(range(0, n, 6), [f"{h:%Hh%M}" for h in c["Data"][::6]], rotation=45, fontsize=9)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)

fig.tight_layout()
fig.savefig(PASTA / "medias_exemplo.png", dpi=200)
for op in operacoes:
    print(op)
print("salvo medias_exemplo.png")
