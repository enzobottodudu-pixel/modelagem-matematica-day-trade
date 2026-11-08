"""Conferência dos dados, do modelo e da simulação com US$1.000 (candles de 1 h, os 9 ativos).

1. Candles de 1 h: buracos, repetidos, preços impossíveis, máxima/mínima erradas, candles por dia.
2. Segunda fonte, hora por hora: o fechamento de cada hora comparado com outra fonte independente.
   B3 → Profit Pro (1 min); Tesla → Bybit (1 min); SPY e NQ → HistData (1 min, índice: compara a variação);
   EUR/USD e BTC/USD → Yahoo Finance (1 h, só o mês de teste).
3. Maiores variações de 1 hora: confere se a segunda fonte mostra o mesmo salto.
4. Modelo refeito de outro jeito (equações normais) e simulação refeita de outro jeito (sem laço).

Rodar: py -3.14 conferir.py   →   salva CONFERENCIA.md.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
TCC = PASTA.parent
sys.path.insert(0, str(TCC / "backtest"))
from custos import custo_percentual
from dados import ATIVOS, FUSO, ULTIMO_DIA_DO_TREINO, carregar, treino_e_teste

D90 = TCC / "Dados 90 dias"
YAHOO = TCC / "Dados do Yahoo Finance"
B3 = ("PETR4", "ITUB4", "MGLU3", "IBOV")
INICIAL = 1000.0


def abrir(caminho, fuso):
    c = pd.read_csv(caminho)
    c["Data"] = pd.to_datetime(c["Data"], utc=True).dt.tz_convert(fuso)
    return c.set_index("Data").sort_index()


def horas_do_minuto(minuto, fuso, inicio, fim, meia_hora):
    """Junta candles de 1 min em horas, do mesmo jeito que o Yahoo (nos EUA a hora começa em :30)."""
    m = minuto[(minuto.index.strftime("%H:%M") >= inicio) & (minuto.index.strftime("%H:%M") < fim)]
    return m["Close"].resample("1h", offset="30min" if meia_hora else "0min").last().dropna()


def segunda_fonte(ativo):
    """Devolve (fechamento de cada hora na segunda fonte, nome da fonte, se compara nível ou só variação)."""
    fuso = FUSO[ativo]
    if ativo in B3:
        return horas_do_minuto(abrir(D90 / ativo / f"{ativo}_1min.csv", fuso), fuso, "10:00", "17:00", False), \
            "Profit Pro (1 min)", "nível"
    if ativo == "TESLA":
        return horas_do_minuto(abrir(D90 / "TESLA" / "TESLA_1min_bybit.csv", fuso), fuso, "09:30", "16:00", True), \
            "Bybit TSLAUSDT (1 min)", "nível"
    if ativo == "SPY":
        return horas_do_minuto(abrir(D90 / "SPY" / "SPY_1min_histdata.csv", fuso), fuso, "09:30", "16:00", True), \
            "HistData índice S&P 500 (1 min)", "variação"
    if ativo == "NQ":
        m = abrir(D90 / "NQ" / "NQ_1min_histdata.csv", fuso)
        return m["Close"].resample("1h").last().dropna(), "HistData índice Nasdaq-100 (1 min)", "variação"
    return abrir(YAHOO / ativo / f"{ativo}_1h.csv", fuso)["Close"], "Yahoo Finance (1 h, só o teste)", "nível"


def pc(v, casas=3):
    return f"{v:.{casas}f}".replace(".", ",") + "%"


linhas = ["# Conferência dos dados, do modelo e da simulação (candles de 1 h)", "",
          "Gerado por `previsao/conferir.py`. Treino: 12/07 a 09/09/2026. Teste: 10/09 a 09/10/2026.", ""]

# ---------------------------------------------------------------- 1. os candles de 1 h
linhas += ["## 1. Os candles de 1 h usados no modelo", "",
           ("| Ativo | Candles (treino / teste) | Primeiro e último | Repetidos | Vazios | Preço ≤ 0 "
            "| Máx/mín incoerentes | Candles por dia | Dias incompletos |"),
           "|---|---|---|---|---|---|---|---|---|"]
for ativo in ATIVOS:
    c = carregar(ativo, "1h")
    treino, teste = treino_e_teste(c)
    ohlc = c[["Open", "High", "Low", "Close"]]
    incoerente = ((c["High"] < ohlc.max(axis=1) - 1e-9) | (c["Low"] > ohlc.min(axis=1) + 1e-9)).sum()
    por_dia = c.groupby("dia").size()
    normal = por_dia.mode().iloc[0]
    incompletos = por_dia[por_dia < normal]
    texto_incompletos = ", ".join(f"{pd.Timestamp(d):%d/%m} ({n})" for d, n in incompletos.items()) or "nenhum"
    linhas.append(f"| {ativo} | {len(treino)} / {len(teste)} | {c.index[0]:%d/%m %H:%M} a {c.index[-1]:%d/%m %H:%M} "
                  f"| {c.index.duplicated().sum()} | {int(ohlc.isna().sum().sum())} | {int((ohlc <= 0).sum().sum())} "
                  f"| {incoerente} | {normal} | {texto_incompletos} |")

# ---------------------------------------------------------------- 2 e 3. segunda fonte
linhas += ["", "## 2. Fechamento de cada hora comparado com uma segunda fonte", "",
           ("| Ativo | Segunda fonte | Horas comparadas | Diferença média | Maior diferença | Variações com o mesmo "
            "sinal | Correlação das variações |"),
           "|---|---|---|---|---|---|---|"]
saltos = []
for ativo in ATIVOS:
    c = carregar(ativo, "1h")
    outra, fonte, modo = segunda_fonte(ativo)
    junto = pd.concat({"usado": c["Close"], "outra": outra, "dia": c["dia"]}, axis=1, join="inner").dropna()
    var = junto.groupby("dia")[["usado", "outra"]].pct_change().dropna()  # variação dentro do mesmo dia
    mesmo_sinal = (np.sign(var["usado"]) == np.sign(var["outra"]))[(var != 0).all(axis=1)].mean() * 100
    correl = var["usado"].corr(var["outra"])
    if modo == "nível":
        dif = (junto["usado"] / junto["outra"] - 1).abs() * 100
        media, maior = pc(dif.mean()), f"{pc(dif.max())} ({dif.idxmax():%d/%m %H:%M})"
    else:
        dif = (var["usado"] - var["outra"]).abs() * 100
        media = pc(dif.mean()).replace("%", " p.p.")
        maior = f"{pc(dif.max()).replace('%', ' p.p.')} ({dif.idxmax():%d/%m %H:%M})"
    linhas.append(f"| {ativo} | {fonte} | {len(junto)} de {len(c)} | {media} | {maior} "
                  f"| {pc(mesmo_sinal, 1)} | {f'{correl:.4f}'.replace('.', ',')} |")

    # as 3 maiores variações de 1 hora no arquivo usado (todas as horas, inclusive a abertura do dia)
    v = c["Close"].pct_change().dropna()
    outra_var = outra.pct_change()
    for quando in v.abs().nlargest(3).index:
        anterior = c.index[c.index.get_loc(quando) - 1]
        confere = "não tem essa hora"
        if quando in outra.index and anterior in outra.index:
            confere = pc((outra[quando] / outra[anterior] - 1) * 100, 2)
        elif quando in outra_var.index and not np.isnan(outra_var[quando]):
            confere = pc(outra_var[quando] * 100, 2)
        abertura = "abertura do dia" if c.loc[quando, "dia"] != c.loc[anterior, "dia"] else "dentro do dia"
        saltos.append(f"| {ativo} | {quando:%d/%m/%Y %H:%M} | {abertura} | {pc(v[quando] * 100, 2)} | {confere} |")

linhas += ["", "## 3. As 3 maiores variações de 1 hora de cada ativo, na segunda fonte", "",
           "| Ativo | Hora | Tipo | Arquivo usado | Segunda fonte |", "|---|---|---|---|---|", *saltos]

# ---------------------------------------------------------------- 4. modelo e simulação refeitos
prev = pd.read_csv(PASTA / "previsoes_teste.csv")
capital_md = (PASTA / "CAPITAL.md").read_text(encoding="utf-8")
linhas += ["", "## 4. Modelo e simulação refeitos de outro jeito", "",
           ("| Ativo | Último dia do treino | Primeiro dia do teste | Maior diferença nos pesos | Maior diferença nas "
            "previsões | Operações | Custo por operação | Final com custos (refeito) | Está no CAPITAL.md? "
            "| Comprar e segurar (refeito) |"),
           "|---|---|---|---|---|---|---|---|---|---|"]
for ativo in ATIVOS:
    c = carregar(ativo, "1h")
    c["variacao"] = c["Close"].pct_change()
    for k in range(3):
        c[f"v{k}"] = c["variacao"].shift(k)
    c["alvo"] = c["variacao"].shift(-1)
    treino, teste = treino_e_teste(c)
    t = treino.dropna(subset=["v0", "v1", "v2", "alvo"])
    s = teste.dropna(subset=["v0", "v1", "v2", "alvo"])
    x = np.column_stack([np.ones(len(t)), t[["v0", "v1", "v2"]]])
    pesos = np.linalg.solve(x.T @ x, x.T @ t["alvo"].to_numpy())  # equações normais (outro jeito de achar a, b)
    pesos_lstsq = np.linalg.lstsq(x, t["alvo"], rcond=None)[0]
    minha = np.column_stack([np.ones(len(s)), s[["v0", "v1", "v2"]]]) @ pesos
    p = prev[prev["ativo"] == ativo]
    dif_prev = np.abs(minha - p["prevista"].to_numpy()).max() * 100

    # simulação sem laço: lado de cada hora, operações = quando o lado muda para comprado ou vendido
    s = s.assign(dia_seguinte=c["dia"].shift(-1).loc[s.index])
    lado = np.where(s["dia_seguinte"].to_numpy() == s["dia"].to_numpy(), np.sign(minha), 0)
    antes = np.concatenate([[0], lado[:-1]])
    abre = (lado != 0) & (lado != antes)
    custos = np.array([custo_percentual(ativo, preco, "1h") / 100 for preco in s["Close"][abre]])
    final = INICIAL * np.prod(1 + lado * s["alvo"].to_numpy()) * np.prod(1 - custos)
    segurar = INICIAL * s["Close"].iloc[-1] * (1 + s["alvo"].iloc[-1]) / s["Close"].iloc[0]
    texto_final = f"{final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    no_md = "sim" if f"US${texto_final}" in capital_md else "NÃO"
    linhas.append(f"| {ativo} | {max(treino['dia']):%d/%m} | {min(teste['dia']):%d/%m} "
                  f"| {f'{np.abs(pesos - pesos_lstsq).max():.1e}'} | {f'{dif_prev:.1e}'} p.p. | {abre.sum()} "
                  f"| {pc(custos.mean() * 100)} | US${texto_final} | {no_md} "
                  f"| US${f'{segurar:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')} |")
    assert max(treino["dia"]) <= ULTIMO_DIA_DO_TREINO < min(teste["dia"])  # treino e teste não se misturam

(PASTA / "CONFERENCIA.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
print("\n".join(linhas))
