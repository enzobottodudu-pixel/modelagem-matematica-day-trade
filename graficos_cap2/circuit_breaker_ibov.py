"""3.7.5 — O circuit breaker de 26/10/2026 no Ibovespa, em candles de 5 minutos.

Rodar: py -3.14 circuit_breaker_ibov.py   →   salva cap2_8_circuit_breaker.png nesta pasta.
Dados: Yahoo Finance (^BVSP), candles de 1 minuto juntados de 5 em 5. Antes das 10h46 o Yahoo só repete o
fechamento anterior (não houve negócios), então esses minutos são descartados.
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from matplotlib.ticker import FuncFormatter

PASTA = Path(__file__).parent
DIA = "2026-10-26"
FECH_ANTERIOR = 205_083  # fechamento de sexta, 23/10/2026
AZUL, CINZA, VERMELHO, VERDE = "#1f4e79", "#4d4d4d", "#d73027", "#1a9850"

minuto = yf.download("^BVSP", period="5d", interval="1m", auto_adjust=False, progress=False)
minuto.columns = minuto.columns.get_level_values(0)
minuto.index = minuto.index.tz_localize(None)  # já vem no horário de Brasília
minuto = minuto.loc[DIA].between_time("10:46", "16:59")
# junta os minutos de 5 em 5: abre no 1º, fecha no último, máxima e mínima de todos
ibov = minuto.resample("5min").agg({"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna()


def pontos(valor):
    return f"{valor / 1000:.1f} mil".replace(".", ",")  # 205083 -> "205,1 mil"


def hora(texto):
    return pd.Timestamp(f"{DIA} {texto}")


fig, ax = plt.subplots(figsize=(11, 5.8))

# o período sem negócios: pregão parado pelo circuit breaker e leilão de reabertura
ax.axvspan(hora("10:00"), hora("10:45"), color="#fcebea", zorder=0)
ax.text(hora("10:22"), 196_000, "PREGÃO\nPARADO\n(circuit\nbreaker)", ha="center", va="center", fontsize=10,
        fontweight="bold", color=VERMELHO)

# as linhas de referência: o fechamento anterior e os gatilhos de −10%, −15% e −20%
ax.hlines(FECH_ANTERIOR, hora("10:00"), hora("17:00"), color=CINZA, linewidth=1.3)
ax.text(hora("16:58"), FECH_ANTERIOR + 700, f"fechamento anterior (23/10): {pontos(FECH_ANTERIOR)}", ha="right",
        va="bottom", fontsize=10, color=CINZA, fontweight="bold")
for queda, nome in ((10, "1º circuit breaker"), (15, "2º circuit breaker"), (20, "3º circuit breaker")):
    nivel = FECH_ANTERIOR * (1 - queda / 100)
    ax.hlines(nivel, hora("10:00"), hora("17:00"), color=VERMELHO, linestyle="--", linewidth=1.1)
    ax.text(hora("16:58"), nivel - 500, f"−{queda}% = {pontos(nivel)} ({nome})", ha="right", va="top",
            fontsize=9.5, color=VERMELHO)

# candles: corpo (abertura → fechamento) e pavio (mínima → máxima)
largura = pd.Timedelta(minutes=3.5)
for momento, c in ibov.iterrows():
    cor = VERDE if c["Close"] >= c["Open"] else VERMELHO
    ax.vlines(momento, c["Low"], c["High"], color=cor, linewidth=1, zorder=3)
    ax.bar(momento, max(abs(c["Close"] - c["Open"]), 60), largura, bottom=min(c["Open"], c["Close"]), color=cor,
           zorder=3, align="center")

# o salto: o pregão parou em 205 mil e só voltou com o preço lá embaixo
ax.annotate("", (hora("10:45"), ibov["Open"].iloc[0]), xytext=(hora("10:45"), FECH_ANTERIOR),
            arrowprops={"arrowstyle": "->", "color": VERMELHO, "linewidth": 1.8, "linestyle": ":"})

# o pior momento e o fechamento do dia
minimo, quando = ibov["Low"].min(), ibov["Low"].idxmin()
fechamento = ibov["Close"].iloc[-1]
for momento, valor, texto, desl in (
    (quando, minimo, f"mínima: {pontos(minimo)}\n({(minimo / FECH_ANTERIOR - 1) * 100:+.1f}%)", (14, -6)),
    (ibov.index[-1], fechamento, f"fechamento: {pontos(fechamento)}\n({(fechamento / FECH_ANTERIOR - 1) * 100:+.1f}%)",
     (-6, 28)),
):
    ax.scatter([momento], [valor], s=60, color=AZUL, zorder=4, edgecolor="white", linewidth=1.5)
    ax.annotate(texto.replace(".", ",").replace("−", "-"), (momento, valor), xytext=desl, textcoords="offset points",
                fontsize=10.5, fontweight="bold", color=AZUL, ha="left" if desl[0] > 0 else "right", va="top")
    print(f"{momento:%H:%M}: {texto.replace(chr(10), ' ')}")

ax.set_title(
    "Circuit breaker no Ibovespa (IBOV) em 26/10/2026, dia seguinte ao 2º turno da eleição presidencial\n"
    "candles de 5 minutos (timeframe de 5 min); as linhas tracejadas marcam as quedas que param o pregão",
    fontsize=11.5,
    loc="left",
    fontweight="bold",
)
ax.set_ylabel("Ibovespa (pontos)", fontsize=10)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v / 1000:.0f} mil"))
ax.set_ylim(160_000, 210_000)
ax.set_xlim(hora("10:00"), hora("17:00"))
ax.xaxis.set_major_locator(mdates.HourLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Hh"))
ax.set_xlabel("horário de Brasília", fontsize=10)
ax.grid(axis="y", alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
fig.savefig(PASTA / "cap2_8_circuit_breaker.png", dpi=200)
print("salvo cap2_8_circuit_breaker.png")
