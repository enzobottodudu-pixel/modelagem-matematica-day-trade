"""
LEITOR DE DADOS DO BACKTEST — abre os candles de 90 dias e separa treino e teste.

Como usar em outro programa:
    from dados import carregar, treino_e_teste
    candles = carregar("PETR4", "5min")
    treino, teste = treino_e_teste(candles)

Rodando este arquivo direto, ele confere todos os 9 ativos x 13 timeframes
e salva a tabela em RESUMO_DADOS.md.
"""

from pathlib import Path

import pandas as pd

PASTA_DADOS = Path(__file__).resolve().parent.parent / "Dados 90 dias"

ATIVOS = ["EURUSD", "SPY", "NQ", "IBOV", "PETR4", "ITUB4", "BTCUSD", "TESLA", "MGLU3"]  # do menos ao mais volátil
TIMEFRAMES = ["1min", "2min", "3min", "5min", "15min", "30min", "1h", "2h", "4h", "6h", "8h", "12h", "24h"]
TIMEFRAMES_DE_MINUTO = ["1min", "2min", "3min", "5min", "15min", "30min"]

# Treino: 12/07 a 09/09/2026 (60 dias). Teste: 10/09 a 09/10/2026 (30 dias). Decisão do Enzo (seção 5.5).
ULTIMO_DIA_DO_TREINO = pd.Timestamp("2026-09-09").date()

# Fuso de cada mercado, para o "dia" de cada candle ser o dia do pregão daquele mercado
FUSO = {
    "EURUSD": "America/New_York",
    "SPY": "America/New_York",
    "NQ": "America/New_York",
    "TESLA": "America/New_York",
    "IBOV": "America/Sao_Paulo",
    "PETR4": "America/Sao_Paulo",
    "ITUB4": "America/Sao_Paulo",
    "MGLU3": "America/Sao_Paulo",
    "BTCUSD": "UTC",
}


# PEDAÇO 7 — horários de cada mercado (decisão 8 das regras)
# Pregão normal do ativo de verdade. Só é preciso cortar o minuto do SPY (CFD do HistData) e da Tesla (Bybit),
# que vêm com candles quase 24 h por dia; os outros arquivos já estão só no horário certo.
PREGAO_NORMAL = {"SPY": ("09:30", "16:00"), "TESLA": ("09:30", "16:00")}

# Hora em que o "dia" de negociação acaba, no fuso do mercado
FIM_DO_DIA = {
    "PETR4": 17,
    "ITUB4": 17,
    "MGLU3": 17,
    "IBOV": 17,  # B3: 10h às 17h (Brasília)
    "SPY": 16,
    "TESLA": 16,  # bolsa americana: 9h30 às 16h (Nova York)
    "NQ": 17,
    "EURUSD": 17,  # quase 24 h; o dia "vira" às 17h de Nova York
    "BTCUSD": 24,  # 24 h; o dia vira à meia-noite (UTC)
}


# Rolagem do NQ no Yahoo (achada em 02/11 comparando com o índice Nasdaq-100 do HistData, previsao/conferir.py):
# o NQ=F troca do contrato de setembro para o de dezembro de 2026 e o preço "pula" 1,0% sem o mercado se mexer.
# De 1 h a 12 h (montados do 1 h), a troca acontece no candle de 14/09 às 11h de Nova York; no diário, entre 18/09
# e 21/09. Ajuste para trás: os preços do contrato velho são multiplicados pela diferença entre os dois contratos.
NQ_ROLAGEM_FATOR = 1.00996  # razão Yahoo ÷ índice: 1,0104 depois da troca e 1,0004 antes
NQ_ROLAGEM_HORA = pd.Timestamp("2026-09-14 11:00", tz="America/New_York")
NQ_ROLAGEM_DIA = pd.Timestamp("2026-09-21", tz="America/New_York")


