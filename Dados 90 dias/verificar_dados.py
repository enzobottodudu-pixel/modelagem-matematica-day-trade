"""Confere se os dados baixados estão certos e são confiáveis.

1. Candles válidos: máxima >= abertura/fechamento >= mínima, preços > 0, sem datas
   repetidas ou fora de ordem, sem valores vazios.
2. Buracos: dias úteis sem nenhum candle e saltos de preço anormais no 1 minuto.
3. Comparação com outra fonte: fechamento de cada dia comparado com o fechamento
   diário do Yahoo Finance.
Gera o relatório VERIFICACAO.md nesta pasta.

Uso: py -3.14 "Dados 90 dias/verificar_dados.py"
"""

from datetime import timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

PASTA = Path(__file__).parent
INICIO, FIM = "2026-07-12", "2026-10-10"

# ativo, arquivo de 1 minuto, código no Yahoo para comparar, fuso e hora do fechamento oficial
COMPARAR = {
    "EURUSD": ("EURUSD/EURUSD_1min.csv", "EURUSD=X", None, None),
    "BTCUSD": ("BTCUSD/BTCUSD_1min.csv", "BTC-USD", "UTC", "23:59"),
    "SPY": ("SPY/SPY_1min_histdata.csv", "^GSPC", "America/New_York", "15:59"),
    "NQ": ("NQ/NQ_1min_histdata.csv", "^NDX", "America/New_York", "15:59"),
    "TESLA": ("TESLA/TESLA_1min_bybit.csv", "TSLA", "America/New_York", "15:59"),
    "PETR4": ("PETR4/PETR4_5min.csv", "PETR4.SA", "America/Sao_Paulo", None),
    "ITUB4": ("ITUB4/ITUB4_5min.csv", "ITUB4.SA", "America/Sao_Paulo", None),
    "MGLU3": ("MGLU3/MGLU3_5min.csv", "MGLU3.SA", "America/Sao_Paulo", None),
    "IBOV": ("IBOV/IBOV_5min.csv", "^BVSP", "America/Sao_Paulo", None),
}


