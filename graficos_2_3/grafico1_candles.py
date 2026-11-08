# GRÁFICO 1 — Análise técnica: candles do SPY com duas médias móveis

import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

# 1. Baixar os preços diários do SPY do último ano
#    (as médias precisam dos dias ANTERIORES para já começarem no gráfico)
dados = yf.download("SPY", period="1y", interval="1d", auto_adjust=True)
dados = dados[dados.index < pd.Timestamp.now().normalize()]  # só pregões completos (tira o dia de hoje)
dados.columns = dados.columns.get_level_values(0)

# 2. Calcular as médias móveis de 20 e de 50 dias
dados["MM20"] = dados["Close"].rolling(20).mean()
dados["MM50"] = dados["Close"].rolling(50).mean()

# 3. Mostrar só os últimos 6 meses (cerca de 126 pregões)
dados = dados.tail(126)

# 4. Cada pregão ganha uma posição 0, 1, 2, 3...
#    (assim os fins de semana não deixam buracos entre os candles)
x = range(len(dados))

# 5. Desenhar um candle por dia
fig, ax = plt.subplots(figsize=(12, 5))
for i, (data, candle) in enumerate(dados.iterrows()):
    if candle["Close"] >= candle["Open"]:
        cor = "green"   # dia de alta
    else:
        cor = "red"     # dia de queda
    # pavio: vai da mínima até a máxima do dia
    ax.vlines(i, candle["Low"], candle["High"], color=cor, linewidth=1)
    # corpo: vai da abertura até o fechamento
    altura = abs(candle["Close"] - candle["Open"])
    base = min(candle["Open"], candle["Close"])
    ax.bar(i, max(altura, 0.3), bottom=base, width=0.7, color=cor)

# 6. Desenhar as médias móveis por cima
ax.plot(x, dados["MM20"], color="blue", label="MM20: média móvel simples de 20 períodos (20 dias)")
ax.plot(x, dados["MM50"], color="orange", label="MM50: média móvel simples de 50 períodos (50 dias)")

# 7. Mostrar uma data a cada 21 pregões (mais ou menos 1 mês)
posicoes = list(range(0, len(dados), 21))
datas = [dados.index[p].strftime("%d/%m/%Y") for p in posicoes]
ax.set_xticks(posicoes, datas)

ax.set_title("SPY — timeframe diário (1 candle = 1 dia), últimos 6 meses")
ax.set_ylabel("Preço (US$)")
ax.legend(loc="lower right")
ax.grid(alpha=0.3)
plt.savefig("grafico1_candles.png", dpi=200, bbox_inches="tight")
plt.show()
