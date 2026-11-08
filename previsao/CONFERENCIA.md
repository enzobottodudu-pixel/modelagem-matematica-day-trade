# Conferência dos dados, do modelo e da simulação (candles de 1 h)

Gerado por `previsao/conferir.py`. Treino: 12/07 a 09/09/2026. Teste: 10/09 a 09/10/2026.

## 1. Os candles de 1 h usados no modelo

| Ativo | Candles (treino / teste) | Primeiro e último | Repetidos | Vazios | Preço ≤ 0 | Máx/mín incoerentes | Candles por dia | Dias incompletos |
|---|---|---|---|---|---|---|---|---|
| EURUSD | 1032 / 507 | 12/07 17:00 a 09/10 16:00 | 0 | 0 | 0 | 0 | 24 | 25/09 (3) |
| SPY | 294 / 154 | 13/07 09:30 a 09/10 15:30 | 0 | 0 | 0 | 0 | 7 | nenhum |
| NQ | 956 / 506 | 12/07 18:00 a 09/10 16:00 | 0 | 0 | 0 | 0 | 23 | 17/07 (19), 08/09 (17) |
| IBOV | 292 / 154 | 13/07 10:00 a 09/10 16:00 | 0 | 0 | 0 | 0 | 7 | 31/07 (5) |
| PETR4 | 292 / 154 | 13/07 10:00 a 09/10 16:00 | 0 | 0 | 0 | 0 | 7 | 31/07 (5) |
| ITUB4 | 292 / 154 | 13/07 10:00 a 09/10 16:00 | 0 | 0 | 0 | 0 | 7 | 31/07 (5) |
| BTCUSD | 1440 / 720 | 12/07 00:00 a 09/10 23:00 | 0 | 0 | 0 | 0 | 24 | nenhum |
| TESLA | 294 / 154 | 13/07 09:30 a 09/10 15:30 | 0 | 0 | 0 | 0 | 7 | nenhum |
| MGLU3 | 292 / 154 | 13/07 10:00 a 09/10 16:00 | 0 | 0 | 0 | 0 | 7 | 31/07 (5) |

## 2. Fechamento de cada hora comparado com uma segunda fonte

| Ativo | Segunda fonte | Horas comparadas | Diferença média | Maior diferença | Variações com o mesmo sinal | Correlação das variações |
|---|---|---|---|---|---|---|
| EURUSD | Yahoo Finance (1 h, só o teste) | 496 de 1539 | 0,030% | 0,063% (18/09 16:00) | 98,3% | 0,9934 |
| SPY | HistData índice S&P 500 (1 min) | 441 de 448 | 0,004 p.p. | 0,026 p.p. (31/07 15:30) | 98,9% | 0,9996 |
| NQ | HistData índice Nasdaq-100 (1 min) | 1441 de 1462 | 0,008 p.p. | 0,361 p.p. (04/08 16:00) | 98,2% | 0,9954 |
| IBOV | Profit Pro (1 min) | 446 de 446 | 0,011% | 0,287% (14/09 16:00) | 97,4% | 0,9926 |
| PETR4 | Profit Pro (1 min) | 446 de 446 | 0,025% | 0,415% (02/09 16:00) | 98,1% | 0,9860 |
| ITUB4 | Profit Pro (1 min) | 446 de 446 | 0,030% | 0,687% (05/10 16:00) | 95,4% | 0,9756 |
| BTCUSD | Yahoo Finance (1 h, só o teste) | 720 de 2160 | 0,037% | 0,138% (16/09 10:00) | 98,3% | 0,9991 |
| TESLA | Bybit TSLAUSDT (1 min) | 448 de 448 | 0,104% | 0,300% (17/07 11:30) | 97,4% | 0,9964 |
| MGLU3 | Profit Pro (1 min) | 446 de 446 | 0,048% | 1,206% (30/09 16:00) | 99,7% | 0,9930 |

## 3. As 3 maiores variações de 1 hora de cada ativo, na segunda fonte

