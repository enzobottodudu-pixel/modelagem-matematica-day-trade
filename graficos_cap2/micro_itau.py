"""3.7.3 — Indicadores microeconômicos de uma empresa: o Itaú Unibanco (ITUB4).

Rodar: py -3.14 micro_itau.py   →   salva cap2_8_micro_itau.png nesta pasta.
Dados: Yahoo Finance (demonstrativos anuais, dividendos e preço mensal), em reais.
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import yfinance as yf
from matplotlib.ticker import FuncFormatter

PASTA = Path(__file__).parent
AZUL, VERDE, LARANJA, CINZA = "#1f4e79", "#1a9850", "#f28e2b", "#4d4d4d"


def virgula(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",")


acao = yf.Ticker("ITUB4.SA")
dre = acao.income_stmt  # demonstração de resultado anual
anos = sorted(c for c in dre.columns if dre[c].notna()["Net Income"])
receita = [dre.loc["Total Revenue", a] / 1e9 for a in anos]
lucro = [dre.loc["Net Income", a] / 1e9 for a in anos]
lpa = [dre.loc["Diluted EPS", a] for a in anos]
rotulos = [str(a.year) for a in anos]
div = acao.dividends
div = (
    div[div.index.year.isin([a.year for a in anos])]
    .groupby(div[div.index.year.isin([a.year for a in anos])].index.year)
    .sum()
)
preco = acao.history(start="2022-01-01", interval="1mo")["Close"].dropna()
pl = preco.iloc[-1] / lpa[-1]
print("anos", rotulos, "receita", [round(x, 1) for x in receita], "lucro", [round(x, 1) for x in lucro])
print(
    "LPA", [round(x, 2) for x in lpa], "dividendos", div.round(2).to_dict(), f"preço {preco.iloc[-1]:.2f} P/L {pl:.1f}"
)

fig, ((a, b), (c, d)) = plt.subplots(2, 2, figsize=(12, 8))
x = range(len(anos))
a.bar([i - 0.2 for i in x], receita, 0.4, color=AZUL, label="receita")
a.bar([i + 0.2 for i in x], lucro, 0.4, color=VERDE, label="lucro líquido")
for i in x:
    a.text(i - 0.2, receita[i] + 2, virgula(receita[i], 0), ha="center", fontsize=10)
    a.text(i + 0.2, lucro[i] + 2, virgula(lucro[i], 0), ha="center", fontsize=10, color=VERDE, fontweight="bold")
a.set_title("Receita e lucro líquido por ano (R$ bilhões)", loc="left", fontweight="bold")
a.legend(frameon=False, fontsize=10)
a.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"R${v:.0f} bi"))

b.bar(x, lpa, 0.55, color=VERDE)
for i in x:
    b.text(i, lpa[i] + 0.06, "R$" + virgula(lpa[i], 2), ha="center", fontsize=10, fontweight="bold")
b.set_title("Lucro por ação (LPA) por ano", loc="left", fontweight="bold")
b.yaxis.set_major_formatter(FuncFormatter(lambda v, _: "R$" + virgula(v, 1)))

c.bar(x, [div.get(a_.year, 0) for a_ in anos], 0.55, color=LARANJA)
for i, a_ in enumerate(anos):
    c.text(
        i,
        div.get(a_.year, 0) + 0.06,
        "R$" + virgula(div.get(a_.year, 0), 2),
        ha="center",
        fontsize=10,
        fontweight="bold",
    )
c.set_title("Dividendos pagos por ação por ano", loc="left", fontweight="bold")
c.yaxis.set_major_formatter(FuncFormatter(lambda v, _: "R$" + virgula(v, 1)))
for ax in (a, b, c):
    ax.set_xticks(list(x), rotulos)

d.plot(preco.index, preco.values, color=AZUL, linewidth=2)
d.set_title("Preço da ação ITUB4 (fechamento mensal)", loc="left", fontweight="bold")
d.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"R${v:.0f}"))
d.xaxis.set_major_locator(mdates.YearLocator())
d.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
d.text(
    0.02,
    0.95,
    f"P/L = preço ÷ LPA = {virgula(preco.iloc[-1], 2)} ÷ {virgula(lpa[-1], 2)} ≈ {virgula(pl)}",
    transform=d.transAxes,
    va="top",
    fontsize=10,
    bbox={"boxstyle": "round,pad=0.4", "facecolor": "#eef3f9", "edgecolor": AZUL},
)

for ax in (a, b, c, d):
    ax.grid(axis="y", alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
fig.suptitle(
    f"Itaú Unibanco (ITUB4): indicadores microeconômicos da empresa, de {rotulos[0]} a {rotulos[-1]}",
    fontsize=13,
    fontweight="bold",
    x=0.01,
    ha="left",
)
fig.tight_layout()
fig.savefig(PASTA / "cap2_8_micro_itau.png", dpi=200)
print("salvo cap2_8_micro_itau.png")
