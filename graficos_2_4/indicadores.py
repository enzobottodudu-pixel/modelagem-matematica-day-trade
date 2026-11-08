"""
GRÁFICOS DA SEÇÃO 2.4 — exemplos de indicadores técnicos no SPY

Todos usam o timeframe DIÁRIO (1 candle = 1 dia) e mostram os últimos 6 meses.
O último ano inteiro é baixado para que os indicadores já apareçam desde o
primeiro dia do gráfico (eles precisam dos dias anteriores para serem calculados).

A VWAP é a exceção: usa o timeframe de 1 HORA nos últimos 5 pregões.

Gera 6 imagens nesta pasta:
  indicador1_medias_moveis.png
  indicador2_ifr.png
  indicador3_bollinger.png
  indicador4_macd.png
  indicador5_volume_financeiro.png
  indicador6_vwap.png
"""

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

PASTA = Path(__file__).parent

# ---------------------------------------------------------------------------
# DADOS: SPY diário do último ano
# ---------------------------------------------------------------------------
dados = yf.download("SPY", period="1y", interval="1d", auto_adjust=True)
dados = dados[dados.index < pd.Timestamp.now().normalize()]  # só pregões completos (tira o dia de hoje)
dados.columns = dados.columns.get_level_values(0)
preco = dados["Close"]

# ---------------------------------------------------------------------------
# CÁLCULO DOS INDICADORES (os períodos ficam aqui em cima, fáceis de ver)
# ---------------------------------------------------------------------------
MM_CURTA, MM_LONGA = 9, 21                 # médias móveis exponenciais
IFR_PERIODO = 14                           # IFR de Wilder
BB_PERIODO, BB_DESVIOS = 20, 2             # Bandas de Bollinger
MACD_RAPIDA, MACD_LENTA, MACD_SINAL = 12, 26, 9

# Médias móveis exponenciais (dão mais peso aos dias mais recentes)
dados["mme_curta"] = preco.ewm(span=MM_CURTA, adjust=False).mean()
dados["mme_longa"] = preco.ewm(span=MM_LONGA, adjust=False).mean()

# IFR: compara a média das altas com a média das quedas (vai de 0 a 100)
variacao = preco.diff()
media_altas = variacao.clip(lower=0).ewm(alpha=1 / IFR_PERIODO, adjust=False).mean()
media_quedas = (-variacao.clip(upper=0)).ewm(alpha=1 / IFR_PERIODO, adjust=False).mean()
dados["ifr"] = 100 - 100 / (1 + media_altas / media_quedas)

# Bandas de Bollinger: média de 20 dias ± 2 desvios-padrão
dados["bb_meio"] = preco.rolling(BB_PERIODO).mean()
desvio = preco.rolling(BB_PERIODO).std()
dados["bb_cima"] = dados["bb_meio"] + BB_DESVIOS * desvio
dados["bb_baixo"] = dados["bb_meio"] - BB_DESVIOS * desvio

# MACD: diferença entre uma média exponencial rápida (12) e uma lenta (26)
dados["macd"] = (preco.ewm(span=MACD_RAPIDA, adjust=False).mean()
                 - preco.ewm(span=MACD_LENTA, adjust=False).mean())
dados["macd_sinal"] = dados["macd"].ewm(span=MACD_SINAL, adjust=False).mean()
dados["macd_hist"] = dados["macd"] - dados["macd_sinal"]

# Volume financeiro: quantos dólares foram negociados no dia (preço x quantidade)
dados["vol_financeiro"] = preco * dados["Volume"] / 1_000_000_000   # em bilhões de US$

# Mostrar só os últimos 6 meses (cerca de 126 pregões)
dados = dados.tail(126)
preco = dados["Close"]


def formatar_datas(ax):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))  # datas como 04/2026
    ax.grid(alpha=0.3)


