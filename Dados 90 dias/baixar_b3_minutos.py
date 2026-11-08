"""Ativos brasileiros nos timeframes de minuto: o máximo grátis que o Yahoo entrega.

- 2, 5, 15 e 30 min: últimos 60 dias (3 min montado a partir do 1 min).
- 1 min: últimos 30 dias (baixado em pedaços de 7 dias).
Salva em <ATIVO>/<ATIVO>_<tf>.csv, ao lado dos arquivos de 1h a 24h.

Uso: py -3.14 "Dados 90 dias/baixar_b3_minutos.py"
"""

from datetime import UTC, datetime, timedelta

import pandas as pd
import yfinance as yf

from baixar_90dias import AGREGAR, PASTA

B3 = {"PETR4": "PETR4.SA", "ITUB4": "ITUB4.SA", "MGLU3": "MGLU3.SA", "IBOV": "^BVSP"}
FIM = datetime(2026, 10, 10, tzinfo=UTC)


def baixar(codigo, intervalo, inicio, fim):
    df = yf.download(codigo, start=inicio, end=fim, interval=intervalo, progress=False, auto_adjust=True)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df[["Open", "High", "Low", "Close", "Volume"]]


def tres_minutos(m1, fuso, abertura):
    # Os blocos de 3 minutos começam na abertura do pregão (10:00, 10:03...), e não no
    # primeiro minuto que aparece no dia (corrigido em 11/10/2026).
    local = m1.tz_convert(fuso)
    partes = []
    for dia, d in local.groupby(local.index.date):
        origem = pd.Timestamp(f"{dia} {abertura}", tz=fuso)
        partes.append(d.resample("3min", origin=origem).agg(AGREGAR).dropna(subset=["Open"]))
    return pd.concat(partes)


def main():
    hoje = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    inicio_60 = hoje - timedelta(days=59)
    inicio_30 = hoje - timedelta(days=29)
    for nome, codigo in B3.items():
        partes = []
        atual = inicio_30
        while atual < FIM:
            prox = min(atual + timedelta(days=7), FIM)
            partes.append(baixar(codigo, "1m", atual, prox))
            atual = prox
        m1 = pd.concat([p for p in partes if not p.empty])
        m1 = m1[~m1.index.duplicated()].sort_index()
        dados = {"1min": m1, "3min": tres_minutos(m1, "America/Sao_Paulo", "10:00")}
        for tf, itv in {"2min": "2m", "5min": "5m", "15min": "15m", "30min": "30m"}.items():
            dados[tf] = baixar(codigo, itv, inicio_60, FIM)
        for tf, df in dados.items():
            df.index.name = "Data"
            df.to_csv(PASTA / nome / f"{nome}_{tf}.csv")
            print(f"{nome:6} {tf:6} {len(df):6} candles  {df.index.min()} -> {df.index.max()}")


if __name__ == "__main__":
    main()
