"""Simulação com dinheiro: US$1.000 em cada ativo, operando o modelo de previsão no teste (10/09 a 09/10/2026).

Usa as previsões salvas por previsao.py (previsoes_teste.csv), candles de 1 h.
Regras da simulação (day trade):
- no fim de cada hora, se o modelo prevê alta, fica COMPRADO na hora seguinte; se prevê queda, fica VENDIDO;
- enquanto a previsão não muda de lado, continua na mesma operação; quando muda, fecha e vira a mão;
- tudo fecha no fechamento do último candle do dia (não dorme posicionado), e o último candle não abre nada;
- usa o capital inteiro em cada operação, sem alavancagem;
- desconta o custo de cada operação (ida e volta), com os valores do backtest/custos.py (CUSTOS.md).
Os ativos em reais e o NQ são simulados em %, como se os US$1.000 fossem aplicados neles.
Para comparar: "buy and hold" = comprar com os US$1.000 no começo do teste e vender só no fim.

Rodar: py -3.14 simulacao.py   →   salva imagens/capital_<ATIVO>.png, imagens/capital_todos.png, CAPITAL.md
e capital_modelo.csv (as curvas, usadas por estrategias_2_9/estrategias.py).
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parent / "backtest"))
from custos import custo_percentual
from dados import ATIVOS

INICIAL = 1000.0  # capital inicial, em dólares
NOMES = {"EURUSD": "EUR/USD", "SPY": "SPY", "NQ": "NQ", "IBOV": "IBOV", "PETR4": "PETR4", "ITUB4": "ITUB4",
         "BTCUSD": "BTC/USD", "TESLA": "Tesla", "MGLU3": "MGLU3"}
PRETO, LARANJA, CINZA, VERDE, VERMELHO = "#222222", "#e66101", "#9e9e9e", "#1a9850", "#d73027"
plt.rcParams["text.parse_math"] = False  # sem isso, dois "US$" no mesmo texto viram fórmula


def dolares(v):
    return "US$" + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # 1234.5 -> "US$1.234,50"


def porcento(v):
    return f"{v:+.1f}".replace(".", ",") + "%"  # -3.21 -> "-3,2%"


def simular(p, ativo):
    """Anda hora por hora no teste e devolve as curvas de capital e o resultado de cada operação."""
    capital, sem_custo, segurar = INICIAL, INICIAL, INICIAL
    posicao, acumulado, custo = 0, 1.0, 0.0
    curva, curva_sem, curva_segurar, operacoes, brutos, custos = [], [], [], [], [], []
    for linha in p.itertuples():
        # o lado da próxima hora: +1 comprado, -1 vendido, 0 fora (na última hora do dia não abre nada)
        novo = 0 if linha.dia_seguinte != linha.dia else int(np.sign(linha.prevista))
        if posicao != 0 and novo != posicao:  # fecha a operação aberta e paga o custo
            capital *= 1 - custo
            operacoes.append(acumulado * (1 - custo) - 1)
            brutos.append(acumulado - 1)
            custos.append(custo)
        if novo != 0 and novo != posicao:  # abre uma operação nova
            acumulado, custo = 1.0, custo_percentual(ativo, linha.Close, "1h") / 100
        posicao = novo
        if posicao != 0:  # a hora seguinte acontece: ganha se acertou o lado, perde se errou
            acumulado *= 1 + posicao * linha.alvo
            capital *= 1 + posicao * linha.alvo
            sem_custo *= 1 + posicao * linha.alvo
        segurar *= 1 + linha.alvo
        curva.append(capital)
        curva_sem.append(sem_custo)
        curva_segurar.append(segurar)
    if posicao != 0:  # a última operação do teste fecha no último candle e também paga o custo
        capital *= 1 - custo
        operacoes.append(acumulado * (1 - custo) - 1)
        brutos.append(acumulado - 1)
        custos.append(custo)
        curva[-1] = capital
    ops = pd.DataFrame({"resultado": operacoes, "sem_custo": brutos, "custo": custos}) * 100  # em %
    return np.array(curva), np.array(curva_sem), np.array(curva_segurar), ops


todas = pd.read_csv(PASTA / "previsoes_teste.csv")
resultados, curvas, todas_ops = [], [], []
for ativo in ATIVOS:
    p = todas[todas["ativo"] == ativo].reset_index(drop=True)
    curva, curva_sem, curva_segurar, ops = simular(p, ativo)
    curvas.append(pd.DataFrame({"ativo": ativo, "Data": p["Data"], "modelo": curva, "sem_custo": curva_sem,
                                "segurar": curva_segurar}))
    final, final_sem, final_segurar = curva[-1], curva_sem[-1], curva_segurar[-1]
    acerto = (ops["resultado"] > 0).mean() * 100
    todas_ops.append(ops.assign(ativo=ativo))
    resultados.append((ativo, final, final_sem, final_segurar, len(ops), acerto))

    # gráfico do capital ao longo do teste
    n = len(p)
    fig, ax = plt.subplots(figsize=(13, 6.2))
    ax.axhline(INICIAL, color=PRETO, linewidth=0.8, linestyle=":")
    ax.plot(range(n), curva_segurar, color=CINZA, linewidth=1.6, label="só comprar no início e vender no fim")
    ax.plot(range(n), curva_sem, color=LARANJA, linewidth=1.1, linestyle="--", alpha=0.7,
            label="modelo, sem custos")
    ax.plot(range(n), curva, color=LARANJA, linewidth=2.2, label="modelo, com custos")
    baixo, alto = ax.get_ylim()
    ax.set_ylim(baixo, alto + (alto - baixo) * 0.14)  # espaço vazio em cima para a legenda
    ax.legend(loc="upper left", fontsize=10, frameon=False, ncol=3)
    ax.set_ylabel("capital (US$)")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}".replace(",", "."))
    ax.grid(axis="y", alpha=0.3)
    primeiros = pd.Series(range(n), index=p["dia"].to_numpy()).groupby(level=0).first()
    marcas, ultima = [], -n
    for dia, posicao in primeiros.items():
        if posicao - ultima >= n / 11:
            marcas.append((posicao, f"{pd.Timestamp(dia):%d/%m}"))
            ultima = posicao
    ax.set_xticks([m[0] for m in marcas], [m[1] for m in marcas], fontsize=9)
    ax.set_xlim(-1, n + 1)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_title(f"{NOMES[ativo]}: US$1.000 operando o modelo de previsão no teste (10/09 a 09/10/2026)\n"
                 "candles de 1 h (timeframe de 1 hora), compra se o modelo prevê alta e vende se prevê queda, "
                 "fecha tudo no fim do dia\n"
                 f"final com custos: {dolares(final)} ({porcento((final / INICIAL - 1) * 100)})  |  "
                 f"{len(ops)} operações, {f'{acerto:.0f}'}% ganharam  |  "
                 f"buy and hold: {dolares(final_segurar)}",
                 fontsize=11.5, fontweight="bold", loc="left")
    fig.tight_layout()
    fig.savefig(PASTA / "imagens" / f"capital_{ativo}.png", dpi=170)
    plt.close(fig)

# as curvas do capital, para comparar com as estratégias da seção 2.9 (estrategias_2_9/estrategias.py)
pd.concat(curvas).to_csv(PASTA / "capital_modelo.csv", index=False)
pd.concat(todas_ops).to_csv(PASTA / "operacoes_modelo.csv", index=False)  # cada operação, em %

# gráfico com os 9 ativos: quanto sobrou dos US$1.000
fig, ax = plt.subplots(figsize=(12, 7))
y = np.arange(len(resultados))[::-1]
modelo = np.array([r[1] for r in resultados])
segurar = np.array([r[3] for r in resultados])
ax.barh(y + 0.2, modelo, 0.38, color=[VERDE if v >= INICIAL else VERMELHO for v in modelo],
        label="modelo, com custos")
ax.barh(y - 0.2, segurar, 0.38, color=CINZA, label="buy and hold")
for yi, v in zip(y, modelo, strict=True):
    ax.text(v + 15, yi + 0.2, dolares(v), va="center", fontsize=9.5, fontweight="bold")
for yi, v in zip(y, segurar, strict=True):
    ax.text(v + 15, yi - 0.2, dolares(v), va="center", fontsize=9, color="#555555")
ax.axvline(INICIAL, color=PRETO, linewidth=1, linestyle=":")
ax.set_yticks(y, [NOMES[r[0]] for r in resultados], fontsize=11)
ax.set_xlim(0, max(segurar.max(), modelo.max()) * 1.2)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:,.0f}".replace(",", "."))
ax.set_xlabel("capital no fim do teste (US$), começando com US$1.000")
ax.legend(loc="upper right", fontsize=10, frameon=False)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
ax.set_title("Quanto sobrou de US$1.000 em cada ativo no teste (10/09 a 09/10/2026)\n"
             "modelo de previsão em candles de 1 h (timeframe de 1 hora), com custos, × buy and hold",
             fontsize=12, fontweight="bold", loc="left")
fig.tight_layout()
fig.savefig(PASTA / "imagens" / "capital_todos.png", dpi=170)
plt.close(fig)

# gráfico comparativo do ganho ou perda em %, do maior ganho do modelo para a maior perda, com o total no fim
CORTE = 45  # a barra que passa disso é cortada no gráfico, com o valor escrito (só a MGLU3 comprada e segurada)
nomes = [NOMES[r[0]] for r in resultados] + ["Total (US$9.000)"]
finais = np.array([[r[1], r[2], r[3]] for r in resultados])
finais = np.vstack([finais, finais.sum(axis=0) / len(resultados)])  # total = média dos 9 (cada um começou com 1.000)
pct = (finais / INICIAL - 1) * 100  # colunas: modelo com custos, modelo sem custos, buy and hold
ordem = [*np.argsort(-pct[:-1, 0]), len(pct) - 1]  # ordena os ativos pelo modelo com custos; o total fica embaixo
series = [("modelo, com custos", 0, None), ("modelo, sem custos", 1, "#fdb863"), ("buy and hold", 2, CINZA)]

fig, ax = plt.subplots(figsize=(12.5, 9))
altura = 0.26
y = np.arange(len(ordem))[::-1].astype(float)
y[-1] -= 0.5  # separa um pouco o total dos ativos
for desloc, (rotulo, coluna, cor) in zip((altura, 0, -altura), series, strict=True):
    valores = pct[ordem, coluna]
    cores = [VERDE if v >= 0 else VERMELHO for v in valores] if cor is None else cor
    ax.barh(y + desloc, np.clip(valores, -CORTE, CORTE), altura * 0.92, color=cores, label=rotulo)
    for yi, v in zip(y + desloc, valores, strict=True):
        texto = porcento(v) + (" (barra cortada)" if abs(v) > CORTE else "")
        x = min(max(v, -CORTE), CORTE)
        ax.text(x + (0.8 if v >= 0 else -0.8), yi, texto, va="center", ha="left" if v >= 0 else "right",
                fontsize=9.5 if coluna == 0 else 8.5, fontweight="bold" if coluna == 0 else "normal",
                color=PRETO if coluna == 0 else "#555555")
ax.axvline(0, color=PRETO, linewidth=1)
ax.axhline(y[-1] + 0.75, color=CINZA, linewidth=0.8, linestyle=":")
ax.set_yticks(y, [nomes[i] for i in ordem], fontsize=11)
ax.get_yticklabels()[-1].set_fontweight("bold")
ax.set_xlim(min(-35, pct.min() - 10), CORTE + 22)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%" if v else "0%")
ax.set_xlabel("ganho ou perda sobre o capital inicial de US$1.000 (%)")
ax.legend(loc="lower right", fontsize=10, frameon=False)
ax.grid(axis="x", alpha=0.3)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
ax.set_title("Ganho ou perda de US$1.000 em cada ativo no teste (10/09 a 09/10/2026)\n"
             "modelo de previsão em candles de 1 h (timeframe de 1 hora), com e sem custos, × buy and hold",
             fontsize=12, fontweight="bold", loc="left")
fig.tight_layout()
fig.savefig(PASTA / "imagens" / "capital_percentual.png", dpi=170)
plt.close(fig)

# a tabela
linhas = [
    "# Simulação com US$1.000 em cada ativo (teste: 10/09 a 09/10/2026)",
    "",
    ("Candles de 1 h. Compra se o modelo prevê alta, vende se prevê queda, fecha tudo no fim do dia, capital inteiro "
     "em cada operação, custos do `backtest/CUSTOS.md`. Gerado por `simulacao.py`."),
    "",
    "| Ativo | Operações | Ganharam | Final com custos | Final sem custos | Buy and hold |",
    "|---|---|---|---|---|---|",
]
for ativo, final, final_sem, final_segurar, nops, acerto in resultados:
    variacao = porcento((final / INICIAL - 1) * 100)
    linhas.append(f"| {NOMES[ativo]} | {nops} | {acerto:.0f}% | {dolares(final)} ({variacao})"
                  f" | {dolares(final_sem)} | {dolares(final_segurar)} |")
total = sum(r[1] for r in resultados)
total_segurar = sum(r[3] for r in resultados)
linhas += ["", (f"Somando os 9 ativos (US$9.000 no começo): modelo com custos {dolares(total)}, "
                f"buy and hold {dolares(total_segurar)}.")]
(PASTA / "CAPITAL.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
print("\n".join(linhas))
