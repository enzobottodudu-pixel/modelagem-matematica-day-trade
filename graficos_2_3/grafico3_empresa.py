# GRÁFICO 3 — Análise fundamentalista: lucro da NVIDIA x preço da ação

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import yfinance as yf

empresa = yf.Ticker("NVDA")

# 1. Lucro líquido de cada ano fiscal (em bilhões de dólares)
lucro = empresa.income_stmt.loc["Net Income"].dropna() / 1_000_000_000
lucro = lucro.sort_index()
anos = [str(data.year) for data in lucro.index]

# 2. Preço mensal da ação no mesmo período
preco = empresa.history(start=lucro.index[0], interval="1mo")

# 3. Dois gráficos lado a lado
fig, (esquerda, direita) = plt.subplots(1, 2, figsize=(12, 4.5))

esquerda.bar(anos, lucro.values, color="green")
esquerda.set_title("Lucro líquido da NVIDIA — dados anuais (ano fiscal)")
esquerda.set_ylabel("Lucro (bilhões de US$)")
esquerda.grid(alpha=0.3, axis="y")

direita.plot(preco.index, preco["Close"], color="blue", label="Preço da ação")
# Em 10/06/2024 cada ação virou 10 (desdobramento). O Yahoo divide os
# preços antigos por 10 para que todo o gráfico fique na mesma escala.
direita.axvline(preco.index[0].replace(year=2024, month=6, day=10), color="gray",
                linestyle="--", label="Desdobramento de 10 para 1 (jun/2024)")
direita.set_title("Preço da NVIDIA — timeframe mensal (ajustado)")
direita.set_ylabel("Preço ajustado (US$)")
direita.legend(loc="upper left")
direita.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))  # datas como 01/2024
direita.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("grafico3_empresa.png", dpi=200, bbox_inches="tight")
plt.show()