def salvar(fig, nome):
    fig.tight_layout()
    fig.savefig(PASTA / nome, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 1. MÉDIAS MÓVEIS
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(dados.index, preco, color="black", linewidth=1.2, label="Preço de fechamento")
ax.plot(dados.index, dados["mme_curta"], color="blue",
        label=f"MME{MM_CURTA}: média móvel exponencial de {MM_CURTA} períodos")
ax.plot(dados.index, dados["mme_longa"], color="orange",
        label=f"MME{MM_LONGA}: média móvel exponencial de {MM_LONGA} períodos")
ax.set_title("Médias móveis no SPY — timeframe diário, últimos 6 meses")
ax.set_ylabel("Preço (US$)")
ax.legend(loc="lower right")
formatar_datas(ax)
salvar(fig, "indicador1_medias_moveis.png")

# ---------------------------------------------------------------------------
# 2. IFR (preço em cima, IFR embaixo)
# ---------------------------------------------------------------------------
fig, (cima, baixo) = plt.subplots(2, 1, figsize=(11, 6), sharex=True,
                                  gridspec_kw={"height_ratios": [2, 1]})
cima.plot(dados.index, preco, color="black", linewidth=1.2)
cima.set_title("Preço do SPY — timeframe diário, últimos 6 meses")
cima.set_ylabel("Preço (US$)")
formatar_datas(cima)

baixo.plot(dados.index, dados["ifr"], color="purple", label=f"IFR de {IFR_PERIODO} períodos")
baixo.axhline(70, color="red", linestyle="--", label="70: sobrecomprado")
baixo.axhline(30, color="green", linestyle="--", label="30: sobrevendido")
baixo.set_ylim(0, 100)
baixo.set_title(f"IFR (Índice de Força Relativa) de {IFR_PERIODO} períodos")
baixo.set_ylabel("IFR (0 a 100)")
baixo.legend(loc="lower left", fontsize=8)
formatar_datas(baixo)
salvar(fig, "indicador2_ifr.png")

# ---------------------------------------------------------------------------
# 3. BANDAS DE BOLLINGER
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.fill_between(dados.index, dados["bb_baixo"], dados["bb_cima"], color="blue", alpha=0.1)
ax.plot(dados.index, dados["bb_cima"], color="blue", linewidth=1,
        label=f"Banda superior (média + {BB_DESVIOS} desvios-padrão)")
ax.plot(dados.index, dados["bb_meio"], color="blue", linestyle="--", linewidth=1,
        label=f"Média móvel simples de {BB_PERIODO} períodos")
ax.plot(dados.index, dados["bb_baixo"], color="blue", linewidth=1,
        label=f"Banda inferior (média − {BB_DESVIOS} desvios-padrão)")
ax.plot(dados.index, preco, color="black", linewidth=1.2, label="Preço de fechamento")
ax.set_title(f"Bandas de Bollinger ({BB_PERIODO} períodos, {BB_DESVIOS} desvios-padrão) "
             "no SPY — timeframe diário")
ax.set_ylabel("Preço (US$)")
ax.legend(loc="lower right", fontsize=8)
formatar_datas(ax)
salvar(fig, "indicador3_bollinger.png")

# ---------------------------------------------------------------------------
# 4. MACD (preço em cima, MACD embaixo)
# ---------------------------------------------------------------------------
fig, (cima, baixo) = plt.subplots(2, 1, figsize=(11, 6), sharex=True,
                                  gridspec_kw={"height_ratios": [2, 1]})
cima.plot(dados.index, preco, color="black", linewidth=1.2)
cima.set_title("Preço do SPY — timeframe diário, últimos 6 meses")
cima.set_ylabel("Preço (US$)")
formatar_datas(cima)

cores = ["green" if h >= 0 else "red" for h in dados["macd_hist"]]
baixo.bar(dados.index, dados["macd_hist"], color=cores, width=1, label="Histograma (MACD − sinal)")
baixo.plot(dados.index, dados["macd"], color="blue",
           label=f"Linha MACD (MME{MACD_RAPIDA} − MME{MACD_LENTA})")
baixo.plot(dados.index, dados["macd_sinal"], color="orange",
           label=f"Linha de sinal (MME{MACD_SINAL} do MACD)")
baixo.axhline(0, color="gray", linewidth=0.8)
baixo.set_title(f"MACD ({MACD_RAPIDA}, {MACD_LENTA}, {MACD_SINAL})")
baixo.set_ylabel("MACD (US$)")
baixo.legend(loc="lower left", fontsize=8)
formatar_datas(baixo)
salvar(fig, "indicador4_macd.png")

# ---------------------------------------------------------------------------
# 5. VOLUME FINANCEIRO (preço em cima, volume embaixo)
# ---------------------------------------------------------------------------
fig, (cima, baixo) = plt.subplots(2, 1, figsize=(11, 6), sharex=True,
                                  gridspec_kw={"height_ratios": [2, 1]})
cima.plot(dados.index, preco, color="black", linewidth=1.2)
cima.set_title("Preço do SPY — timeframe diário, últimos 6 meses")
cima.set_ylabel("Preço (US$)")
formatar_datas(cima)

subiu = dados["Close"] >= dados["Open"]
baixo.bar(dados.index, dados["vol_financeiro"], width=1,
          color=["green" if s else "red" for s in subiu])
baixo.set_title("Volume financeiro diário (preço × quantidade negociada)")
baixo.set_ylabel("Bilhões de US$")
formatar_datas(baixo)
salvar(fig, "indicador5_volume_financeiro.png")

# ---------------------------------------------------------------------------
# 6. VWAP — precisa do timeframe de 1 HORA, porque recomeça a cada dia
# ---------------------------------------------------------------------------
hora = yf.download("SPY", period="1mo", interval="1h", auto_adjust=True)
hora.columns = hora.columns.get_level_values(0)
hora.index = hora.index.tz_convert("America/New_York")
hora["dia"] = hora.index.date
hora = hora[hora["dia"] < pd.Timestamp.now(tz="America/New_York").date()]  # só pregões completos
hora = hora[hora["dia"] >= sorted(set(hora["dia"]))[-5]]   # últimos 5 pregões

# VWAP = soma de (preço típico x volume) / soma do volume, desde o início do dia
tipico = (hora["High"] + hora["Low"] + hora["Close"]) / 3
hora["vwap"] = ((tipico * hora["Volume"]).groupby(hora["dia"]).cumsum()
                / hora["Volume"].groupby(hora["dia"]).cumsum())

fig, ax = plt.subplots(figsize=(11, 4.5))
x = range(len(hora))                      # uma posição por candle (sem buracos à noite)
for i, (_, c) in enumerate(hora.iterrows()):
    cor = "green" if c["Close"] >= c["Open"] else "red"
    ax.vlines(i, c["Low"], c["High"], color=cor, linewidth=1)
    ax.bar(i, max(abs(c["Close"] - c["Open"]), 0.05), bottom=min(c["Open"], c["Close"]),
           width=0.7, color=cor)
for dia, parte in hora.groupby("dia"):    # uma linha de VWAP por dia (ela recomeça)
    posicoes = [hora.index.get_loc(t) for t in parte.index]
    ax.plot(posicoes, parte["vwap"], color="blue", linewidth=2,
            label="VWAP (recomeça a cada dia)" if dia == hora["dia"].iloc[0] else None)
inicios = [hora.index.get_loc(p.index[0]) for _, p in hora.groupby("dia")]
for p in inicios[1:]:
    ax.axvline(p - 0.5, color="gray", linestyle=":", linewidth=1)
ax.set_xticks(inicios, [hora.index[p].strftime("%d/%m") for p in inicios])
ax.set_title("VWAP no SPY — timeframe de 1 hora (1 candle = 1 hora), últimos 5 pregões")
ax.set_ylabel("Preço (US$)")
ax.legend(loc="upper left")
ax.grid(alpha=0.3)
salvar(fig, "indicador6_vwap.png")

print("Pronto! 6 gráficos salvos em", PASTA)
