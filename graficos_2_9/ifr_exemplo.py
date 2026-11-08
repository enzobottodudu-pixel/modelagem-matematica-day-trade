"""2.9.3 — Exemplo do IFR em candles reais: um dia do BTC/USD com uma compra e uma venda.

03/08/2026, candles de 30 min, horário UTC. IFR de 14 períodos (média de Wilder), calculado com os dias anteriores.
Regra só de exemplo (as regras de verdade saem da reunião com o orientador):
- o candle fecha com IFR 30 ou menos (sobrevendido) → COMPRA no fechamento dele;
- o candle fecha com IFR 70 ou mais (sobrecomprado) → VENDE no fechamento dele;
- alvo: o IFR voltar a 50 (o meio); stop: o preço andar 1% contra a operação.
Rodar: py -3.14 ifr_exemplo.py   →   salva ifr_exemplo.png nesta pasta.
Dados: Binance (par BTCUSDT), candles de 30 min (pasta "Dados 90 dias").
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PASTA = Path(__file__).parent
DADOS = PASTA.parent / "Dados 90 dias" / "BTCUSD" / "BTCUSD_30min.csv"
DIA = "2026-08-03"
PERIODO = 14  # IFR de 14 candles
STOP = 0.01  # stop hipotético: 1% contra a operação, a partir da entrada
VERDE, VERMELHO, AZUL, CINZA, LARANJA = "#1a9850", "#d73027", "#2166ac", "#808080", "#e66101"


def dolares(v):
    return f"US${v:,.0f}".replace(",", ".")  # 63766.4 -> "US$63.766"


todos = pd.read_csv(DADOS, parse_dates=["Data"])

# IFR: média das altas ÷ média das quedas dos últimos 14 candles (Wilder), virado numa escala de 0 a 100
variacao = todos["Close"].diff()
media_altas = variacao.clip(lower=0).ewm(alpha=1 / PERIODO, adjust=False).mean()
media_quedas = (-variacao.clip(upper=0)).ewm(alpha=1 / PERIODO, adjust=False).mean()
todos["IFR"] = 100 - 100 / (1 + media_altas / media_quedas)

c = todos[todos["Data"].astype(str).str.startswith(DIA)].reset_index(drop=True)
n = len(c)
ifr = c["IFR"]

# as operações do dia com a regra de exemplo
operacoes = []  # (lado, candle de entrada, preço de entrada, candle de saída, preço de saída, stop, motivo)
aberta = None
for i in range(1, n):
    if aberta is None:
        if ifr[i] <= 30:
            aberta = ("COMPRA", i, c["Close"][i], c["Close"][i] * (1 - STOP))
        elif ifr[i] >= 70:
            aberta = ("VENDA", i, c["Close"][i], c["Close"][i] * (1 + STOP))
    else:
        lado, ie, pe, stop = aberta
        if (lado == "VENDA" and c["High"][i] >= stop) or (lado == "COMPRA" and c["Low"][i] <= stop):
            operacoes.append((lado, ie, pe, i, stop, stop, "no stop"))
            aberta = None
        elif (lado == "VENDA" and ifr[i] <= 50) or (lado == "COMPRA" and ifr[i] >= 50):
            operacoes.append((lado, ie, pe, i, c["Close"][i], stop, "no alvo"))
            aberta = None

fig, (ax, axi) = plt.subplots(2, 1, figsize=(13, 8), sharex=True, gridspec_kw={"height_ratios": [3, 1.6]})

# os candles do dia
for i, k in c.iterrows():
    cor = VERDE if k["Close"] >= k["Open"] else VERMELHO
    ax.vlines(i, k["Low"], k["High"], color=cor, linewidth=1.4, zorder=3)
    ax.bar(i, max(abs(k["Close"] - k["Open"]), 8), 0.6, bottom=min(k["Open"], k["Close"]), color=cor, zorder=3)

# o IFR embaixo, com as linhas de 70 (sobrecomprado), 30 (sobrevendido) e 50 (o alvo)
axi.plot(range(n), ifr, color="black", linewidth=1.8, zorder=3)
axi.hlines(70, -0.7, n - 0.6, color=VERMELHO, linestyle=":", linewidth=1.5)
axi.hlines(30, -0.7, n - 0.6, color=VERDE, linestyle=":", linewidth=1.5)
axi.hlines(50, -0.7, n - 0.6, color=AZUL, linestyle="--", linewidth=1.2)
axi.text(n - 0.3, 70, "70 sobrecomprado", color=VERMELHO, fontsize=9.5, fontweight="bold", va="center")
axi.text(n - 0.3, 30, "30 sobrevendido", color=VERDE, fontsize=9.5, fontweight="bold", va="center")
axi.text(n - 0.3, 50, "50 = alvo", color=AZUL, fontsize=9.5, fontweight="bold", va="center")

# entrada (círculo) e saída (quadrado) nos dois painéis, com o texto num lugar vazio
for lado, ie, pe, isai, ps, stop, motivo in operacoes:
    cor = VERMELHO if lado == "VENDA" else VERDE
    lucro = (pe / ps - 1) if lado == "VENDA" else (ps / pe - 1)
    acima = lado == "VENDA"
    # o stop hipotético: um tracinho laranja do candle seguinte à entrada até o da saída
    ax.hlines(stop, ie + 0.3, isai + 0.4, color=LARANJA, linewidth=2, zorder=4)
    ax.text(isai + 0.5, stop, f"stop {dolares(stop)}", color=LARANJA, fontsize=9.5, fontweight="bold",
            va="center")
    for eixo, y_ent, y_sai in ((ax, pe, ps), (axi, ifr[ie], ifr[isai])):
        eixo.scatter([ie], [y_ent], s=140, color="white", edgecolor=cor, linewidth=2.5, zorder=5)
        eixo.scatter([isai], [y_sai], s=150, marker="s", color=cor, edgecolor="black", linewidth=1.8, zorder=6)
    porcento = f"{lucro * 100:.1f}".replace(".", ",")  # 1.16 -> "1,2"
    texto = (f"{lado} a {dolares(pe)} ({c['Data'][ie]:%Hh%M}), IFR {ifr[ie]:.0f}\n"
             f"sai {motivo} a {dolares(ps)} ({c['Data'][isai]:%Hh%M}): +{porcento}%")
    ax.text((ie + isai) / 2, stop + (180 if acima else -180), texto, color=cor, fontsize=10.5, fontweight="bold",
            ha="center", va="bottom" if acima else "top")

# legenda dos símbolos
ax.scatter([], [], s=140, color="white", edgecolor="black", linewidth=2.5, label="entrada")
ax.scatter([], [], s=150, marker="s", color="white", edgecolor="black", linewidth=1.8, label="saída")
ax.plot([], [], color=LARANJA, linewidth=2, label="stop (hipotético)")
ax.legend(loc="upper left", fontsize=10, frameon=False)

ax.set_title("O IFR no BTC/USD em 03/08/2026 (segunda-feira): compra no exagero da queda e venda no da alta\n"
             "candles de 30 min (timeframe de 30 minutos), horário UTC, IFR de 14 períodos\n"
             "alvo e stop hipotéticos, só de exemplo", fontsize=12.5, fontweight="bold", loc="left")
stops = [op[5] for op in operacoes]
ax.set_ylim(min([c["Low"].min(), *stops]) - 600, max([c["High"].max(), *stops]) + 600)
ax.set_xlim(-0.7, n + 4.5)
ax.set_ylabel("BTC/USD (US$)")
ax.yaxis.set_major_formatter(lambda v, _: dolares(v))
ax.grid(axis="y", alpha=0.3)
axi.set_ylim(0, 100)
axi.set_yticks([0, 30, 50, 70, 100])
axi.set_ylabel("IFR (14)")
axi.set_xticks(range(0, n, 2), [f"{h:%Hh%M}" for h in c["Data"][::2]], rotation=45, fontsize=8.5)
for a in (ax, axi):
    for lado in ("top", "right"):
        a.spines[lado].set_visible(False)

fig.tight_layout()
fig.savefig(PASTA / "ifr_exemplo.png", dpi=200)
for op in operacoes:
    print(op)
print("salvo ifr_exemplo.png")
