"""2.9.1 — Exemplo da ORB em candles reais: dois dias seguidos da PETR4, um para cada futuro.

15/09/2026: o preço rompeu a máxima da faixa de abertura (compra). 16/09/2026: rompeu a mínima (venda).
A faixa de abertura é o 1º candle de 30 min do dia (10h00 às 10h30).
Stop e alvo HIPOTÉTICOS, só de exemplo (as regras de verdade saem da reunião com o orientador):
stop no outro lado da faixa; alvo a 3 faixas da entrada.
Rodar: py -3.14 orb_exemplo.py   →   salva orb_exemplo.png nesta pasta.
Dados: Profit Pro (Nelogica), candles de 30 min da PETR4 (pasta "Dados 90 dias").
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PASTA = Path(__file__).parent
DADOS = PASTA.parent / "Dados 90 dias" / "PETR4" / "PETR4_30min.csv"
VERDE, VERMELHO, AMARELO, CINZA, AZUL = "#1a9850", "#d73027", "#bf9000", "#404040", "#2166ac"
ALVO_FAIXAS = 3  # alvo hipotético: 3 vezes o tamanho da faixa
# (dia, título, cor, altura do texto da entrada, num lugar vazio de cada dia)
DIAS = [
    ("2026-09-15", "FUTURO 1: o preço rompe a MÁXIMA → COMPRA", VERDE, 49.65),
    ("2026-09-16", "FUTURO 2: o preço rompe a MÍNIMA → VENDA", VERMELHO, 49.48),
]


DIAS_DA_SEMANA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]


def reais(v):
    return f"R${v:.2f}".replace(".", ",")  # 49.3 -> "R$49,30"


todos = pd.read_csv(DADOS, parse_dates=["Data"])
todos["dia"] = todos["Data"].dt.strftime("%Y-%m-%d")

fig, eixos = plt.subplots(1, 2, figsize=(13, 6.6))
for ax, (dia, titulo, cor, y_texto) in zip(eixos, DIAS):
    c = todos[todos["dia"] == dia].reset_index(drop=True)
    maxima, minima = c["High"][0], c["Low"][0]  # a faixa de abertura: 1º candle do dia
    n = len(c)

    # a faixa de abertura e as linhas da máxima e da mínima, seguindo pelo dia
    ax.axhspan(minima, maxima, color=AMARELO, alpha=0.18, zorder=0)
    ax.axhline(maxima, color=VERDE, linestyle="--", linewidth=1.4, zorder=1)
    ax.axhline(minima, color=VERMELHO, linestyle="--", linewidth=1.4, zorder=1)

    # os candles do dia; o 1º (a faixa) tem contorno preto
    for i, k in c.iterrows():
        cc = VERDE if k["Close"] >= k["Open"] else VERMELHO
        ax.vlines(i, k["Low"], k["High"], color=cc, linewidth=1.5, zorder=3)
        ax.bar(i, max(abs(k["Close"] - k["Open"]), 0.005), 0.6, bottom=min(k["Open"], k["Close"]), color=cc,
               zorder=3, edgecolor="black" if i == 0 else cc, linewidth=1.5 if i == 0 else 0)

    # o 1º candle que sai da faixa: ali a estratégia entra
    resto = c.iloc[1:]
    sobe = (resto["High"] > maxima).idxmax() < (resto["Low"] < minima).idxmax() if (resto["Low"] < minima).any() \
        else True
    i = (resto["High"] > maxima).idxmax() if sobe else (resto["Low"] < minima).idxmax()
    entrada = maxima if sobe else minima
    faixa = maxima - minima
    stop = minima if sobe else maxima  # stop hipotético: o outro lado da faixa
    alvo = entrada + ALVO_FAIXAS * faixa if sobe else entrada - ALVO_FAIXAS * faixa
    ax.text(n - 0.2, maxima, f"máxima{'' if sobe else ' = stop'}\n{reais(maxima)}", color=VERDE,
            va="bottom", fontsize=9.5, fontweight="bold")
    ax.text(n - 0.2, minima, f"mínima{' = stop' if sobe else ''}\n{reais(minima)}", color=VERMELHO, va="top",
            fontsize=9.5, fontweight="bold")
    ax.axhline(alvo, color=AZUL, linestyle=":", linewidth=1.8, zorder=1)
    ax.text(n - 0.2, alvo, f"alvo\n{reais(alvo)}", color=AZUL, va="bottom" if sobe else "top", fontsize=9.5,
            fontweight="bold")

    # a saída: o 1º candle depois da entrada que toca o stop ou o alvo
    saida, preco_saida, motivo = n - 1, c["Close"].iloc[-1], "no fim do dia"
    for j in range(i, n):
        bateu_stop = c["Low"][j] <= stop if sobe else c["High"][j] >= stop
        bateu_alvo = c["High"][j] >= alvo if sobe else c["Low"][j] <= alvo
        if j > i and bateu_stop:
            saida, preco_saida, motivo = j, stop, "no stop"
            break
        if bateu_alvo:
            saida, preco_saida, motivo = j, alvo, "no alvo"
            break
    ax.scatter([saida], [preco_saida], s=150, marker="s", color=AZUL, edgecolor="black", linewidth=1.8, zorder=6)
    ax.scatter([i], [entrada], s=130, color="white", edgecolor="black", linewidth=2, zorder=5)
    ax.annotate(f"{'COMPRA' if sobe else 'VENDA'} a {reais(entrada)}\n(candle das {c['Data'][i]:%Hh%M})",
                (i, entrada), xytext=(6.5, y_texto), textcoords="data", fontsize=10.5,
                fontweight="bold", color=cor, ha="left", va="center",
                arrowprops={"arrowstyle": "->", "color": cor, "linewidth": 1.4})
    lucro = (preco_saida / entrada - 1) if sobe else (entrada / preco_saida - 1)
    fecha = f"saiu {motivo} a {reais(preco_saida)} às {c['Data'][saida]:%Hh%M}: {lucro * 100:+.1f}%"
    fecha = fecha.replace(".", ",")
    ax.text(7.5, (maxima + minima) / 2, "faixa de abertura (1º candle)", color=AMARELO, ha="center",
            va="center", fontsize=10, fontweight="bold")

    # a data em destaque, numa caixa acima do gráfico; embaixo dela, o que aconteceu no dia
    data = pd.Timestamp(dia)
    ax.text(0.5, 1.15, f"{data:%d/%m/%Y} ({DIAS_DA_SEMANA[data.weekday()]})", transform=ax.transAxes,
            ha="center", va="bottom", fontsize=16, fontweight="bold", color="white",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": cor, "edgecolor": "none"})
    ax.set_title(f"{titulo}\n{fecha}", fontsize=11.5, fontweight="bold", color=cor)
    ax.set_xticks(range(n), [f"{h:%Hh%M}" for h in c["Data"]], rotation=45, fontsize=8.5)
    ax.set_xlim(-0.7, n + 1.4)
    margem = (c["High"].max() - c["Low"].min()) * 0.12
    ax.set_ylim(c["Low"].min() - margem, c["High"].max() + margem)
    ax.set_ylabel("PETR4 (R$)")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.2f}".replace(".", ","))
    ax.grid(axis="y", alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)

fig.suptitle("A ORB na PETR4 em dois dias reais: a faixa de abertura e os dois futuros possíveis\n"
             "candles de 30 min (timeframe de 30 minutos), pregão das 10h00 às 17h00; "
             "alvo e stop hipotéticos, só de exemplo",
             fontsize=12.5, fontweight="bold", x=0.01, ha="left")
# legenda dos símbolos, uma só, embaixo dos dois gráficos (fora dos candles)
simbolos = [
    plt.Line2D([], [], marker="o", linestyle="", markersize=11, markerfacecolor="white", markeredgecolor="black",
               markeredgewidth=2, label="entrada"),
    plt.Line2D([], [], marker="s", linestyle="", markersize=11, markerfacecolor=AZUL, markeredgecolor="black",
               markeredgewidth=1.8, label="saída"),
    plt.Line2D([], [], color=AZUL, linestyle=":", linewidth=1.8, label="alvo (hipotético): 3 faixas da entrada"),
    plt.Line2D([], [], color=CINZA, linestyle="--", linewidth=1.4, label="stop (hipotético): o outro lado da faixa"),
]
fig.legend(handles=simbolos, loc="lower center", ncol=4, fontsize=10.5, frameon=False)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(PASTA / "orb_exemplo.png", dpi=200)
print("salvo orb_exemplo.png")
