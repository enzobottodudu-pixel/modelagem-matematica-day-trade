"""Baixa 90 dias de candles de 1 minuto do HistData (grátis) e monta os 13 timeframes.

- EUR/USD: fonte única do ativo (todos os timeframes).
- S&P 500 (SPXUSD) e Nasdaq-100 (NSXUSD): índices em CFD, usados nos timeframes de minuto
  de SPY e NQ. Os preços são do índice, não do ETF SPY nem do futuro NQ, por isso os
  arquivos levam o final "_histdata".
Os horários do HistData são de Nova York (com horário de verão); aqui tudo vira UTC.

Uso: py -3.14 "Dados 90 dias/baixar_histdata.py"
"""

import io
import re
import time
import zipfile

import pandas as pd
import requests

from baixar_90dias import FIM, INICIO, NAVEGADOR, PASTA, TODOS, juntar

# código no HistData, pasta do ativo no TCC, final do nome do arquivo
PARES = {
    "EURUSD": ("EURUSD", ""),
    "SPXUSD": ("SPY", "_histdata"),
    "NSXUSD": ("NQ", "_histdata"),
}
MESES = [(2026, 7), (2026, 8), (2026, 9), (2026, 10)]


def baixar_mes(sessao, par, ano, mes):
    pagina = f"https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{par.lower()}/{ano}/{mes}"
    html = sessao.get(pagina, timeout=60).text
    token = re.search(r'id="tk" value="([^"]+)"', html).group(1)
    dados = {"tk": token, "date": str(ano), "datemonth": f"{ano}{mes:02d}", "platform": "ASCII", "timeframe": "M1", "fxpair": par}
    resposta = sessao.post("https://www.histdata.com/get.php", data=dados, headers={"Referer": pagina}, timeout=120)
    arquivo = zipfile.ZipFile(io.BytesIO(resposta.content))
    nome = next(n for n in arquivo.namelist() if n.endswith(".csv"))
    df = pd.read_csv(arquivo.open(nome), sep=";", header=None, names=["Data", "Open", "High", "Low", "Close", "Volume"])
    # Conferido contra o Yahoo em 11/10/2026: os horários batem com Nova York COM horário de
    # verão (com UTC-5 fixo, como diz o site, tudo ficava 1 hora atrasado).
    horario = pd.to_datetime(df["Data"], format="%Y%m%d %H%M%S")
    df["Data"] = horario.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC")
    df = df.dropna(subset=["Data"])
    return df.set_index("Data")


def main():
    sessao = requests.Session()
    sessao.headers.update(NAVEGADOR)
    for par, (nome, final) in PARES.items():
        meses = []
        for ano, mes in MESES:
            meses.append(baixar_mes(sessao, par, ano, mes))
            time.sleep(2)
        base = pd.concat(meses).sort_index()
        base = base[(base.index >= INICIO) & (base.index < FIM)]
        base = base[~base.index.duplicated()]
        pasta = PASTA / nome
        pasta.mkdir(exist_ok=True)
        for tf in TODOS:
            df = base if tf == "1min" else juntar(base, "1D" if tf == "24h" else tf, True)
            df.index.name = "Data"
            df.to_csv(pasta / f"{nome}_{tf}{final}.csv")
            print(f"{nome:6} {tf:6} {len(df):7} candles  {df.index.min()} -> {df.index.max()}  (HistData {par})")


if __name__ == "__main__":
    main()
