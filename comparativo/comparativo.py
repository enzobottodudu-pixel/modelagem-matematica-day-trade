"""Comparativo de tudo o que foi testado no mês de teste (10/09 a 09/10/2026), com US$1.000 em cada ativo.

Junta as 4 estratégias da seção 2.9 (estrategias_2_9/operacoes.csv), a regressão linear (previsao/operacoes_modelo.csv)
e buy and hold (previsao/capital_modelo.csv), e calcula para todos as mesmas medidas do capítulo 2
(backtest/metricas.py): taxa de acerto, payoff, esperança, margem de erro e drawdown.

Rodar: py -3.14 comparativo.py   →   salva COMPARATIVO.md e as imagens em imagens/.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
TCC = PASTA.parent
sys.path.insert(0, str(TCC / "backtest"))
from dados import ATIVOS
from metricas import boletim

INICIAL = 1000.0
ABORDAGENS = ["ORB", "VWAP", "IFR", "Médias", "Regressão"]
TIMEFRAME = {"ORB": "30 min", "VWAP": "15 min", "IFR": "30 min", "Médias": "5 min", "Regressão": "1 h"}
TIPO = {"ORB": "segue a tendência", "Médias": "segue a tendência", "VWAP": "aposta na volta",
        "IFR": "aposta na volta", "Regressão": "previsão estatística"}
NOMES = {"EURUSD": "EUR/USD", "SPY": "SPY", "NQ": "NQ", "IBOV": "IBOV", "PETR4": "PETR4", "ITUB4": "ITUB4",
         "BTCUSD": "BTC/USD", "TESLA": "Tesla", "MGLU3": "MGLU3"}
CORES = {"ORB": "#2166ac", "VWAP": "#1b9e77", "IFR": "#e7298a", "Médias": "#7570b3", "Regressão": "#e66101",
         "Buy and hold": "#9e9e9e"}
PRETO, CINZA, VERDE, VERMELHO = "#222222", "#9e9e9e", "#1a9850", "#d73027"
plt.rcParams["text.parse_math"] = False
(PASTA / "imagens").mkdir(exist_ok=True)


def porcento(v, casas=1):
    return f"{v:+.{casas}f}".replace(".", ",") + "%"


def virgula(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


# ------------------------------------------------------------------ as operações de todas as abordagens
est = pd.read_csv(TCC / "estrategias_2_9" / "operacoes.csv")
reg = pd.read_csv(TCC / "previsao" / "operacoes_modelo.csv").assign(estrategia="Regressão")
ops = pd.concat([est[["estrategia", "ativo", "resultado", "sem_custo", "custo"]], reg], ignore_index=True)
segurar = pd.read_csv(TCC / "previsao" / "capital_modelo.csv").groupby("ativo")["segurar"].last()

# ------------------------------------------------------------------ as medidas de cada abordagem em cada ativo
por_ativo = {}
for (abordagem, ativo), o in ops.groupby(["estrategia", "ativo"]):
    b = boletim(o.to_dict("records"), INICIAL)
    sem = boletim([{"resultado": r} for r in o["sem_custo"]], INICIAL)
    por_ativo[(abordagem, ativo)] = {**b, "final": b["capital"][-1], "final_sem": sem["capital"][-1],
                                     "pct": (b["capital"][-1] / INICIAL - 1) * 100,
                                     "pct_sem": (sem["capital"][-1] / INICIAL - 1) * 100}

geral = []
for a in ABORDAGENS:
    o = ops[ops["estrategia"] == a]
    b = boletim(o.to_dict("records"), INICIAL)  # acerto, payoff e esperança de todas as operações juntas
    celulas = [por_ativo[(a, x)] for x in ATIVOS if (a, x) in por_ativo]
    ativos = [x for x in ATIVOS if (a, x) in por_ativo]
    pior_dd = min(ativos, key=lambda x: por_ativo[(a, x)]["drawdown_maximo"])
    validos = [c for c in celulas if c["operacoes"] > 1]  # com 1 operação não dá para calcular a margem de erro
    geral.append({
        "abordagem": a, "operacoes": len(o), "ativos": len(ativos), "acerto": b["taxa_de_acerto"],
        "payoff": b["payoff"], "esperanca": b["esperanca"], "bruto": o["sem_custo"].mean(), "custo": o["custo"].mean(),
        "total": (sum(c["final"] for c in celulas) / (INICIAL * len(celulas)) - 1) * 100,
        "total_sem": (sum(c["final_sem"] for c in celulas) / (INICIAL * len(celulas)) - 1) * 100,
        "com_lucro": sum(c["final"] > INICIAL for c in celulas),
        "vantagem": sum(c["tem_vantagem"] for c in validos),
        "desvantagem": sum(c["faixa_da_esperanca"][1] < 0 for c in validos),
        "pior_dd": por_ativo[(a, pior_dd)]["drawdown_maximo"], "pior_dd_ativo": pior_dd,
        "melhor": max(ativos, key=lambda x: por_ativo[(a, x)]["pct"]),
        "pior": min(ativos, key=lambda x: por_ativo[(a, x)]["pct"]),
    })
geral = pd.DataFrame(geral).set_index("abordagem")
total_segurar = (segurar.sum() / (INICIAL * len(segurar)) - 1) * 100

# ------------------------------------------------------------------ gráfico 1: o total de cada abordagem
fig, ax = plt.subplots(figsize=(12, 6.6))
x = np.arange(len(ABORDAGENS) + 1)
com = [*geral["total"], total_segurar]
sem = [*geral["total_sem"], total_segurar]
ax.bar(x - 0.2, com, 0.38, color=[VERDE if v >= 0 else VERMELHO for v in com], label="com custos")
ax.bar(x[:-1] + 0.2, sem[:-1], 0.38, color="#fdb863", label="sem custos")
for xi, v in zip(x - 0.2, com, strict=True):
    ax.text(xi, v + (0.6 if v >= 0 else -0.6), porcento(v), ha="center", va="bottom" if v >= 0 else "top",
            fontsize=11, fontweight="bold")
for xi, v in zip(x[:-1] + 0.2, sem[:-1], strict=True):
    ax.text(xi, v + 0.6, porcento(v), ha="center", va="bottom", fontsize=10, color="#555555")
ax.axhline(0, color=PRETO, linewidth=1)
rotulos = [f"{a}\n({TIMEFRAME[a]})\n{int(geral.loc[a, 'operacoes']):,} operações".replace(",", ".") for a in ABORDAGENS]
ax.set_xticks(x, [*rotulos, "Buy and\nhold\n9 operações"], fontsize=10.5)
ax.set_ylim(min(com) - 4, total_segurar + 5)
ax.yaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%" if v else "0%")
ax.set_ylabel("ganho ou perda sobre o capital inicial (%)")
ax.legend(loc="upper left", fontsize=10.5, frameon=False)
ax.grid(axis="y", alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
ax.set_title("Resultado total de cada abordagem no teste (10/09 a 09/10/2026), com US$1.000 em cada ativo\n"
             "soma dos 9 ativos (a VWAP tem 8: o EUR/USD não tem volume), com e sem custos",
             fontsize=12, fontweight="bold", loc="left")
fig.tight_layout()
fig.savefig(PASTA / "imagens" / "comparativo_total.png", dpi=170)
plt.close(fig)

# ------------------------------------------------------------------ gráfico 2: ganho antes do custo × custo
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(ABORDAGENS))
ax.bar(x - 0.2, geral["bruto"], 0.38, color="#fdb863", label="ganho médio por operação, antes do custo")
ax.bar(x + 0.2, geral["custo"], 0.38, color=CINZA, label="custo médio por operação")
for xi, a in zip(x, ABORDAGENS, strict=True):
    ax.text(xi - 0.2, geral.loc[a, "bruto"] + 0.004, porcento(geral.loc[a, "bruto"], 3), ha="center",
            va="bottom", fontsize=10)
    ax.text(xi + 0.2, geral.loc[a, "custo"] + 0.004, virgula(geral.loc[a, "custo"], 3) + "%", ha="center",
            va="bottom", fontsize=10)
    liquido = geral.loc[a, "esperanca"]
    ax.text(xi, -0.03, f"sobra: {porcento(liquido, 3)}", ha="center", va="top", fontsize=10.5, fontweight="bold",
            color=VERDE if liquido >= 0 else VERMELHO)
ax.axhline(0, color=PRETO, linewidth=1)
ax.set_xticks(x, [f"{a}\n({TIMEFRAME[a]})" for a in ABORDAGENS], fontsize=11)
ax.set_ylim(-0.05, geral[["bruto", "custo"]].max().max() * 1.3)
ax.yaxis.set_major_formatter(lambda v, _: virgula(v, 2) + "%")
ax.legend(loc="upper left", fontsize=10.5, frameon=False)
ax.grid(axis="y", alpha=0.3)
for lado in ("top", "right", "bottom"):
    ax.spines[lado].set_visible(False)
ax.tick_params(axis="x", length=0, pad=6)
ax.set_title("Em todas as abordagens, o custo de cada operação foi maior que o ganho antes do custo\n"
             "média de todas as operações do teste (10/09 a 09/10/2026), em % do valor de cada operação",
             fontsize=12, fontweight="bold", loc="left")
fig.tight_layout()
fig.savefig(PASTA / "imagens" / "comparativo_custo.png", dpi=170)
plt.close(fig)

# ------------------------------------------------------------------ gráfico 3: operações × resultado
fig, ax = plt.subplots(figsize=(12, 7))
for a in ABORDAGENS:
    pontos = [(por_ativo[(a, x)]["operacoes"], por_ativo[(a, x)]["pct"], x) for x in ATIVOS if (a, x) in por_ativo]
    ax.scatter([p[0] for p in pontos], [p[1] for p in pontos], s=70, color=CORES[a], edgecolor="white",
               linewidth=0.8, label=f"{a} ({TIMEFRAME[a]})", zorder=3)
destaques = [("Médias", "BTCUSD"), ("VWAP", "MGLU3"), ("Regressão", "MGLU3"), ("Regressão", "BTCUSD"),
             ("Médias", "NQ")]
NO_NA = {"EURUSD": "no", "SPY": "no", "NQ": "no", "IBOV": "no", "BTCUSD": "no", "PETR4": "na", "ITUB4": "no",
         "TESLA": "na", "MGLU3": "na"}
for a, x in destaques:
    r = por_ativo[(a, x)]
    ax.annotate(f"{a} {NO_NA[x]} {NOMES[x]}: {porcento(r['pct'])}", (r["operacoes"], r["pct"]), xytext=(10, -4),
                textcoords="offset points", fontsize=9.5, color=CORES[a], fontweight="bold")
ax.axhline(0, color=PRETO, linewidth=1)
ax.set_xscale("log")
ax.set_xticks([1, 3, 10, 30, 100, 300], ["1", "3", "10", "30", "100", "300"])
ax.set_xlim(0.8, 900)
ax.yaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%" if v else "0%")
ax.set_xlabel("número de operações no mês (escala que multiplica por 10 a cada passo)")
ax.set_ylabel("ganho ou perda com custos (%)")
ax.legend(loc="lower left", fontsize=10, frameon=False)
ax.grid(alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
ax.set_title("Em média, quanto mais operações, maior a perda: cada ponto é uma abordagem em um ativo\n"
             "teste de 10/09 a 09/10/2026, US$1.000 em cada ativo, com custos", fontsize=12, fontweight="bold",
             loc="left")
fig.tight_layout()
fig.savefig(PASTA / "imagens" / "comparativo_operacoes.png", dpi=170)
plt.close(fig)

# ------------------------------------------------------------------ gráfico 4: o melhor de cada ativo
fig, ax = plt.subplots(figsize=(12.5, 7.4))
corte = 30
for li, x in enumerate(ATIVOS):
    y = len(ATIVOS) - 1 - li
    valores = {a: por_ativo[(a, x)]["pct"] for a in ABORDAGENS if (a, x) in por_ativo}
    valores["Buy and hold"] = (segurar[x] / INICIAL - 1) * 100
    ax.hlines(y, min(min(valores.values()), -corte - 5), min(max(valores.values()), corte), color="#e6e6e6",
              linewidth=1, zorder=1)
    for a, v in valores.items():
        ax.scatter(max(min(v, corte), -corte - 5), y, s=110 if a != "Buy and hold" else 140, color=CORES[a],
                   marker="D" if a == "Buy and hold" else "o", edgecolor="white", linewidth=0.8, zorder=3)
    melhor = max((a for a in valores if a != "Buy and hold"), key=valores.get)
    texto = f"melhor: {melhor} ({porcento(valores[melhor])})"
    fora = [f"{a} {porcento(v)}" for a, v in valores.items() if v > corte or v < -corte - 5]
    ax.text(corte + 3, y, texto + (f"  |  fora do gráfico: {', '.join(fora)}" if fora else ""), va="center",
            fontsize=9.5)
for a in [*ABORDAGENS, "Buy and hold"]:
    ax.scatter([], [], s=90, color=CORES[a], marker="D" if a == "Buy and hold" else "o", label=a)
ax.axvline(0, color=PRETO, linewidth=1)
ax.set_yticks(range(len(ATIVOS)), [NOMES[x] for x in ATIVOS][::-1], fontsize=11)
ax.set_xlim(-corte - 7, corte + 48)
ax.set_xticks(range(-30, 31, 10), [f"{v:+d}%" if v else "0%" for v in range(-30, 31, 10)])
ax.set_xlabel("ganho ou perda com custos (%)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=6, fontsize=10, frameon=False)
ax.grid(axis="x", alpha=0.3)
for lado in ("top", "right", "left"):
    ax.spines[lado].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.set_title("As 6 abordagens em cada ativo, com custos (teste: 10/09 a 09/10/2026)\n"
             "ativos do menos volátil (EUR/USD) ao mais volátil (MGLU3); valores além de ±30% ficam na borda",
             fontsize=12, fontweight="bold", loc="left")
fig.tight_layout()
fig.savefig(PASTA / "imagens" / "comparativo_ativos.png", dpi=170)
plt.close(fig)

# ------------------------------------------------------------------ as tabelas
md = ["# Comparativo: as 4 estratégias da seção 2.9, a regressão linear e buy and hold", "",
      ("Teste de 10/09 a 09/10/2026, US$1.000 em cada ativo, com custos (salvo indicado). Gerado por "
       "`comparativo/comparativo.py`."), "",
      "## 1. Quadro geral", "",
      "| Medida | " + " | ".join(ABORDAGENS) + " | Buy and hold |",
      "|---|" + "---|" * (len(ABORDAGENS) + 1)]


def linha(nome, f, segurar_txt="—"):
    md.append(f"| {nome} | " + " | ".join(f(a) for a in ABORDAGENS) + f" | {segurar_txt} |")


g = geral
linha("Tipo", lambda a: TIPO[a], "nenhuma operação no meio")
linha("Timeframe", lambda a: TIMEFRAME[a])
linha("Ativos testados", lambda a: str(int(g.loc[a, "ativos"])), "9")
linha("Operações no mês", lambda a: f"{int(g.loc[a, 'operacoes']):,}".replace(",", "."), "9")
linha("Taxa de acerto", lambda a: virgula(g.loc[a, "acerto"], 1) + "%")
linha("Payoff", lambda a: virgula(g.loc[a, "payoff"]))
linha("Ganho médio por operação, antes do custo", lambda a: porcento(g.loc[a, "bruto"], 3))
linha("Custo médio por operação", lambda a: virgula(g.loc[a, "custo"], 3) + "%")
linha("Esperança por operação, com custos", lambda a: porcento(g.loc[a, "esperanca"], 3))
linha("**Total com custos**", lambda a: f"**{porcento(g.loc[a, 'total'])}**", f"**{porcento(total_segurar)}**")
linha("Total sem custos", lambda a: porcento(g.loc[a, "total_sem"]), porcento(total_segurar))
linha("Ativos com lucro", lambda a: f"{int(g.loc[a, 'com_lucro'])} de {int(g.loc[a, 'ativos'])}",
      f"{int((segurar > INICIAL).sum())} de 9")
linha("Ativos com vantagem (faixa acima de zero)", lambda a: str(int(g.loc[a, "vantagem"])))
linha("Ativos com desvantagem (faixa abaixo de zero)", lambda a: str(int(g.loc[a, "desvantagem"])))
linha("Melhor ativo", lambda a: f"{NOMES[g.loc[a, 'melhor']]} ({porcento(por_ativo[(a, g.loc[a, 'melhor'])]['pct'])})")
linha("Pior ativo", lambda a: f"{NOMES[g.loc[a, 'pior']]} ({porcento(por_ativo[(a, g.loc[a, 'pior'])]['pct'])})")
linha("Pior drawdown", lambda a: f"{virgula(g.loc[a, 'pior_dd'], 1)}% ({NOMES[g.loc[a, 'pior_dd_ativo']]})")

md += ["", "## 2. Cada ativo (ganho ou perda com custos)", "",
       ("| Ativo | " + " | ".join(ABORDAGENS)
        + " | Buy and hold | Melhor abordagem | Ganhou de buy and hold? |"),
       "|---|" + "---|" * (len(ABORDAGENS) + 3)]
for x in ATIVOS:
    valores = {a: por_ativo[(a, x)]["pct"] for a in ABORDAGENS if (a, x) in por_ativo}
    s = (segurar[x] / INICIAL - 1) * 100
    melhor = max(valores, key=valores.get)
    venceram = [a for a, v in valores.items() if v > s]
    md.append(f"| {NOMES[x]} | " + " | ".join(porcento(valores[a]) if a in valores else "sem volume"
                                             for a in ABORDAGENS)
              + f" | {porcento(s)} | {melhor} | {', '.join(venceram) if venceram else 'nenhuma'} |")

grupos = {"Seguem a tendência (ORB e Médias)": ["ORB", "Médias"], "Apostam na volta (VWAP e IFR)": ["VWAP", "IFR"],
          "Previsão estatística (regressão)": ["Regressão"]}
md += ["", "## 3. Por tipo de abordagem", "", "| Tipo | Operações | Total com custos | Total sem custos | MGLU3 |",
       "|---|---|---|---|---|"]
for nome, membros in grupos.items():
    celulas = [por_ativo[(a, x)] for a in membros for x in ATIVOS if (a, x) in por_ativo]
    t_com = (sum(c["final"] for c in celulas) / (INICIAL * len(celulas)) - 1) * 100
    t_sem = (sum(c["final_sem"] for c in celulas) / (INICIAL * len(celulas)) - 1) * 100
    mglu = ", ".join(f"{a} {porcento(por_ativo[(a, 'MGLU3')]['pct'])}" for a in membros)
    n_ops = f"{sum(c['operacoes'] for c in celulas):,}".replace(",", ".")
    md.append(f"| {nome} | {n_ops} | {porcento(t_com)} | {porcento(t_sem)} | {mglu} |")
(PASTA / "COMPARATIVO.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("\n".join(md))
