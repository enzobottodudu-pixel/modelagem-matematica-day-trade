"""2.4 — O NQ (futuro do Nasdaq-100) na covid, em candles semanais, com o VIX embaixo.

Rodar: py -3.14 nq_covid.py   →   salva cap2_5_nq_covid.png nesta pasta.
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from matplotlib.ticker import FuncFormatter

PASTA = Path(__file__).parent
INICIO, FIM = "2019-07-01", "2021-01-01"
VERDE, VERMELHO, CINZA, LARANJA = "#1a9850", "#d73027", "#4d4d4d", "#f28e2b"


def semanal(codigo):
    tabela = yf.download(codigo, start=INICIO, end=FIM, interval="1wk", auto_adjust=False, progress=False)
    tabela.columns = tabela.columns.get_level_values(0)  # tira o nome do ativo do cabeçalho
    return tabela.dropna()


def pontos(valor):
    return f"{valor:,.0f}".replace(",", ".")  # 9736 -> "9.736"


nq, vix = semanal("NQ=F"), semanal("^VIX")

# topo antes da covid, fundo na covid e quanto caiu
antes = nq[:"2020-03-01"]
topo_dia, topo = antes["High"].idxmax(), antes["High"].max()
depois = nq[topo_dia:"2020-06-01"]
fundo_dia, fundo = depois["Low"].idxmin(), depois["Low"].min()
queda = (fundo / topo - 1) * 100
volta = nq[fundo_dia:][nq[fundo_dia:]["Close"] > topo].index[0]  # 1ª semana fechando acima do topo
print(f"topo {pontos(topo)} ({topo_dia:%d/%m/%Y}), fundo {pontos(fundo)} ({fundo_dia:%d/%m/%Y}), queda {queda:.1f}%")
print(f"voltou ao topo na semana de {volta:%d/%m/%Y}; VIX máx semanal {vix['High'].max():.0f}")

fig, (cima, baixo) = plt.subplots(2, 1, figsize=(11, 6.6), sharex=True, gridspec_kw={"height_ratios": [3, 1.2]})

# candles: corpo (abertura → fechamento) e pavio (mínima → máxima)
largura = pd.Timedelta(days=4.5)
for dia, c in nq.iterrows():
    cor = VERDE if c["Close"] >= c["Open"] else VERMELHO
    cima.vlines(dia, c["Low"], c["High"], color=cor, linewidth=0.9)
    cima.bar(dia, abs(c["Close"] - c["Open"]), largura, bottom=min(c["Open"], c["Close"]), color=cor)

cima.axvspan(topo_dia, fundo_dia + pd.Timedelta(days=7), color=VERMELHO, alpha=0.08)
cima.annotate(
    f"topo antes da covid\n{pontos(topo)} pontos ({topo_dia:%d/%m/%Y})",
    (topo_dia, topo),
    xytext=(-150, 18),
    textcoords="offset points",
    fontsize=9,
    color=CINZA,
    arrowprops={"arrowstyle": "->", "color": CINZA},
)
cima.annotate(
    f"fundo na covid\n{pontos(fundo)} pontos ({fundo_dia:%d/%m/%Y})\nqueda de {-queda:.0f}% em {(fundo_dia - topo_dia).days // 7} semanas",
    (fundo_dia, fundo),
    xytext=(30, -10),
    textcoords="offset points",
    fontsize=9,
    color=VERMELHO,
    fontweight="bold",
    arrowprops={"arrowstyle": "->", "color": VERMELHO},
)
cima.annotate(
    f"já voltou ao topo\n(semana de {volta:%d/%m/%Y})",
    (volta, nq.loc[volta, "Close"]),
    xytext=(-170, 70),
    textcoords="offset points",
    fontsize=9,
    color=VERDE,
    fontweight="bold",
    arrowprops={"arrowstyle": "->", "color": VERDE},
)
cima.set_title(
    "NQ (futuro do Nasdaq-100) na pandemia de covid\ncandles semanais (timeframe de 1 semana), de 07/2019 a 12/2020",
    fontsize=11,
    loc="left",
    fontweight="bold",
)
cima.set_ylabel("NQ (pontos do índice)", fontsize=9)
cima.yaxis.set_major_formatter(FuncFormatter(lambda v, _: pontos(v)))

baixo.plot(vix.index, vix["Close"], color=CINZA, linewidth=1.4)
baixo.axhline(20, color=LARANJA, linestyle="--", linewidth=1.1)
baixo.text(vix.index[0], 21.5, "acima de 20: mercado nervoso", fontsize=8, color=LARANJA)
baixo.set_title("VIX no mesmo período — fechamento semanal", fontsize=10, loc="left")
baixo.set_ylabel("VIX (pontos)", fontsize=9)

for ax in (cima, baixo):
    ax.grid(alpha=0.25)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
baixo.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
baixo.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
fig.tight_layout()
fig.savefig(PASTA / "cap2_5_nq_covid.png", dpi=200)
print("salvo cap2_5_nq_covid.png")