def ajustar_rolagem_nq(candles: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Tira o salto falso da troca de contrato do NQ do Yahoo e as sobras da hora em que a CME fica fechada."""
    candles = candles.copy()
    precos = ["Open", "High", "Low", "Close"]
    if timeframe == "24h":
        candles.loc[candles.index < NQ_ROLAGEM_DIA, precos] *= NQ_ROLAGEM_FATOR
        return candles
    if timeframe == "1h":
        candles = candles[candles.index.hour != 17]  # a CME fecha das 17h às 18h: candle nessa hora é sobra do Yahoo
    duracao = pd.Timedelta(timeframe)
    inteiro_antes = candles.index + duracao <= NQ_ROLAGEM_HORA
    misturado = (candles.index <= NQ_ROLAGEM_HORA) & ~inteiro_antes  # começa no contrato velho e fecha no novo
    candles.loc[inteiro_antes, precos] *= NQ_ROLAGEM_FATOR
    candles.loc[misturado, ["Open", "Low"]] *= NQ_ROLAGEM_FATOR
    return candles


def arquivo(ativo: str, timeframe: str) -> Path:
    """Escolhe o arquivo certo de cada ativo (as fontes estão explicadas na seção 5.3)."""
    sufixo = ""
    if timeframe in TIMEFRAMES_DE_MINUTO and ativo in ("SPY", "NQ"):
        sufixo = "_histdata"  # minuto do índice em CFD (HistData); de 1 h para cima, Yahoo
    if timeframe in TIMEFRAMES_DE_MINUTO and ativo == "TESLA":
        sufixo = "_bybit"  # minuto do contrato TSLAUSDT (Bybit); de 1 h para cima, Yahoo
    return PASTA_DADOS / ativo / f"{ativo}_{timeframe}{sufixo}.csv"


def carregar(ativo: str, timeframe: str) -> pd.DataFrame:
    """Abre os candles com o horário no fuso do mercado, uma coluna 'dia' e uma coluna 'ultima_hora'."""
    candles = pd.read_csv(arquivo(ativo, timeframe))
    if candles["Data"].str.len().max() == 10:
        # candles diários do Yahoo vêm só com a data ("2026-07-13"): é o dia daquele mercado, sem fuso
        candles["Data"] = pd.to_datetime(candles["Data"]).dt.tz_localize(FUSO[ativo])
    else:
        candles["Data"] = pd.to_datetime(candles["Data"], utc=True).dt.tz_convert(FUSO[ativo])
    candles = candles.set_index("Data").sort_index()

    # 0) NQ de 1 h para cima (Yahoo): tira o salto da troca de contrato
    if ativo == "NQ" and timeframe not in TIMEFRAMES_DE_MINUTO:
        candles = ajustar_rolagem_nq(candles, timeframe)

    # 1) só o pregão normal (SPY e Tesla nos timeframes de minuto)
    if ativo in PREGAO_NORMAL and timeframe in TIMEFRAMES_DE_MINUTO:
        inicio, fim = PREGAO_NORMAL[ativo]
        hora = candles.index.strftime("%H:%M")
        candles = candles[(hora >= inicio) & (hora < fim)]

    # 2) o dia de negociação: no NQ e no EUR/USD, o que começa às 17h ou depois já é o dia seguinte
    if ativo in ("NQ", "EURUSD"):
        candles["dia"] = (candles.index + pd.Timedelta(hours=7)).date
    else:
        candles["dia"] = candles.index.date

    # 3) última hora do dia (decisão 7: sem novas entradas nela)
    candles["ultima_hora"] = candles.index.hour == FIM_DO_DIA[ativo] - 1
    return candles


def treino_e_teste(candles: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Corta pela data: até 09/09 é treino; de 10/09 em diante é teste."""
    treino = candles[candles["dia"] <= ULTIMO_DIA_DO_TREINO]
    teste = candles[candles["dia"] > ULTIMO_DIA_DO_TREINO]
    return treino, teste


if __name__ == "__main__":
    linhas = [
        "# Dados do backtest: candles no treino e no teste",
        "",
        "Treino: 12/07 a 09/09/2026. Teste: 10/09 a 09/10/2026. Gerado por `dados.py`.",
        "",
        "| Ativo | " + " | ".join(TIMEFRAMES) + " |",
        "|---|" + "---|" * len(TIMEFRAMES),
    ]
    for ativo in ATIVOS:
        celulas = []
        for tf in TIMEFRAMES:
            treino, teste = treino_e_teste(carregar(ativo, tf))
            celulas.append(f"{len(treino)} / {len(teste)}")
        linhas.append(f"| {ativo} | " + " | ".join(celulas) + " |")
    linhas += ["", "Cada célula: candles no treino / candles no teste."]
    saida = Path(__file__).resolve().parent / "RESUMO_DADOS.md"
    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))
