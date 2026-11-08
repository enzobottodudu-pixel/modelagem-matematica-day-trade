"""Cap. 2 — O petróleo Brent na guerra entre EUA/Israel e Irã (2026), em candles semanais.

Rodar: py -3.14 petroleo_guerra_ira.py   →   salva cap2_6_petroleo_guerra_ira.png nesta pasta.
Datas dos eventos: Encyclopaedia Britannica (2026).
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from matplotlib.ticker import FuncFormatter

PASTA = Path(__file__).parent
INICIO = "2025-10-01"
AZUL, CINZA, VERMELHO, VERDE = "#1f4e79", "#4d4d4d", "#d73027", "#1a9850"

brent = yf.download("BZ=F", start=INICIO, interval="1wk", auto_adjust=False, progress=False)
brent.columns = brent.columns.get_level_values(0)  # tira o nome do ativo do cabeçalho
brent = brent.dropna()
brent = brent[brent.index <= pd.Timestamp.today() - pd.Timedelta(days=7)]  # só semanas completas
preco = brent["Close"]


def reais(valor):
    return f"US${valor:.0f}"


# as 4 fases, cada uma com uma cor de fundo
FASES = [
    (INICIO, "2026-02-28", "1) Antes da guerra", "#f3f3f3"),
    ("2026-02-28", "2026-04-08", "2) Guerra e Ormuz\nfechado", "#fcebea"),
    ("2026-04-08", "2026-07-07", "3) Cessar-fogo", "#e9f5eb"),
    ("2026-07-07", preco.index[-1] + pd.Timedelta(days=7), "4) A guerra volta", "#fcebea"),
]

fig, ax = plt.subplots(figsize=(11, 5.8))
for inicio, fim, nome, cor in FASES:
    a, b = pd.Timestamp(inicio), pd.Timestamp(fim)
    ax.axvspan(a, b, color=cor, zorder=0)
    ax.text(a + (b - a) / 2, 136, nome, ha="center", va="top", fontsize=10, fontweight="bold", color=CINZA)

# candles: corpo (abertura → fechamento) e pavio (mínima → máxima)
largura = pd.Timedelta(days=4.5)
for dia, c in brent.iterrows():
    cor = VERDE if c["Close"] >= c["Open"] else VERMELHO
    ax.vlines(dia, c["Low"], c["High"], color=cor, linewidth=1, zorder=3)
    ax.bar(dia, max(abs(c["Close"] - c["Open"]), 0.3), largura, bottom=min(c["Open"], c["Close"]), color=cor, zorder=3)

# os 4 números que contam a história
antes = preco[:"2026-02-27"].iloc[-1]
topo_dia = preco["2026-02-28":"2026-06-30"].idxmax()
fundo_dia = preco["2026-04-08":"2026-07-07"].idxmin()
hoje_dia = preco.index[-1]
PONTOS = [
    (preco[:"2026-02-27"].index[-1], antes, f"{reais(antes)}", (-14, -34), CINZA),
    (
        topo_dia,
        preco[topo_dia],
        f"{reais(preco[topo_dia])}\n(+{(preco[topo_dia] / antes - 1) * 100:.0f}%)",
        (-80, 8),
        VERMELHO,
    ),
    (fundo_dia, preco[fundo_dia], f"{reais(preco[fundo_dia])}", (-22, -40), VERDE),
    (hoje_dia, preco[hoje_dia], f"{reais(preco[hoje_dia])}", (-30, 18), AZUL),
]
for dia, valor, texto, deslocamento, cor in PONTOS:
    ax.scatter([dia], [valor], s=60, color=AZUL, zorder=4, edgecolor="white", linewidth=1.5)
    ax.annotate(
        texto,
        (dia, valor),
        xytext=deslocamento,
        textcoords="offset points",
        fontsize=11,
        fontweight="bold",
        color=cor,
        ha="center",
    )
    print(f"{dia:%d/%m/%Y}: {texto.replace(chr(10), ' ')}")

ax.set_title(
    "Petróleo Brent na guerra entre EUA/Israel e Irã\n"
    f"candles semanais (timeframe de 1 semana), de 10/2025 a {hoje_dia:%m/%Y}; os pontos azuis marcam o fechamento",
    fontsize=11.5,
    loc="left",
    fontweight="bold",
)
ax.text(
    0,
    -0.13,
    "28/02: EUA e Israel atacam o Irã, e o Irã fecha o Estreito de Ormuz   •   "
    "08/04: cessar-fogo   •   07/07: o Irã ataca navios e o cessar-fogo acaba",
    transform=ax.transAxes,
    fontsize=9,
    color=CINZA,
)
ax.set_ylabel("Preço do barril (US$)", fontsize=10)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: reais(v)))
ax.set_ylim(50, 140)
ax.set_xlim(pd.Timestamp(INICIO), hoje_dia + pd.Timedelta(days=7))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
ax.grid(axis="y", alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
fig.savefig(PASTA / "cap2_6_petroleo_guerra_ira.png", dpi=200)
print("salvo cap2_6_petroleo_guerra_ira.png")