| Ativo | Hora | Tipo | Arquivo usado | Segunda fonte |
|---|---|---|---|---|
| EURUSD | 16/09/2026 14:00 | dentro do dia | -0,59% | -0,60% |
| EURUSD | 04/10/2026 22:00 | dentro do dia | -0,54% | -0,54% |
| EURUSD | 29/07/2026 14:00 | dentro do dia | 0,49% | não tem essa hora |
| SPY | 30/07/2026 09:30 | abertura do dia | 1,24% | 1,24% |
| SPY | 16/09/2026 14:30 | dentro do dia | -1,11% | -1,11% |
| SPY | 02/10/2026 09:30 | abertura do dia | 1,05% | 1,05% |
| NQ | 29/07/2026 15:00 | dentro do dia | -2,56% | -2,56% |
| NQ | 28/07/2026 19:00 | dentro do dia | 1,25% | 1,25% |
| NQ | 30/07/2026 09:00 | dentro do dia | 1,25% | 1,27% |
| IBOV | 05/10/2026 10:00 | abertura do dia | 8,47% | 8,29% |
| IBOV | 19/08/2026 10:00 | abertura do dia | 2,34% | 2,39% |
| IBOV | 02/09/2026 10:00 | abertura do dia | 2,31% | 2,28% |
| PETR4 | 05/10/2026 10:00 | abertura do dia | 6,61% | 6,57% |
| PETR4 | 24/08/2026 10:00 | abertura do dia | -5,49% | -5,62% |
| PETR4 | 31/08/2026 10:00 | abertura do dia | 3,56% | 3,51% |
| ITUB4 | 05/10/2026 10:00 | abertura do dia | 11,34% | 11,47% |
| ITUB4 | 02/09/2026 10:00 | abertura do dia | 2,94% | 2,83% |
| ITUB4 | 03/09/2026 10:00 | abertura do dia | 2,71% | 2,51% |
| BTCUSD | 19/08/2026 15:00 | dentro do dia | 3,99% | não tem essa hora |
| BTCUSD | 21/08/2026 08:00 | dentro do dia | 3,87% | não tem essa hora |
| BTCUSD | 18/09/2026 13:00 | dentro do dia | 2,60% | 2,63% |
| TESLA | 23/07/2026 09:30 | abertura do dia | -13,40% | -13,34% |
| TESLA | 04/09/2026 09:30 | abertura do dia | -6,14% | -6,05% |
| TESLA | 03/09/2026 09:30 | abertura do dia | 6,07% | 6,12% |
| MGLU3 | 05/10/2026 10:00 | abertura do dia | 25,07% | 25,23% |
| MGLU3 | 02/09/2026 11:00 | dentro do dia | 9,29% | 9,29% |
| MGLU3 | 02/09/2026 10:00 | abertura do dia | 9,29% | 9,52% |

## 4. Modelo e simulação refeitos de outro jeito

| Ativo | Último dia do treino | Primeiro dia do teste | Maior diferença nos pesos | Maior diferença nas previsões | Operações | Custo por operação | Final com custos (refeito) | Está no CAPITAL.md? | Comprar e segurar (refeito) |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 09/09 | 10/09 | 4.5e-17 | 9.9e-15 p.p. | 271 | 0,010% | US$972,56 | sim | US$962,72 |
| SPY | 09/09 | 10/09 | 9.7e-17 | 1.9e-14 p.p. | 75 | 0,005% | US$984,86 | sim | US$1.026,12 |
| NQ | 09/09 | 10/09 | 1.2e-16 | 1.6e-14 p.p. | 166 | 0,003% | US$1.031,30 | sim | US$1.046,56 |
| IBOV | 09/09 | 10/09 | 6.9e-17 | 1.1e-14 p.p. | 50 | 0,051% | US$1.064,92 | sim | US$1.128,23 |
| PETR4 | 09/09 | 10/09 | 1.1e-16 | 9.8e-15 p.p. | 48 | 0,086% | US$941,74 | sim | US$1.146,34 |
| ITUB4 | 09/09 | 10/09 | 1.2e-16 | 2.2e-14 p.p. | 80 | 0,091% | US$945,65 | sim | US$1.220,51 |
| BTCUSD | 09/09 | 10/09 | 4.9e-17 | 1.0e-14 p.p. | 150 | 0,220% | US$745,65 | sim | US$1.056,98 |
| TESLA | 09/09 | 10/09 | 2.3e-17 | 9.9e-15 p.p. | 79 | 0,007% | US$1.018,64 | sim | US$1.044,80 |
| MGLU3 | 09/09 | 10/09 | 2.1e-17 | 1.1e-14 p.p. | 76 | 0,344% | US$715,78 | sim | US$2.221,82 |
