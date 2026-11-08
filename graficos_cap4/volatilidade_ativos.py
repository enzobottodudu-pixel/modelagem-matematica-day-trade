"""Figura da 4.2: os 9 ativos do TCC ordenados da menor para a maior volatilidade.

Volatilidade = desvio-padrão dos retornos diários (timeframe diário),
de 12/07/2026 a 09/10/2026, com os dados da pasta "Dados 90 dias".
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DADOS = Path(__file__).resolve().parent.parent / "Dados 90 dias"
ARQUIVOS = {
    "EUR/USD": "EURUSD/EURUSD_24h.csv",
    "SPY": "SPY/SPY_24h.csv",
    "NQ": "NQ/NQ_24h.csv",
    "IBOV": "IBOV/IBOV_24h.csv",
    "PETR4": "PETR4/PETR4_24h.csv",
    "ITUB4": "ITUB4/ITUB4_24h.csv",
    "BTC/USD": "BTCUSD/BTCUSD_24h.csv",
    "Tesla": "TESLA/TESLA_24h.csv",
    "MGLU3": "MGLU3/MGLU3_24h.csv",
}

volatilidade = {}
for nome, arquivo in ARQUIVOS.items():
    fechamento = pd.read_csv(DADOS / arquivo, index_col=0)["Close"]
    volatilidade[nome] = fechamento.pct_change().dropna().std() * 100

serie = pd.Series(volatilidade).sort_values()
cores = plt.cm.RdYlBu_r([i / (len(serie) - 1) * 0.85 + 0.075 for i in range(len(serie))])

fig, ax = plt.subplots(figsize=(9, 5))
barras = ax.barh(serie.index, serie.values, color=cores, edgecolor="dimgray", linewidth=0.6)
for barra, valor in zip(barras, serie.values):
    ax.text(valor + 0.08, barra.get_y() + barra.get_height() / 2, f"{valor:.2f}%".replace(".", ","), va="center")
ax.invert_yaxis()
ax.set_xlim(0, serie.max() * 1.15)
ax.set_xlabel("Desvio-padrão dos retornos diários (%)")
ax.set_title("Timeframe diário, de 12/07/2026 a 09/10/2026", fontsize=10, loc="left", color="gray")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.grid(axis="x", linestyle=":", alpha=0.6)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(Path(__file__).parent / "fig24_volatilidade_ativos.png", dpi=200)
print(serie.round(2))
