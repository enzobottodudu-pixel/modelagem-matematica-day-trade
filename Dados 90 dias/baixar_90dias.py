"""Baixa 90 dias de dados (12/07/2026 a 09/10/2026) dos 9 ativos do TCC.

Fontes grátis usadas:
- Yahoo Finance (yfinance): todos os ativos, timeframes de 1h a 24h.
- Binance: BTC/USD (par BTCUSDT) em 1 minuto, usado para montar todos os timeframes.
- Dukascopy: EUR/USD (preço BID) em 1 minuto, usado para montar todos os timeframes.

Os timeframes que a fonte não entrega direto são montados juntando candles menores
(ex.: 4h = quatro candles de 1h).

Uso: py -3.14 "Dados 90 dias/baixar_90dias.py"
"""

import lzma
import struct
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

PASTA = Path(__file__).parent
INICIO = datetime(2026, 7, 12, tzinfo=UTC)
FIM = datetime(2026, 10, 10, tzinfo=UTC)  # o dia 10/10 não entra

YAHOO = {
    "SPY": "SPY",
    "BTCUSD": "BTC-USD",
    "ITUB4": "ITUB4.SA",
    "TESLA": "TSLA",
    "IBOV": "^BVSP",
    "PETR4": "PETR4.SA",
    "MGLU3": "MGLU3.SA",
    "NQ": "NQ=F",
    "EURUSD": "EURUSD=X",  # por último: a Dukascopy é a fonte mais lenta
}
CONTINUOS = {"EURUSD", "BTCUSD", "NQ"}
# A Dukascopy recusa pedidos que não parecem vir de um navegador.
NAVEGADOR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36"}
AGREGAR = {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}
TODOS = ["1min", "2min", "3min", "5min", "15min", "30min", "1h", "2h", "4h", "6h", "8h", "12h", "24h"]
DE_1H = ["1h", "2h", "4h", "6h", "8h", "12h"]


def juntar(df, regra, continuo):
    if continuo:
        novo = df.resample(regra, origin="epoch").agg(AGREGAR)
    else:
        dias = [d.resample(regra, origin=d.index[0]).agg(AGREGAR) for _, d in df.groupby(df.index.date)]
        novo = pd.concat(dias)
    return novo.dropna(subset=["Open"])


def yahoo(codigo, intervalo):
    df = yf.download(codigo, start=INICIO, end=FIM, interval=intervalo, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df[["Open", "High", "Low", "Close", "Volume"]]


def binance_1min():
    linhas = []
    inicio = int(INICIO.timestamp() * 1000)
    fim = int(FIM.timestamp() * 1000)
    while inicio < fim:
        r = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": "BTCUSDT", "interval": "1m", "startTime": inicio, "endTime": fim - 1, "limit": 1000},
            timeout=30,
        )
        r.raise_for_status()
        dados = r.json()
        if not dados:
            break
        linhas += dados
        inicio = dados[-1][0] + 60_000
        time.sleep(0.2)
    df = pd.DataFrame([x[:6] for x in linhas], columns=["Data", "Open", "High", "Low", "Close", "Volume"])
    df["Data"] = pd.to_datetime(df["Data"], unit="ms", utc=True)
    return df.set_index("Data").astype(float)


def baixar_dia_dukascopy(dia, codigo="EURUSD"):
    # Cada dia baixado fica guardado em _cache, para não baixar de novo se o programa parar.
    cache = PASTA / "_cache" / f"{codigo}_{dia:%Y-%m-%d}.bi5"
    if cache.exists():
        return cache.read_bytes()
    # Na Dukascopy os meses começam em 00 (janeiro = 00).
    url = f"https://datafeed.dukascopy.com/datafeed/{codigo}/{dia.year}/{dia.month - 1:02d}/{dia.day:02d}/BID_candles_min_1.bi5"
    for tentativa in range(12):
        try:
            r = requests.get(url, headers=NAVEGADOR, timeout=30)
            if r.status_code == 200:
                cache.parent.mkdir(exist_ok=True)
                cache.write_bytes(r.content)
                return r.content
        except requests.RequestException:
            pass
        time.sleep(min(60, 5 * (tentativa + 1)))
    raise RuntimeError(f"Dukascopy não respondeu para {dia:%d/%m/%Y}")


def dukascopy_1min():
    partes = []
    dia = INICIO
    while dia < FIM:
        conteudo = baixar_dia_dukascopy(dia)
        if conteudo:
            bruto = lzma.decompress(conteudo, format=lzma.FORMAT_ALONE)
            for i in range(0, len(bruto), 24):
                seg, o, c, mi, ma, vol = struct.unpack(">5if", bruto[i : i + 24])
                if vol > 0:
                    partes.append((dia + timedelta(seconds=seg), o / 1e5, ma / 1e5, mi / 1e5, c / 1e5, vol))
        dia += timedelta(days=1)
        time.sleep(1)
    df = pd.DataFrame(partes, columns=["Data", "Open", "High", "Low", "Close", "Volume"])
    return df.set_index("Data")


def salvar(nome, dados, resumo, fonte):
    pasta = PASTA / nome
    pasta.mkdir(exist_ok=True)
    for tf in TODOS:
        if tf not in dados:
            continue
        df = dados[tf]
        df.index.name = "Data"
        df.to_csv(pasta / f"{nome}_{tf}.csv")
        resumo.append((nome, tf, len(df), df.index.min(), df.index.max(), fonte[tf]))
        print(f"{nome:7} {tf:6} {len(df):7} candles  {df.index.min()}  ->  {df.index.max()}  ({fonte[tf]})")


def main():
    resumo = []
    for nome, codigo in YAHOO.items():
        continuo = nome in CONTINUOS
        if nome in ("BTCUSD", "EURUSD"):
            base = binance_1min() if nome == "BTCUSD" else dukascopy_1min()
            origem = "Binance (BTCUSDT)" if nome == "BTCUSD" else "Dukascopy (BID)"
            dados = {"1min": base}
            for tf in TODOS[1:-1]:
                dados[tf] = juntar(base, tf, True)
            dados["24h"] = juntar(base, "1D", True)
            fonte = dict.fromkeys(TODOS, origem)
        else:
            h1 = yahoo(codigo, "1h")
            dados = {tf: (h1 if tf == "1h" else juntar(h1, tf, continuo)) for tf in DE_1H}
            dados["24h"] = yahoo(codigo, "1d")
            fonte = dict.fromkeys(TODOS, "Yahoo Finance")
        salvar(nome, dados, resumo, fonte)
        # Atualiza o resumo a cada ativo, para não perder nada se o programa parar no meio.
        pd.DataFrame(resumo, columns=["ativo", "timeframe", "candles", "inicio", "fim", "fonte"]).to_csv(
            PASTA / "resumo.csv", index=False
        )


if __name__ == "__main__":
    main()
