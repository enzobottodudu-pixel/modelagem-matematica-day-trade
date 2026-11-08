# GRÁFICO 2 — Análise fundamentalista: juros dos EUA x preço do SPY

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

# 1. Baixar a taxa de juros do banco central americano (Fed), do site FRED
juros = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS")
juros["observation_date"] = pd.to_datetime(juros["observation_date"])
juros = juros[juros["observation_date"] >= "2020-01-01"]

# 2. Baixar o preço mensal do SPY desde 2020
spy = yf.download("SPY", start="2020-01-01", interval="1mo", auto_adjust=True)
spy.columns = spy.columns.get_level_values(0)

# 3. Dois gráficos, um embaixo do outro, com as mesmas datas
fig, (cima, baixo) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)

cima.plot(juros["observation_date"], juros["FEDFUNDS"], color="red")
cima.set_title("Taxa de juros básica dos EUA (Fed) — dados mensais")
cima.set_ylabel("Juros ao ano (%)")
cima.grid(alpha=0.3)

baixo.plot(spy.index, spy["Close"], color="blue")
baixo.set_title("Preço do SPY — timeframe mensal (fechamento de cada mês)")
baixo.set_ylabel("Preço (US$)")
baixo.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("grafico2_juros_spy.png", dpi=200, bbox_inches="tight")
plt.show()