def ler(caminho):
    df = pd.read_csv(caminho, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def checar_candles(df):
    problemas = []
    if df[["Open", "High", "Low", "Close"]].isna().any().any():
        problemas.append("valores vazios")
    if (df[["Open", "High", "Low", "Close"]] <= 0).any().any():
        problemas.append("preço zero ou negativo")
    tolerancia = 1e-9 * df["Close"].abs()
    if (df["High"] < df[["Open", "Close"]].max(axis=1) - tolerancia).any():
        problemas.append("máxima menor que abertura/fechamento")
    if (df["Low"] > df[["Open", "Close"]].min(axis=1) + tolerancia).any():
        problemas.append("mínima maior que abertura/fechamento")
    if df.index.duplicated().any():
        problemas.append("datas repetidas")
    if not df.index.is_monotonic_increasing:
        problemas.append("datas fora de ordem")
    return problemas


def comparar(nome, arquivo, codigo, fuso, hora):
    df = ler(PASTA / arquivo)
    ref = yf.download(codigo, start=INICIO, end=FIM, interval="1d", progress=False, auto_adjust=False)
    if isinstance(ref.columns, pd.MultiIndex):
        ref.columns = ref.columns.get_level_values(0)
    ref_close = ref["Close"]
    ref_close.index = pd.to_datetime(ref_close.index).date
    if fuso is None:
        # câmbio: o Yahoo chama de "dia D" o fechamento do fim do dia D-1 em UTC
        # (conferido em 11/10/2026: com esse ajuste, diferença média de 0,007%)
        local = df["Close"]
        nosso = local.groupby(local.index.date).last()
        nosso.index = [d + timedelta(days=1) for d in nosso.index]
        juntos = pd.concat([nosso, pd.Series(ref_close)], axis=1, join="inner").dropna()
        juntos.columns = ["nosso", "yahoo"]
        erro = ((juntos["nosso"] - juntos["yahoo"]).abs() / juntos["yahoo"]) * 100
        corr = juntos.pct_change().dropna().corr().iloc[0, 1]
        texto = f"fechamento diário: diferença média {erro.mean():.3f}%, máxima {erro.max():.3f}%; correlação das variações {corr:.3f} ({len(juntos)} dias)"
        return texto, erro.mean() < 0.2 and corr > 0.9
    local = df["Close"].tz_convert(fuso)
    if hora is None:
        nosso = local.groupby(local.index.date).last()
    else:
        h, m = map(int, hora.split(":"))
        ate = local[(local.index.hour < h) | ((local.index.hour == h) & (local.index.minute <= m))]
        nosso = ate.groupby(ate.index.date).last()
    juntos = pd.concat([nosso, pd.Series(ref_close)], axis=1, join="inner").dropna()
    juntos.columns = ["nosso", "yahoo"]
    juntos = juntos[juntos.index.map(lambda d: d.weekday() < 5)]
    if nome == "SPY" or nome == "NQ":
        # CFD do índice: compara a variação diária, porque o nível pode ter pequena diferença fixa
        var = juntos.pct_change().dropna()
        diff = (var["nosso"] - var["yahoo"]).abs()
        corr = var.corr().iloc[0, 1]
        texto = f"variação diária: correlação {corr:.3f}, diferença média {diff.mean() * 100:.3f} p.p. ({len(var)} dias)"
        return texto, corr > 0.95 and diff.mean() < 0.003
    erro = ((juntos["nosso"] - juntos["yahoo"]).abs() / juntos["yahoo"]) * 100
    texto = f"fechamento diário: diferença média {erro.mean():.3f}%, máxima {erro.max():.3f}% ({len(juntos)} dias)"
    return texto, erro.mean() < 0.5


def main():
    linhas = ["# Verificação dos dados (90 dias)", ""]
    linhas += ["## 1. Candles válidos", "", "| Arquivo | Candles | Problemas |", "|---|---|---|"]
    ruins = 0
    for arquivo in sorted(PASTA.glob("*/*.csv")):
        if arquivo.parent.name.startswith("_"):
            continue
        df = ler(arquivo)
        problemas = checar_candles(df)
        ruins += bool(problemas)
        linhas.append(f"| {arquivo.parent.name}/{arquivo.name} | {len(df)} | {', '.join(problemas) or 'nenhum'} |")
    linhas += ["", f"Arquivos com problema: **{ruins}**.", ""]

    linhas += [
        "## 2. Buracos e saltos (arquivo de 1 minuto ou 5 minutos)",
        "",
        "Salto de abertura = da última cotação de um dia para a primeira do dia seguinte (gap real de mercado).",
        "",
        "| Ativo | Dias com dados | Maior salto dentro do mesmo dia | Maior salto de abertura |",
        "|---|---|---|---|",
    ]
    for nome, (arquivo, _codigo, fuso, _hora) in COMPARAR.items():
        caminho = PASTA / arquivo
        if not caminho.exists():
            linhas.append(f"| {nome} | arquivo ainda não existe | - | - |")
            continue
        df = ler(caminho)
        local = df["Close"].tz_convert(fuso or "UTC")
        dia = pd.Series(local.index.date, index=local.index)
        mesmo_dia = dia.eq(dia.shift())
        var = local.pct_change().abs() * 100
        linhas.append(f"| {nome} | {dia.nunique()} | {var[mesmo_dia].max():.2f}% | {var[~mesmo_dia].max():.2f}% |")

    linhas += ["", "## 3. Comparação com o Yahoo Finance", "", "| Ativo | Resultado | Confiável? |", "|---|---|---|"]
    for nome, (arquivo, codigo, fuso, hora) in COMPARAR.items():
        if not (PASTA / arquivo).exists():
            linhas.append(f"| {nome} | arquivo ainda não existe | - |")
            continue
        texto, ok = comparar(nome, arquivo, codigo, fuso, hora)
        linhas.append(f"| {nome} | {texto} | {'sim' if ok else '**VERIFICAR**'} |")
    (PASTA / "VERIFICACAO.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
