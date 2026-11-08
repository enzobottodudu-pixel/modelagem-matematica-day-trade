# Simulação com US$1.000 em cada ativo (teste: 10/09 a 09/10/2026)

Candles de 1 h. Compra se o modelo prevê alta, vende se prevê queda, fecha tudo no fim do dia, capital inteiro em cada operação, custos do `backtest/CUSTOS.md`. Gerado por `simulacao.py`.

| Ativo | Operações | Ganharam | Final com custos | Final sem custos | Buy and hold |
|---|---|---|---|---|---|
| EUR/USD | 271 | 47% | US$972,56 (-2,7%) | US$998,08 | US$962,72 |
| SPY | 75 | 49% | US$984,86 (-1,5%) | US$988,26 | US$1.026,12 |
| NQ | 166 | 64% | US$1.031,30 (+3,1%) | US$1.035,73 | US$1.046,56 |
| IBOV | 50 | 64% | US$1.064,92 (+6,5%) | US$1.092,57 | US$1.128,23 |
| PETR4 | 48 | 42% | US$941,74 (-5,8%) | US$981,27 | US$1.146,34 |
| ITUB4 | 80 | 45% | US$945,65 (-5,4%) | US$1.017,32 | US$1.220,51 |
| BTC/USD | 150 | 27% | US$745,65 (-25,4%) | US$1.037,55 | US$1.056,98 |
| Tesla | 79 | 52% | US$1.018,64 (+1,9%) | US$1.024,62 | US$1.044,80 |
| MGLU3 | 76 | 26% | US$715,78 (-28,4%) | US$930,19 | US$2.221,82 |

Somando os 9 ativos (US$9.000 no começo): modelo com custos US$8.421,09, buy and hold US$10.854,08.
