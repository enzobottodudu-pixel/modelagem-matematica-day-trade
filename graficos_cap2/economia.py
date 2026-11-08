"""
GRÁFICOS DO CAPÍTULO 2 — A economia e o mercado.

Dados oficiais, baixados na hora:
  - Banco Central do Brasil, Sistema Gerenciador de Séries Temporais (SGS):
      432   meta da taxa Selic (% ao ano)
      13522 IPCA acumulado em 12 meses (%)
      13762 dívida bruta do governo geral (% do PIB)
      5793  necessidade de financiamento do setor público, resultado primário, 12 meses (% do PIB)
            (positivo = déficit; no gráfico o sinal é invertido para positivo = superávit)
      7326  PIB, variação real no ano (%)
      3698  dólar comercial, venda, média mensal (R$)
  - FRED (Federal Reserve Bank of St. Louis): VIXCLS, o VIX diário.

Rode este arquivo para gerar as 4 imagens nesta pasta.
"""

import json
import time
import urllib.error
import urllib.request
from io import StringIO
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

PASTA = Path(__file__).resolve().parent
INICIO = "2015-01-01"
HOJE = pd.Timestamp.today().normalize()
VERDE, VERMELHO, AZUL, LARANJA, CINZA = "#1a9850", "#d73027", "#2c7bb6", "#f28e2b", "#4d4d4d"


def serie_bcb(codigo):
    """Baixa uma série do SGS do Banco Central e devolve uma tabela com data e valor.

    O Banco Central só entrega 10 anos de dados diários por pedido, então o pedido vai em pedaços de 5 anos.
    """
    dados = []
    for ano in range(2015, HOJE.year + 1, 5):
        url = (
            f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=json"
            f"&dataInicial=01/01/{ano}&dataFinal=31/12/{min(ano + 4, HOJE.year)}"
        )
        for tentativa in range(5):  # o site do Banco Central às vezes falha; tenta de novo
            try:
                dados += json.load(urllib.request.urlopen(url, timeout=60))
                break
            except (urllib.error.HTTPError, ValueError):  # erro do site ou resposta vazia
                time.sleep(3)
        else:
            raise RuntimeError(f"o Banco Central não respondeu a série {codigo}")
    tabela = pd.DataFrame(dados).drop_duplicates()
    tabela["data"] = pd.to_datetime(tabela["data"], dayfirst=True)
    tabela["valor"] = tabela["valor"].astype(float)
    return tabela[tabela["data"] <= HOJE].set_index("data")["valor"]


def arrumar(ax, titulo, rotulo_y):
    ax.set_title(titulo, fontsize=11, loc="left", fontweight="bold")
    ax.set_ylabel(rotulo_y, fontsize=9)
    ax.grid(alpha=0.25)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def virgula(numero, casas):
    return f"{numero:.{casas}f}".replace(".", ",")


PORCENTO = FuncFormatter(lambda v, _: virgula(v, 0) + "%")  # 80 -> "80%"
REAIS = FuncFormatter(lambda v, _: "R$" + virgula(v, 2))  # 5.5 -> "R$5,50"


