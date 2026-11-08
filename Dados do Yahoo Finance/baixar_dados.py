"""Baixa 1 mês de dados do Yahoo Finance de 8 ativos em 13 timeframes.

Timeframes que o Yahoo entrega direto: 1m, 2m, 5m, 15m, 30m, 1h e 1d.
Os outros são montados juntando candles menores do próprio Yahoo:
3m (de 1m) e 2h, 4h, 6h, 8h, 12h (de 1h).

Uso: py -3.14 "Dados do Yahoo Finance/baixar_dados.py"
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

PASTA = Path(__file__).parent

ATIVOS = {
    "EURUSD": "EURUSD=X",
    "SPY": "SPY",
    "IBOV": "^BVSP",
    "BTCUSD": "BTC-USD",
    "PETR4": "PETR4.SA",
    "TESLA": "TSLA",
    "ITUB4": "ITUB4.SA",
    "MGLU3": "MGLU3.SA",
    "NQ": "NQ=F",  # futuro do Nasdaq-100 (contrato vigente, trocado automaticamente pelo Yahoo)
}

# Mercados que funcionam quase o dia todo: os candles seguem o relógio (00:00, 04:00...).
# Nos outros (bolsas), os candles começam na abertura do pregão de cada dia.
CONTINUOS = {"EURUSD", "BTCUSD", "NQ"}

DIRETOS = {"1min": "1m", "2min": "2m", "5min": "5m", "15min": "15m", "30min": "30m", "1h": "1h", "24h": "1d"}
MONTADOS = {"3min": ("1min", "3min"), "2h": ("1h", "2h"), "4h": ("1h", "4h"), "6h": ("1h", "6h"),
            "8h": ("1h", "8h"), "12h": ("1h", "12h")}
ORDEM = ["1min", "2min", "3min", "5min", "15min", "30min", "1h", "2h", "4h", "6h", "8h", "12h", "24h"]

AGREGAR = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}


def baixar(codigo: str, intervalo: str, inicio: datetime, fim: datetime) -> pd.DataFrame:
    df = yf.download(codigo, start=inicio, end=fim, interval=intervalo, progress=False, auto_adjust=True)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df[["Open", "High", "Low", "Close", "Volume"]]


def baixar_1min(codigo: str, inicio: datetime, fim: datetime) -> pd.DataFrame:
    # O Yahoo só entrega 1 minuto em pedaços de até 8 dias.
    partes = []
    atual = inicio
    while atual < fim:
        prox = min(atual + timedelta(days=7), fim)
        partes.append(baixar(codigo, "1m", atual, prox))
        atual = prox
    df = pd.concat([p for p in partes if not p.empty])
    return df[~df.index.duplicated()].sort_index()


def juntar(df: pd.DataFrame, regra: str, continuo: bool) -> pd.DataFrame:
    if continuo:
        novo = df.resample(regra, origin="epoch").agg(AGREGAR)
    else:
        dias = [d.resample(regra, origin=d.index[0]).agg(AGREGAR) for _, d in df.groupby(df.index.date)]
        novo = pd.concat(dias)
    return novo.dropna(subset=["Open"])


def main() -> None:
    fim = datetime.now(timezone.utc)
    hoje = fim.replace(hour=0, minute=0, second=0, microsecond=0)
    inicio = hoje - timedelta(days=30)
    # 1 minuto: o Yahoo só guarda os últimos 30 dias, então começa um dia depois.
    inicio_1min = hoje - timedelta(days=29)
    # Sem argumentos baixa todos; com argumentos baixa só os pedidos (ex.: NQ).
    escolhidos = sys.argv[1:] or list(ATIVOS)
    resumo = []
    for nome in escolhidos:
        codigo = ATIVOS[nome]
        pasta = PASTA / nome
        pasta.mkdir(exist_ok=True)
        dados = {}
        for tf, intervalo in DIRETOS.items():
            if tf == "1min":
                dados[tf] = baixar_1min(codigo, inicio_1min, fim)
            else:
                dados[tf] = baixar(codigo, intervalo, inicio, fim)
        for tf, (base, regra) in MONTADOS.items():
            dados[tf] = juntar(dados[base], regra, nome in CONTINUOS) if not dados[base].empty else dados[base]
        for tf in ORDEM:
            df = dados[tf]
            df.index.name = "Data"
            df.to_csv(pasta / f"{nome}_{tf}.csv")
            primeiro = df.index.min() if len(df) else "-"
            ultimo = df.index.max() if len(df) else "-"
            resumo.append((nome, tf, len(df), primeiro, ultimo))
            print(f"{nome:7} {tf:6} {len(df):6} candles  {primeiro}  ->  {ultimo}")
    novo = pd.DataFrame(resumo, columns=["ativo", "timeframe", "candles", "inicio", "fim"])
    arquivo = PASTA / "resumo.csv"
    if arquivo.exists() and len(escolhidos) < len(ATIVOS):
        antigo = pd.read_csv(arquivo)
        novo = pd.concat([antigo[~antigo["ativo"].isin(escolhidos)], novo])
    novo.to_csv(arquivo, index=False)


if __name__ == "__main__":
    main()
