"""Quanto da alta dos ativos da B3 no teste veio de dentro do pregão e quanto veio dos gaps de abertura.

Usa os candles de 1 h do Yahoo (os mesmos da simulação; 30min = Profit), no mês de teste (10/09 a 09/10/2026).
Gap de abertura = abertura do dia ÷ fechamento do dia anterior. Dentro do pregão = fechamento ÷ abertura do mesmo dia.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backtest"))
from dados import carregar, treino_e_teste

for ativo in ["IBOV", "PETR4", "ITUB4", "MGLU3"]:
    treino, teste = treino_e_teste(carregar(ativo, sys.argv[1] if len(sys.argv) > 1 else "1h"))
    dias = teste.groupby(teste.index.date).agg(abre=("Open", "first"), fecha=("Close", "last"))
    fech_ant = treino["Close"].iloc[-1]
    anteriores = [fech_ant, *dias["fecha"].iloc[:-1]]
    gap = (dias["abre"].to_numpy() / anteriores).prod() - 1
    dentro = (dias["fecha"] / dias["abre"]).prod() - 1
    total = dias["fecha"].iloc[-1] / fech_ant - 1
    dias_alta = (dias["fecha"].to_numpy() > anteriores).sum()
    g = dias["abre"].to_numpy() / anteriores - 1
    maior = g.argmax()
    print(f"{ativo}: total {total:+.1%} | gaps {gap:+.1%} | dentro do pregão {dentro:+.1%} | "
          f"dias de alta {dias_alta} de {len(dias)} | maior gap {g[maior]:+.1%} em {dias.index[maior]}")