def salvar(fig, nome):
    fig.tight_layout()
    fig.savefig(PASTA / nome, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("salvo:", nome)


# ---------------------------------------------------------------------------
# 1) 2.1 — Selic e inflação (IPCA em 12 meses)
selic = serie_bcb(432)
ipca = serie_bcb(13522)
fig, ax = plt.subplots(figsize=(11, 4.8))
ax.step(selic.index, selic.values, where="post", color=VERMELHO, linewidth=2, label="Meta da taxa Selic (% ao ano)")
ax.plot(ipca.index, ipca.values, color=AZUL, linewidth=2, label="Inflação: IPCA acumulado em 12 meses (%)")
ax.annotate(
    f"Selic: {selic.iloc[-1]:.2f}%".replace(".", ","),
    (selic.index[-1], selic.iloc[-1]),
    xytext=(8, 0),
    textcoords="offset points",
    va="center",
    fontsize=9,
    color=VERMELHO,
    fontweight="bold",
)
ax.annotate(
    f"IPCA: {ipca.iloc[-1]:.2f}%".replace(".", ","),
    (ipca.index[-1], ipca.iloc[-1]),
    xytext=(8, 0),
    textcoords="offset points",
    va="center",
    fontsize=9,
    color=AZUL,
    fontweight="bold",
)
arrumar(ax, f"Brasil: juros (Selic) e inflação (IPCA) — dados mensais, de 01/2015 a {ipca.index[-1]:%m/%Y}", "% ao ano")
ax.legend(loc="upper center", bbox_to_anchor=(0.45, 1.0), fontsize=9, frameon=False)
ax.yaxis.set_major_formatter(PORCENTO)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
salvar(fig, "cap2_1_selic_ipca.png")

# ---------------------------------------------------------------------------
# 2) 3.7.2 — a lei da oferta e da demanda agora fica em oferta_demanda.py


# ---------------------------------------------------------------------------
# 3) 2.3 — Painel da macroeconomia do Brasil
pib = serie_bcb(7326)
divida = serie_bcb(13762)
primario = -serie_bcb(5793)  # NFSP positiva = déficit; invertido: positivo = superávit
dolar = serie_bcb(3698)
fig, eixos = plt.subplots(2, 2, figsize=(12, 7.5))
(a, b), (c, d) = eixos

anos = [x.year for x in pib.index]
a.bar(anos, pib.values, color=[VERDE if v >= 0 else VERMELHO for v in pib.values], zorder=3)
for ano, v in zip(anos, pib.values):
    a.annotate(
        f"{v:.1f}".replace(".", ","),
        (ano, v),
        xytext=(0, 3 if v >= 0 else -10),
        textcoords="offset points",
        ha="center",
        fontsize=7,
    )
a.axhline(0, color=CINZA, linewidth=1)
a.margins(y=0.15)
arrumar(a, "PIB: crescimento real no ano (%) — dados anuais", "crescimento do PIB")
a.yaxis.set_major_formatter(PORCENTO)
a.set_xticks(anos)
a.tick_params(axis="x", labelsize=7, rotation=45)

b.plot(divida.index, divida.values, color=LARANJA, linewidth=2)
arrumar(b, "Dívida bruta do governo (% do PIB) — dados mensais", "dívida, em % do PIB")
b.yaxis.set_major_formatter(PORCENTO)

c.fill_between(
    primario.index,
    primario.values,
    0,
    where=primario.values >= 0,
    color=VERDE,
    alpha=0.5,
    label="superávit (sobrou dinheiro)",
)
c.fill_between(
    primario.index,
    primario.values,
    0,
    where=primario.values < 0,
    color=VERMELHO,
    alpha=0.5,
    label="déficit (faltou dinheiro)",
)
c.axhline(0, color=CINZA, linewidth=1)
arrumar(c, "Resultado primário em 12 meses (% do PIB) — mensal", "resultado, em % do PIB")
c.yaxis.set_major_formatter(PORCENTO)
c.legend(loc="lower left", fontsize=8, frameon=False)

d.plot(dolar.index, dolar.values, color=AZUL, linewidth=2)
arrumar(d, "Dólar comercial (R\\$ por US\\$1) — média mensal", "preço de 1 dólar")
d.yaxis.set_major_formatter(REAIS)

for ax in (b, c, d):
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", labelsize=8)
fig.suptitle("Brasil: indicadores macroeconômicos, de 2015 a 2026", fontsize=13, fontweight="bold", x=0.01, ha="left")
salvar(fig, "cap2_3_painel_macroeconomia.png")

# ---------------------------------------------------------------------------
# 4) 2.4 — O VIX (o "termômetro do medo")
texto = (
    urllib.request.urlopen(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS&cosd={INICIO}", timeout=60)
    .read()
    .decode()
)
vix = pd.read_csv(StringIO(texto), parse_dates=["observation_date"]).dropna()
vix = vix[pd.to_numeric(vix["VIXCLS"], errors="coerce").notna()]
vix["VIXCLS"] = vix["VIXCLS"].astype(float)
vix = vix.set_index("observation_date")["VIXCLS"]
fig, ax = plt.subplots(figsize=(11, 4.8))
ax.plot(vix.index, vix.values, color=CINZA, linewidth=0.9)
ax.axhline(20, color=LARANJA, linestyle="--", linewidth=1.2)
ax.annotate(
    "acima de 20: mercado nervoso",
    (pd.Timestamp("2017-03-01"), 20),
    xytext=(0, 5),
    textcoords="offset points",
    fontsize=8,
    color=LARANJA,
)
# marca os 3 maiores picos, cada um num ano diferente
picos = vix.groupby(vix.index.year).idxmax().map(lambda dia: (dia, vix[dia])).tolist()
EVENTOS = {(2015, 8): "queda da bolsa da China", (2020, 3): "pandemia de covid", (2025, 4): "tarifas dos EUA"}
for dia, valor in sorted(picos, key=lambda p: -p[1])[:3]:
    evento = EVENTOS.get((dia.year, dia.month))
    ax.annotate(
        f"{dia:%m/%Y}: {valor:.0f}" + (f" ({evento})" if evento else ""),
        (dia, valor),
        xytext=(8, -4),
        textcoords="offset points",
        fontsize=9,
        color=VERMELHO,
        fontweight="bold",
    )
    ax.scatter([dia], [valor], color=VERMELHO, s=25, zorder=5)
arrumar(
    ax,
    f"VIX, o índice do medo do mercado americano — dados diários, de 01/2015 a {vix.index[-1]:%m/%Y}",
    "VIX (pontos)",
)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
salvar(fig, "cap2_4_vix.png")
