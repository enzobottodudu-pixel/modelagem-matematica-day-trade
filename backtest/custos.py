"""
CUSTOS DE CADA ATIVO — quanto cada operação (compra + venda) perde em custos, em %.

custo = taxas (corretagem + bolsa + reguladores, já em % ida e volta)
      + slippage (1 tick na entrada + 1 tick na saída, dividido pelo preço)

Os valores e as fontes estão em CUSTOS.md (aprovados pelo Enzo em 18/10).
"""

# Taxas em % do valor, somando compra e venda
TAXAS = {
    "PETR4": 0.046,  # B3 day trade: 0,023% + 0,023%; corretagem zero
    "ITUB4": 0.046,
    "MGLU3": 0.046,
    "IBOV": 0.046,  # não é negociado direto: usa as taxas das ações
    "SPY": 0.002,  # taxa da SEC (US$20,60 por milhão), só na venda; corretagem zero
    "TESLA": 0.002,
    "EURUSD": 0.0078,  # spread 0,2 pip + comissão 0,7 pip = 0,9 pip sobre 1,1488
    "BTCUSD": 0.2,  # Binance: 0,1% na compra + 0,1% na venda
    "NQ": 0.0,  # cobrado em dólar por contrato: ver NQ_DOLARES_POR_LADO
}

# Tick = menor passo de preço (o slippage é 1 tick em cada ponta)
TICK = {
    "PETR4": 0.01,
    "ITUB4": 0.01,
    "MGLU3": 0.01,
    "IBOV": 5,  # tick do mini-índice
    "SPY": 0.01,
    "TESLA": 0.01,
    "EURUSD": 0.00001,  # 0,1 pip
    "BTCUSD": None,  # slippage em %: ver abaixo
    "NQ": 0.25,
}

BTC_SLIPPAGE_POR_LADO = 0.01  # %
NQ_DOLARES_POR_LADO = 1.29 + 1.58  # corretagem + bolsa/NFA/compensação
NQ_DOLARES_POR_PONTO = 20
SPY_NIVEL_DO_INDICE = 10  # no minuto (HistData) o SPY vem como índice S&P 500, ≈10 vezes o preço do SPY


def custo_percentual(ativo: str, preco: float, timeframe: str = "1h") -> float:
    """Custo de uma operação completa (ida e volta), em % do preço de entrada."""
    if ativo == "BTCUSD":
        return TAXAS[ativo] + 2 * BTC_SLIPPAGE_POR_LADO
    if ativo == "NQ":
        pontos = 2 * NQ_DOLARES_POR_LADO / NQ_DOLARES_POR_PONTO + 2 * TICK["NQ"]
        return pontos / preco * 100
    tick = TICK[ativo]
    if ativo == "SPY" and timeframe.endswith("min"):
        tick = tick * SPY_NIVEL_DO_INDICE  # 1 centavo do SPY = 0,1 ponto do índice
    return TAXAS[ativo] + 2 * tick / preco * 100


if __name__ == "__main__":
    # Confere com a tabela do CUSTOS.md, usando os preços médios do período
    precos = {
        "PETR4": 45.52,
        "ITUB4": 42.17,
        "MGLU3": 5.58,
        "IBOV": 180460,
        "SPY": 765,
        "TESLA": 354.38,
        "NQ": 29510,
        "EURUSD": 1.1488,
        "BTCUSD": 73441,
    }
    for ativo, preco in precos.items():
        print(f"{ativo:7} {custo_percentual(ativo, preco):.3f}%")
