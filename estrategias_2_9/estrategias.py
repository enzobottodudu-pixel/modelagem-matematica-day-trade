"""As 4 estratégias da seção 2.9 no mês de teste (10/09 a 09/10/2026), com a mesma simulação de US$1.000 do modelo.

Regras: as dos exemplos da seção 2.9 (Figuras 33 a 36), sem mudar nada; estão explicadas em REGRAS.md.
- ORB, 30 min: faixa = 1º candle do dia; compra no rompimento da máxima, vende no da mínima; stop no outro lado da
  faixa; alvo a 3 faixas da entrada; 1 operação por dia.
- VWAP, 15 min: vende quando o candle fecha 0,6% acima da VWAP, compra quando fecha 0,6% abaixo; alvo = voltar à
  VWAP; stop 0,6% contra.
- IFR, 30 min: IFR de 14 períodos; compra com IFR ≤ 30, vende com IFR ≥ 70; alvo = IFR voltar a 50; stop 1% contra.
- Médias, 5 min: MME 9 × MME 21; compra quando a rápida cruza a lenta para cima, vende quando cruza para baixo, vira
  a mão no cruzamento contrário; stop 1,5% contra.
Iguais para as 4 (as mesmas do motor.py e da simulação do modelo): day trade (fecha tudo no último candle do dia e
não abre nada nele); se o stop e o alvo caem no mesmo candle, conta o stop; capital inteiro em cada operação;
custo de cada operação do backtest/custos.py; US$1.000 em cada ativo; comparação com o modelo de previsão e com
buy and hold (previsao/capital_modelo.csv).

Rodar: py -3.14 estrategias.py   →   salva as imagens em imagens/, ESTRATEGIAS.md e operacoes.csv.
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
TCC = PASTA.parent
sys.path.insert(0, str(TCC / "backtest"))
from custos import custo_percentual
from dados import ATIVOS, FUSO, carregar, treino_e_teste
from metricas import boletim

INICIAL = 1000.0
TIMEFRAME = {"ORB": "30min", "VWAP": "15min", "IFR": "30min", "Médias": "5min"}
NOMES = {"EURUSD": "EUR/USD", "SPY": "SPY", "NQ": "NQ", "IBOV": "IBOV", "PETR4": "PETR4", "ITUB4": "ITUB4",
         "BTCUSD": "BTC/USD", "TESLA": "Tesla", "MGLU3": "MGLU3"}
CORES = {"ORB": "#2166ac", "VWAP": "#1b9e77", "IFR": "#e7298a", "Médias": "#7570b3", "Modelo": "#e66101",
         "Buy and hold": "#9e9e9e"}
PRETO, CINZA, VERDE, VERMELHO = "#222222", "#9e9e9e", "#1a9850", "#d73027"
plt.rcParams["text.parse_math"] = False  # sem isso, dois "US$" no mesmo texto viram fórmula
(PASTA / "imagens").mkdir(exist_ok=True)


def porcento(v):
    return f"{v:+.1f}".replace(".", ",") + "%"  # -3.21 -> "-3,2%"


def dolares(v):
    return "US$" + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # 1234.5 -> "US$1.234,50"


def virgula(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


# ------------------------------------------------------------------ os dados e os indicadores
def volume_do_yahoo(ativo):
    """SPY e NQ: o HistData não tem volume; usa o volume do Yahoo (15 min), que existe só no mês de teste."""
    y = pd.read_csv(TCC / "Dados do Yahoo Finance" / ativo / f"{ativo}_15min.csv")
    y["Data"] = pd.to_datetime(y["Data"], utc=True).dt.tz_convert(FUSO[ativo])
    return y.set_index("Data")["Volume"]


def candles_do_teste(ativo, estrategia):
    """Abre os candles, calcula o indicador da estratégia com todo o histórico e devolve só o mês de teste."""
    c = carregar(ativo, TIMEFRAME[estrategia]).copy()
    if estrategia == "VWAP":
        if ativo == "EURUSD":
            return None  # câmbio não tem volume centralizado: não dá para calcular a VWAP
        if ativo in ("SPY", "NQ"):
            c["Volume"] = volume_do_yahoo(ativo).reindex(c.index).fillna(0)
        tipico = (c["High"] + c["Low"] + c["Close"]) / 3  # preço típico, como na Figura 34
        soma_pv = (tipico * c["Volume"]).groupby(c["dia"]).cumsum()
        soma_v = c["Volume"].groupby(c["dia"]).cumsum()
        c["vwap"] = (soma_pv / soma_v).where(soma_v > 0)  # recomeça todo dia
    if estrategia == "IFR":
        variacao = c["Close"].diff()
        altas = variacao.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
        quedas = (-variacao.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        c["ifr"] = 100 - 100 / (1 + altas / quedas)
    if estrategia == "Médias":
        c["acima"] = c["Close"].ewm(span=9, adjust=False).mean() > c["Close"].ewm(span=21, adjust=False).mean()
    _, teste = treino_e_teste(c)
    return teste


# ------------------------------------------------------------------ peças iguais para as 4 estratégias
def bateu(lado, k, stop, alvo):
    """Stop e alvo dentro do candle, pela máxima e pela mínima. Os dois no mesmo candle: conta o stop.
    Se o candle já abre depois do nível (gap), sai na abertura."""
    if lado == "compra":
        if stop is not None and k.Low <= stop:
            return min(k.Open, stop), "stop"
        if alvo is not None and k.High >= alvo:
            return max(k.Open, alvo), "alvo"
    else:
        if stop is not None and k.High >= stop:
            return max(k.Open, stop), "stop"
        if alvo is not None and k.Low <= alvo:
            return min(k.Open, alvo), "alvo"
    return None


def abrir(lado, preco, k, i, stop, alvo=None):
    return {"lado": lado, "entrada": preco, "hora_entrada": k.Index, "i": i, "stop": stop, "alvo": alvo}


def fechar(op, preco, motivo, k, ativo, timeframe):
    """Fecha a operação: resultado = retorno − custo, em % (a fórmula do motor.py, pedaço 1)."""
    custo = custo_percentual(ativo, op["entrada"], timeframe)
    if op["lado"] == "compra":
        retorno = (preco - op["entrada"]) / op["entrada"] * 100
    else:
        retorno = (op["entrada"] - preco) / op["entrada"] * 100
    return {"lado": op["lado"], "hora_entrada": op["hora_entrada"], "entrada": op["entrada"], "hora_saida": k.Index,
            "saida": preco, "motivo": motivo, "custo": custo, "sem_custo": retorno, "resultado": retorno - custo}


# ------------------------------------------------------------------ as 4 estratégias, um dia de cada vez
def orb(dia, ativo, tf):
    ops, aberta, operou = [], None, False
    maxima, minima = dia[0].High, dia[0].Low  # a faixa de abertura: o 1º candle do dia
    faixa = maxima - minima
    if faixa <= 0:
        return ops
    for i, k in enumerate(dia[1:], start=1):
        if aberta is None and not operou and i < len(dia) - 1:
            sobe, desce = k.High > maxima, k.Low < minima
            if sobe or desce:
                if sobe and desce:  # rompeu os dois lados no mesmo candle: vale o lado mais perto da abertura
                    sobe = abs(k.Open - maxima) <= abs(k.Open - minima)
                lado = "compra" if sobe else "venda"
                preco = max(k.Open, maxima) if sobe else min(k.Open, minima)
                alvo = preco + 3 * faixa if sobe else preco - 3 * faixa
                aberta, operou = abrir(lado, preco, k, i, minima if sobe else maxima, alvo), True
                saida = bateu(lado, k, aberta["stop"], None)  # no candle da entrada, só o stop (o caso pior)
                if saida:
                    ops.append(fechar(aberta, *saida, k, ativo, tf))
                    aberta = None
                continue
        if aberta is not None:
            saida = bateu(aberta["lado"], k, aberta["stop"], aberta["alvo"])
            if saida:
                ops.append(fechar(aberta, *saida, k, ativo, tf))
                aberta = None
    if aberta is not None:
        ops.append(fechar(aberta, dia[-1].Close, "fim do dia", dia[-1], ativo, tf))
    return ops


def vwap(dia, ativo, tf):
    ops, aberta = [], None
    for i, k in enumerate(dia):
        saiu = False
        if aberta is not None and i > aberta["i"]:
            alvo = dia[i - 1].vwap  # a VWAP que já era conhecida quando o candle começou
            saida = bateu(aberta["lado"], k, aberta["stop"], alvo)
            if saida:
                ops.append(fechar(aberta, *saida, k, ativo, tf))
                aberta, saiu = None, True
        if aberta is None and not saiu and i < len(dia) - 1 and not np.isnan(k.vwap):
            distancia = k.Close / k.vwap - 1
            if distancia >= 0.006:
                aberta = abrir("venda", k.Close, k, i, k.Close * 1.006)
            elif distancia <= -0.006:
                aberta = abrir("compra", k.Close, k, i, k.Close * 0.994)
    if aberta is not None:
        ops.append(fechar(aberta, dia[-1].Close, "fim do dia", dia[-1], ativo, tf))
    return ops


def ifr(dia, ativo, tf):
    ops, aberta = [], None
    for i, k in enumerate(dia):
        saiu = False
        if aberta is not None and i > aberta["i"]:
            saida = bateu(aberta["lado"], k, aberta["stop"], None)
            if saida is None and ((aberta["lado"] == "compra" and k.ifr >= 50) or
                                  (aberta["lado"] == "venda" and k.ifr <= 50)):
                saida = (k.Close, "alvo (IFR voltou a 50)")
            if saida:
                ops.append(fechar(aberta, *saida, k, ativo, tf))
                aberta, saiu = None, True
        if aberta is None and not saiu and i < len(dia) - 1:
            if k.ifr <= 30:
                aberta = abrir("compra", k.Close, k, i, k.Close * 0.99)
            elif k.ifr >= 70:
                aberta = abrir("venda", k.Close, k, i, k.Close * 1.01)
    if aberta is not None:
        ops.append(fechar(aberta, dia[-1].Close, "fim do dia", dia[-1], ativo, tf))
    return ops


def medias(dia, ativo, tf):
    ops, aberta = [], None
    for i, k in enumerate(dia):
        if aberta is not None and i > aberta["i"]:
            saida = bateu(aberta["lado"], k, aberta["stop"], None)
            if saida:
                ops.append(fechar(aberta, *saida, k, ativo, tf))
                aberta = None
        if i > 0 and k.acima != dia[i - 1].acima and i < len(dia) - 1:  # as médias cruzaram neste candle
            lado = "compra" if k.acima else "venda"
            if aberta is not None and aberta["lado"] != lado:  # cruzamento contrário: vira a mão
                ops.append(fechar(aberta, k.Close, "cruzamento contrário", k, ativo, tf))
                aberta = None
            if aberta is None:
                aberta = abrir(lado, k.Close, k, i, k.Close * (0.985 if lado == "compra" else 1.015))
    if aberta is not None:
        ops.append(fechar(aberta, dia[-1].Close, "fim do dia", dia[-1], ativo, tf))
    return ops


REGRA = {"ORB": orb, "VWAP": vwap, "IFR": ifr, "Médias": medias}

# ------------------------------------------------------------------ roda tudo
modelo = pd.read_csv(TCC / "previsao" / "capital_modelo.csv")
modelo["Data"] = pd.to_datetime(modelo["Data"], utc=True)
resultado, todas_ops = {}, []
for estrategia, tf in TIMEFRAME.items():
    for ativo in ATIVOS:
        teste = candles_do_teste(ativo, estrategia)
        if teste is None:
            continue
        ops = []
        for _, d in teste.groupby("dia"):
            ops += REGRA[estrategia](list(d.itertuples()), ativo, tf)
        b = boletim(ops, INICIAL)
        sem = boletim([{"resultado": op["sem_custo"]} for op in ops], INICIAL)
        resultado[(estrategia, ativo)] = {**b, "final": b["capital"][-1] if ops else INICIAL,
                                          "final_sem": sem["capital"][-1] if ops else INICIAL,
                                          "horas": [op["hora_saida"] for op in ops]}
        todas_ops += [{"estrategia": estrategia, "ativo": ativo, **op} for op in ops]
pd.DataFrame(todas_ops).to_csv(PASTA / "operacoes.csv", index=False)

m = modelo.groupby("ativo").last()
for ativo in ATIVOS:
    resultado[("Modelo", ativo)] = {"final": m.loc[ativo, "modelo"], "final_sem": m.loc[ativo, "sem_custo"]}
    resultado[("Buy and hold", ativo)] = {"final": m.loc[ativo, "segurar"], "final_sem": m.loc[ativo, "segurar"]}
COLUNAS = [*TIMEFRAME, "Modelo", "Buy and hold"]


def total(coluna, chave="final"):
    """Total da coluna em %: soma dos finais ÷ capital investido (a VWAP não tem o EUR/USD)."""
    finais = [resultado[(coluna, a)][chave] for a in ATIVOS if (coluna, a) in resultado]
    return (sum(finais) / (INICIAL * len(finais)) - 1) * 100, len(finais)


# ------------------------------------------------------------------ gráfico 1: a tabela colorida de comparação
pct = pd.DataFrame({col: [(resultado[(col, a)]["final"] / INICIAL - 1) * 100 if (col, a) in resultado else np.nan
                          for a in ATIVOS] for col in COLUNAS}, index=[NOMES[a] for a in ATIVOS])
pct.loc["Total, com custos"] = [total(col)[0] for col in COLUNAS]
pct.loc["Total, sem custos"] = [total(col, "final_sem")[0] for col in COLUNAS]

fig, ax = plt.subplots(figsize=(13, 8.2))
limite = 30
for li, linha in enumerate(pct.index):
    for ci, col in enumerate(COLUNAS):
        v = pct.loc[linha, col]
        if np.isnan(v):
            cor, texto = "#eeeeee", "sem volume"
        else:
            forca = min(abs(v), limite) / limite
            base = np.array([26, 152, 80]) if v >= 0 else np.array([215, 48, 39])
            cor = tuple((255 - (255 - base) * (0.15 + 0.85 * forca)) / 255)
            texto = porcento(v)
        y = li + (0.4 if li >= len(ATIVOS) else 0)  # separa um pouco os totais
        ax.add_patch(plt.Rectangle((ci, y), 0.96, 0.92, color=cor))
        escuro = not np.isnan(v) and abs(v) > limite * 0.55
        ax.text(ci + 0.48, y + 0.46, texto, ha="center", va="center", fontsize=11 if not np.isnan(v) else 9,
                fontweight="bold" if li >= len(ATIVOS) else "normal", color="white" if escuro else PRETO)
ax.set_xlim(0, len(COLUNAS))
ax.set_ylim(len(pct) + 0.4, 0)
nomes_col = [f"{c}\n({TIMEFRAME[c].replace('min', ' min')})" if c in TIMEFRAME else
             ("Modelo\n(1 h)" if c == "Modelo" else "Buy and\nhold") for c in COLUNAS]
ax.set_xticks(np.arange(len(COLUNAS)) + 0.48, nomes_col, fontsize=11)
ax.xaxis.tick_top()
ax.set_yticks([i + 0.46 + (0.4 if i >= len(ATIVOS) else 0) for i in range(len(pct))], pct.index, fontsize=11)
for i in range(len(ATIVOS), len(pct)):
    ax.get_yticklabels()[i].set_fontweight("bold")
ax.tick_params(length=0)
for lado in ("top", "right", "left", "bottom"):
    ax.spines[lado].set_visible(False)
ax.set_title("Ganho ou perda de US$1.000 em cada ativo no teste (10/09 a 09/10/2026)\n"
             "as 4 estratégias da seção 2.9 (regras dos exemplos), o modelo de previsão e buy and hold, "
             "com custos\n"
             "verde = ganhou, vermelho = perdeu (quanto mais forte a cor, maior)",
             fontsize=12, fontweight="bold", loc="left", pad=44)
fig.tight_layout()
fig.savefig(PASTA / "imagens" / "comparacao_percentual.png", dpi=170)
plt.close(fig)


# ------------------------------------------------------------------ gráfico 2: uma figura por estratégia
def grafico_estrategia(estrategia):
    """Igual ao capital_percentual do modelo: com custos, sem custos e buy and hold, por ativo."""
    ativos = [a for a in ATIVOS if (estrategia, a) in resultado]
    linhas = [(NOMES[a], resultado[(estrategia, a)]["final"], resultado[(estrategia, a)]["final_sem"],
               resultado[("Buy and hold", a)]["final"]) for a in ativos]
    tot = [total(estrategia)[0], total(estrategia, "final_sem")[0],
           (sum(r[3] for r in linhas) / (INICIAL * len(linhas)) - 1) * 100]
    valores = np.array([[(v / INICIAL - 1) * 100 for v in r[1:]] for r in linhas])
    ordem = list(np.argsort(-valores[:, 0]))
    nomes = [linhas[i][0] for i in ordem] + [f"Total (US${len(linhas)}.000)"]
    valores = np.vstack([valores[ordem], tot])
    corte = 45
    fig, ax = plt.subplots(figsize=(12.5, 8.6))
    y = np.arange(len(nomes))[::-1].astype(float)
    y[-1] -= 0.5
    altura = 0.26
    series = [("com custos", 0, None), ("sem custos", 1, "#fdb863"), ("buy and hold", 2, CINZA)]
    for desloc, (rotulo, col, cor) in zip((altura, 0, -altura), series, strict=True):
        v = valores[:, col]
        cores = [VERDE if x >= 0 else VERMELHO for x in v] if cor is None else cor
        ax.barh(y + desloc, np.clip(v, -corte, corte), altura * 0.92, color=cores,
                label=f"{estrategia}, {rotulo}" if col < 2 else rotulo)
        for yi, x in zip(y + desloc, v, strict=True):
            xb = min(max(x, -corte), corte)
            ax.text(xb + (0.8 if x >= 0 else -0.8), yi, porcento(x) + (" (barra cortada)" if abs(x) > corte else ""),
                    va="center", ha="left" if x >= 0 else "right", fontsize=9.5 if col == 0 else 8.5,
                    fontweight="bold" if col == 0 else "normal", color=PRETO if col == 0 else "#555555")
    ax.axvline(0, color=PRETO, linewidth=1)
    ax.axhline(y[-1] + 0.75, color=CINZA, linewidth=0.8, linestyle=":")
    ax.set_yticks(y, nomes, fontsize=11)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.set_xlim(min(-35, np.nanmin(valores) - 10), corte + 22)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%" if v else "0%")
    ax.set_xlabel("ganho ou perda sobre o capital inicial de US$1.000 (%)")
    ax.legend(loc="lower right", fontsize=10, frameon=False)
    ax.grid(axis="x", alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_title(f"{estrategia}: ganho ou perda de US$1.000 em cada ativo no teste (10/09 a 09/10/2026)\n"
                 f"candles de {TIMEFRAME[estrategia].replace('min', ' min')} (timeframe de "
                 f"{TIMEFRAME[estrategia].replace('min', ' minutos')}), regras da seção 2.9, com e sem custos, "
                 "× buy and hold", fontsize=12, fontweight="bold", loc="left")
    fig.tight_layout()
    fig.savefig(PASTA / "imagens" / f"percentual_{estrategia.replace('é', 'e')}.png", dpi=170)
    plt.close(fig)


for estrategia in TIMEFRAME:
    grafico_estrategia(estrategia)

# ------------------------------------------------------------------ gráfico 3: o capital de cada ativo no teste
for ativo in ATIVOS:
    fig, ax = plt.subplots(figsize=(13, 6.4))
    ax.axhline(INICIAL, color=PRETO, linewidth=0.8, linestyle=":")
    mm = modelo[modelo["ativo"] == ativo]
    ax.plot(mm["Data"], mm["segurar"], color=CORES["Buy and hold"], linewidth=1.6, label="buy and hold")
    ax.plot(mm["Data"], mm["modelo"], color=CORES["Modelo"], linewidth=1.6, linestyle="--", label="modelo (1 h)")
    inicio = mm["Data"].iloc[0]
    for estrategia, tf in TIMEFRAME.items():
        r = resultado.get((estrategia, ativo))
        if r is None:
            continue
        horas = [inicio] + [pd.Timestamp(h).tz_convert("UTC") for h in r["horas"]]
        ax.step(horas, r["capital"], where="post", color=CORES[estrategia], linewidth=2, label=f"{estrategia} ({tf})")
    baixo, alto = ax.get_ylim()
    ax.set_ylim(baixo, alto + (alto - baixo) * 0.16)
    ax.legend(loc="upper left", fontsize=9.5, frameon=False, ncol=6)
    ax.set_ylabel("capital (US$)")
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}".replace(",", "."))
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%d/%m", tz=FUSO[ativo]))
    ax.grid(axis="y", alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    finais = "  |  ".join(f"{c}: {porcento((resultado[(c, ativo)]['final'] / INICIAL - 1) * 100)}"
                          for c in COLUNAS if (c, ativo) in resultado)
    ax.set_title(f"{NOMES[ativo]}: US$1.000 em cada estratégia no teste (10/09 a 09/10/2026), com custos\n{finais}",
                 fontsize=11.5, fontweight="bold", loc="left")
    fig.tight_layout()
    fig.savefig(PASTA / "imagens" / f"capital_{ativo}.png", dpi=170)
    plt.close(fig)

# ------------------------------------------------------------------ as tabelas
linhas = ["# As 4 estratégias da seção 2.9 no teste (10/09 a 09/10/2026), com US$1.000 em cada ativo", "",
          "Gerado por `estrategias_2_9/estrategias.py`. Regras em `REGRAS.md`. Resultados com custos, salvo indicado.",
          "", "## Comparação (ganho ou perda sobre US$1.000, com custos)", "",
          "| Ativo | " + " | ".join(COLUNAS) + " |", "|---|" + "---|" * len(COLUNAS)]
for nome, linha in pct.iterrows():
    linhas.append(f"| {nome} | " + " | ".join("sem volume" if np.isnan(v) else porcento(v) for v in linha) + " |")
for estrategia, tf in TIMEFRAME.items():
    linhas += ["", f"## {estrategia} (candles de {tf})", "",
               ("| Ativo | Operações | Acerto | Payoff | Esperança por operação | Faixa da esperança | Tem vantagem? "
                "| Drawdown máximo | Final com custos | Final sem custos |"),
               "|---|---|---|---|---|---|---|---|---|---|"]
    for ativo in ATIVOS:
        r = resultado.get((estrategia, ativo))
        if r is None:
            linhas.append(f"| {NOMES[ativo]} | sem volume: não dá para calcular a VWAP | | | | | | | | |")
            continue
        if r["operacoes"] == 0:
            linhas.append(f"| {NOMES[ativo]} | 0 | | | | | | | {dolares(INICIAL)} | {dolares(INICIAL)} |")
            continue
        f1, f2 = r["faixa_da_esperanca"]
        payoff = "—" if r["payoff"] == float("inf") else virgula(r["payoff"])
        faixa = f"{virgula(f1, 3)}% a {virgula(f2, 3)}%" if r["operacoes"] > 1 else "—"
        vantagem = ("sim" if r["tem_vantagem"] else "não") if r["operacoes"] > 1 else "não dá para saber (1 operação)"
        linhas.append(f"| {NOMES[ativo]} | {r['operacoes']} | {virgula(r['taxa_de_acerto'], 1)}% | {payoff} "
                      f"| {virgula(r['esperanca'], 3)}% | {faixa} | {vantagem} | {virgula(r['drawdown_maximo'], 1)}% "
                      f"| {dolares(r['final'])} ({porcento((r['final'] / INICIAL - 1) * 100)}) "
                      f"| {dolares(r['final_sem'])} |")
    t_com, n = total(estrategia)
    t_sem, _ = total(estrategia, "final_sem")
    linhas += ["", (f"Total ({n} ativos, US${n}.000 no começo): com custos {porcento(t_com)}, "
                    f"sem custos {porcento(t_sem)}.")]
(PASTA / "ESTRATEGIAS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
print("\n".join(linhas))
