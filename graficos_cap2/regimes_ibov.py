"""3.7.5 — Os 3 regimes de mercado (alta, baixa e lateral) no IBOV, em candles semanais, de 2020 a 10/2026,
com o circuit breaker de 26/10/2026 no fim.

Rodar: py -3.14 regimes_ibov.py   →   salva cap2_7_regimes_ibov.png nesta pasta.
Dados: Yahoo Finance (^BVSP).
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from matplotlib.ticker import FuncFormatter

PASTA = Path(__file__).parent
INICIO, FIM = "2020-01-01", "2026-10-31"
CIRCUIT_BREAKER, FECH_ANTERIOR = pd.Timestamp("2026-10-26"), 205_083  # fechamento de 23/10/2026
AZUL, CINZA, VERMELHO, VERDE = "#1f4e79", "#4d4d4d", "#d73027", "#1a9850"

ibov = yf.download("^BVSP", start="2019-12-30", end=FIM, interval="1wk", auto_adjust=False, progress=False)
ibov.columns = ibov.columns.get_level_values(0)  # tira o nome do ativo do cabeçalho
ibov = ibov.dropna()  # começa numa segunda (30/12/2019) para cada candle ser uma semana de segunda a sexta


def pontos(valor):
    return f"{valor / 1000:.0f} mil"  # 119593 -> "120 mil"


# os 4 trechos: (início, fim, nome, cor de fundo)
FASES = [
    (INICIO, "2020-03-16", "BAIXA", "#fcebea"),
    ("2020-03-16", "2021-06-07", "ALTA", "#e9f5eb"),
    ("2021-06-07", "2021-11-29", "BAIXA", "#fcebea"),
    ("2021-11-29", "2023-10-30", "LATERAL\n(sem direção)", "#f1f1f1"),
    ("2023-10-30", "2026-04-13", "ALTA", "#e9f5eb"),
    ("2026-04-13", "2026-08-10", "BAIXA", "#fcebea"),
    ("2026-08-10", "2026-10-19", "ALTA", "#e9f5eb"),
]

fig, ax = plt.subplots(figsize=(12, 6.2))
for inicio, fim, nome, cor in FASES:
    a, b = pd.Timestamp(inicio), pd.Timestamp(fim)
    ax.axvspan(a, b, color=cor, zorder=0)
    estreita = (b - a).days < 200  # fase curta: o nome vai de pé para caber
    ax.text(a + (b - a) / 2, 246_000, nome, ha="center", va="top", fontsize=10 if estreita else 11,
            fontweight="bold", color=CINZA, rotation=90 if estreita else 0)

# candles: corpo (abertura → fechamento) e pavio (mínima → máxima)
largura = pd.Timedelta(days=4.5)
for dia, c in ibov.iterrows():
    cor = VERDE if c["Close"] >= c["Open"] else VERMELHO
    ax.vlines(dia, c["Low"], c["High"], color=cor, linewidth=1, zorder=3)
    ax.bar(dia, max(abs(c["Close"] - c["Open"]), 150), largura, bottom=min(c["Open"], c["Close"]), color=cor, zorder=3)

# os pontos de virada: (coluna, trecho onde procurar, deslocamento do texto, mostra o %?)
VIRADAS = [
    ("High", INICIO, "2020-03-01", (0, 10), False),
    ("Low", "2020-02", "2020-06", (12, -8), True),
    ("High", "2021", "2021", (0, 10), True),
    ("Low", "2021-06", "2021-12", (0, -30), True),
    ("Low", "2023-09", "2023-12", (0, -12), False),
    ("High", "2026-03", "2026-05", (-16, 2), True),
    ("Low", "2026-05", "2026-09", (-10, -4), True),
    ("High", "2026-10", "2026-10-19", (-6, 10), True),
]
viradas = []
for k, (coluna, de, ate, desl, mostra_pct) in enumerate(VIRADAS):
    trecho = ibov[coluna][de:ate]
    dia, valor = (trecho.idxmax(), trecho.max()) if coluna == "High" else (trecho.idxmin(), trecho.min())
    viradas.append((dia, valor))
    texto = pontos(valor)
    if mostra_pct:  # mostra quanto mudou desde o ponto anterior
        quebra = " " if k == len(VIRADAS) - 1 else "\n"  # o último fica numa linha só, para não bater no vizinho
        texto += f"{quebra}({(valor / viradas[k - 1][1] - 1) * 100:+.0f}%)"
    ax.scatter([dia], [valor], s=60, color=AZUL, zorder=4, edgecolor="white", linewidth=1.5)
    ax.annotate(texto, (dia, valor), xytext=desl, textcoords="offset points", fontsize=11, fontweight="bold",
                color=VERDE if "+" in texto else (VERMELHO if "-" in texto else CINZA),
                ha="center" if desl[0] == 0 else ("left" if desl[0] > 0 else "right"),
                va="bottom" if desl[1] > 0 else "top")
    print(f"{dia:%d/%m/%Y}: {texto.replace(chr(10), ' ')}")

# a faixa da lateralização: o preço fica preso entre um piso e um teto
lateral = ibov["2021-12":"2023-10"]
piso, teto = lateral["Low"].min(), lateral["High"].max()
a, b = pd.Timestamp("2021-12-06"), pd.Timestamp("2023-10-30")
for nivel in (piso, teto):
    ax.hlines(nivel, a, b, color=AZUL, linestyle="--", linewidth=1.3, zorder=2)
ax.text(b, teto + 1500, f"teto ≈ {pontos(teto)}", ha="right", va="bottom", fontsize=10, color=AZUL, fontweight="bold")
ax.text(b, piso - 1500, f"piso ≈ {pontos(piso)}", ha="right", va="top", fontsize=10, color=AZUL, fontweight="bold")
print(f"lateral: piso {pontos(piso)}, teto {pontos(teto)}")

# o circuit breaker: na semana de 26/10/2026 o índice despencou logo depois do 2º turno da eleição
semana = ibov.loc[CIRCUIT_BREAKER]
queda = (semana["Low"] / FECH_ANTERIOR - 1) * 100
ax.annotate(f"CIRCUIT BREAKER\n26/10/2026\n{pontos(semana['Low'])} ({queda:+.0f}% em um dia)",
            (CIRCUIT_BREAKER, semana["Low"]), xytext=(pd.Timestamp("2025-12-15"), 80_000), textcoords="data",
            fontsize=10.5,
            fontweight="bold", color=VERMELHO, ha="center", va="top",
            arrowprops={"arrowstyle": "->", "color": VERMELHO, "linewidth": 1.8},
            bbox={"boxstyle": "round", "facecolor": "white", "edgecolor": VERMELHO})
print(f"circuit breaker: mínima {pontos(semana['Low'])} ({queda:+.1f}%)")

ax.set_title(
    "Os 3 regimes de mercado no Ibovespa (IBOV): alta, baixa e lateral\n"
    "candles semanais (timeframe de 1 semana), de 01/2020 a 10/2026; os pontos azuis marcam as viradas",
    fontsize=11.5,
    loc="left",
    fontweight="bold",
)
ax.set_ylabel("Ibovespa (pontos)", fontsize=10)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: pontos(v)))
ax.set_ylim(40_000, 250_000)
ax.set_xlim(pd.Timestamp(INICIO), ibov.index[-1] + pd.Timedelta(days=7))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.grid(axis="y", alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
fig.savefig(PASTA / "cap2_7_regimes_ibov.png", dpi=200)
print("salvo cap2_7_regimes_ibov.png")
