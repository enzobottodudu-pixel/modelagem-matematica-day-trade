# GRÁFICO 4 — Análise fundamentalista: inflação x juros nos EUA

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

site = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="

# 1. Baixar o índice de preços (CPI) e a taxa de juros do Fed
cpi = pd.read_csv(site + "CPIAUCSL")
juros = pd.read_csv(site + "FEDFUNDS")
cpi["observation_date"] = pd.to_datetime(cpi["observation_date"])
juros["observation_date"] = pd.to_datetime(juros["observation_date"])

# 2. A fonte não tem o dado de outubro de 2025; ele é preenchido
#    com o valor entre setembro e novembro (interpolação)
cpi["CPIAUCSL"] = cpi["CPIAUCSL"].interpolate()

# 3. Inflação = quanto os preços subiram em 12 meses, em %
cpi["inflacao"] = cpi["CPIAUCSL"].pct_change(12) * 100

# 4. Ficar só com os dados desde 2020
cpi = cpi[cpi["observation_date"] >= "2020-01-01"]
juros = juros[juros["observation_date"] >= "2020-01-01"]

# 5. As duas linhas no mesmo gráfico (as duas estão em % ao ano)
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(cpi["observation_date"], cpi["inflacao"], color="orange", label="Inflação (CPI) acumulada em 12 meses")
ax.plot(juros["observation_date"], juros["FEDFUNDS"], color="red", label="Taxa de juros básica dos EUA (Fed)")
ax.axhline(2, color="gray", linestyle="--", label="Referência: meta de 2% do Fed")

ax.set_title("Inflação e juros nos EUA — dados mensais, desde 01/2020")
ax.set_ylabel("% ao ano")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))  # datas como 01/2020
ax.legend()
ax.grid(alpha=0.3)
plt.savefig("grafico4_inflacao_juros.png", dpi=200, bbox_inches="tight")
plt.show()
