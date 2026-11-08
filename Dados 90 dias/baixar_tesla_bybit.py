"""Baixa 90 dias de candles de 1 minuto da Tesla na Bybit (contrato TSLAUSDT) e monta os 13 timeframes.

O TSLAUSDT é um contrato perpétuo da Bybit que acompanha o preço da ação da Tesla e é
negociado 24 horas por dia. Os arquivos levam o final "_bybit".
Grátis e sem conta (API pública de candles).

Uso: py -3.14 "Dados 90 dias/baixar_tesla_bybit.py"
"""

import time

import pandas as pd
import requests

from baixar_90dias import FIM, INICIO, NAVEGADOR, PASTA, TODOS, juntar


def baixar_1min():
    linhas = []
    inicio = int(INICIO.timestamp() * 1000)
    fim = int(FIM.timestamp() * 1000)
    while inicio < fim:
        ate = min(inicio + 1000 * 60_000, fim) - 1
        r = requests.get(
            "https://api.bybit.com/v5/market/kline",
            params={"category": "linear", "symbol": "TSLAUSDT", "interval": "1", "start": inicio, "end": ate, "limit": 1000},
            headers=NAVEGADOR,
            timeout=30,
        )
        r.raise_for_status()
        linhas += r.json()["result"]["list"]
        inicio = ate + 1
        time.sleep(0.2)
    df = pd.DataFrame([x[:6] for x in linhas], columns=["Data", "Open", "High", "Low", "Close", "Volume"])
    df["Data"] = pd.to_datetime(df["Data"].astype("int64"), unit="ms", utc=True)
    df = df.set_index("Data").astype(float).sort_index()
    return df[~df.index.duplicated()]


def main():
    base = baixar_1min()
    pasta = PASTA / "TESLA"
    for tf in TODOS:
        df = base if tf == "1min" else juntar(base, "1D" if tf == "24h" else tf, True)
        df.index.name = "Data"
        df.to_csv(pasta / f"TESLA_{tf}_bybit.csv")
        print(f"TESLA {tf:6} {len(df):7} candles  {df.index.min()} -> {df.index.max()}  (Bybit TSLAUSDT)")


if __name__ == "__main__":
    main()
