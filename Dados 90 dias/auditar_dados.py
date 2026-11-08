"""Auditoria completa da pasta Dados 90 dias (complementa o verificar_dados.py).

1. Inventário: cada ativo/fonte tem os 13 timeframes?
2. Coerência: os timeframes maiores batem com a soma dos candles menores de onde vieram?
3. Cobertura: data do primeiro e do último candle de cada arquivo.
4. Minutos faltando dentro do horário de pregão (arquivos de 1 minuto).
5. Volume: quantos candles têm volume zero (a VWAP precisa de volume).
Gera AUDITORIA.md.

Uso: py -3.14 "Dados 90 dias/auditar_dados.py"
"""

from pathlib import Path

import pandas as pd

PASTA = Path(__file__).parent
TFS = ["1min", "2min", "3min", "5min", "15min", "30min", "1h", "2h", "4h", "6h", "8h", "12h", "24h"]
REGRA = {"1min": "1min", "2min": "2min", "3min": "3min", "5min": "5min", "15min": "15min", "30min": "30min",
         "1h": "1h", "2h": "2h", "4h": "4h", "6h": "6h", "8h": "8h", "12h": "12h", "24h": "1D"}
AGREGAR = {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
# horário de pregão regular para contar minutos faltando (fuso, abertura, fechamento)
PREGAO = {
    "SPY": ("America/New_York", "09:30", "16:00"),
    "NQ": ("America/New_York", "09:30", "16:00"),
    "TESLA": ("America/New_York", "09:30", "16:00"),
    "PETR4": ("America/Sao_Paulo", "10:15", "16:55"),
    "ITUB4": ("America/Sao_Paulo", "10:15", "16:55"),
    "MGLU3": ("America/Sao_Paulo", "10:15", "16:55"),
    "IBOV": ("America/Sao_Paulo", "10:15", "16:55"),
}


def ler(caminho):
    df = pd.read_csv(caminho, index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def grupos():
    """Agrupa os arquivos por (ativo, fonte), usando o final do nome."""
    saida = {}
    for arq in sorted(PASTA.glob("*/*.csv")):
        if arq.parent.name.startswith("_"):
            continue
        partes = arq.stem.split("_")
        ativo, tf = partes[0], partes[1]
        fonte = partes[2] if len(partes) > 2 else "padrao"
        saida.setdefault((ativo, fonte), {})[tf] = arq
    return saida


def main():
    linhas = ["# Auditoria dos dados (90 dias)", ""]
    g = grupos()

    linhas += ["## 1. Inventário de timeframes", "", "| Ativo | Fonte do arquivo | Timeframes | Faltando |", "|---|---|---|---|"]
    for (ativo, fonte), tfs in sorted(g.items()):
        faltam = [t for t in TFS if t not in tfs]
        linhas.append(f"| {ativo} | {fonte} | {len(tfs)} | {', '.join(faltam) or '-'} |")

    linhas += ["", "## 2. Coerência entre timeframes", "",
               "Cada timeframe maior é refeito a partir do menor arquivo da mesma fonte e comparado.", "",
               "| Ativo | Fonte | Base | Timeframes conferidos | Diferenças |", "|---|---|---|---|---|"]
    for (ativo, fonte), tfs in sorted(g.items()):
        base_tf = next((t for t in TFS if t in tfs), None)
        base = ler(tfs[base_tf])
        continuo = ativo in {"EURUSD", "BTCUSD"} or fonte in {"histdata", "bybit"}
        conferidos, diferencas = 0, []
        for tf in TFS[TFS.index(base_tf) + 1:]:
            if tf not in tfs or tf == "24h" and not continuo:
                continue
            alvo = ler(tfs[tf])
            if continuo:
                refeito = base.resample(REGRA[tf], origin="epoch").agg(AGREGAR).dropna()
            else:
                refeito = pd.concat(
                    d.resample(REGRA[tf], origin=d.index[0]).agg(AGREGAR) for _, d in base.groupby(base.index.date)
                ).dropna()
            juntos = alvo[list(AGREGAR)].join(refeito, rsuffix="_r", how="inner")
            if len(juntos) == 0:
                continue
            conferidos += 1
            erro = max((juntos[c] - juntos[c + "_r"]).abs().div(juntos[c]).max() for c in AGREGAR)
            if erro > 1e-6 or len(juntos) < 0.95 * len(alvo):
                diferencas.append(f"{tf} (erro {erro:.2e}, {len(juntos)}/{len(alvo)} candles)")
        linhas.append(f"| {ativo} | {fonte} | {base_tf} | {conferidos} | {'; '.join(diferencas) or 'nenhuma'} |")

    linhas += ["", "## 3. Cobertura (primeiro e último candle)", "", "| Arquivo | Primeiro | Último | Candles |", "|---|---|---|---|"]
    for (ativo, fonte), tfs in sorted(g.items()):
        for tf in ("1min", "1h", "24h"):
            if tf in tfs:
                df = ler(tfs[tf])
                linhas.append(f"| {tfs[tf].name} | {df.index.min():%d/%m/%Y %H:%M} UTC | {df.index.max():%d/%m/%Y %H:%M} UTC | {len(df)} |")

    linhas += ["", "## 4. Minutos faltando no horário de pregão (arquivos de 1 minuto)", "",
               "| Arquivo | Dias de pregão | Minutos esperados | Minutos presentes | Cobertura |", "|---|---|---|---|---|"]
    for (ativo, fonte), tfs in sorted(g.items()):
        if "1min" not in tfs or ativo not in PREGAO:
            continue
        fuso, abre, fecha = PREGAO[ativo]
        local = ler(tfs["1min"]).tz_convert(fuso)
        local = local[local.index.dayofweek < 5]
        no_pregao = local.between_time(abre, fecha, inclusive="left")
        dias = no_pregao.index.normalize().nunique()
        por_dia = (pd.Timestamp(fecha) - pd.Timestamp(abre)).seconds // 60
        esperado = dias * por_dia
        linhas.append(f"| {tfs['1min'].name} | {dias} | {esperado} | {len(no_pregao)} | {len(no_pregao) / esperado * 100:.1f}% |")

    linhas += ["", "## 5. Volume", "", "| Arquivo de 1 minuto (ou o menor) | Candles com volume zero |", "|---|---|"]
    for (ativo, fonte), tfs in sorted(g.items()):
        base_tf = next(t for t in TFS if t in tfs)
        df = ler(tfs[base_tf])
        zero = (df["Volume"] <= 0).mean() * 100
        linhas.append(f"| {tfs[base_tf].name} | {zero:.1f}% |")

    (PASTA / "AUDITORIA.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
