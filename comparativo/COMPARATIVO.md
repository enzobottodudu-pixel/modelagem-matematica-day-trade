# Comparativo: as 4 estratégias da seção 2.9, a regressão linear e buy and hold

Teste de 10/09 a 09/10/2026, US$1.000 em cada ativo, com custos (salvo indicado). Gerado por `comparativo/comparativo.py`.

## 1. Quadro geral

| Medida | ORB | VWAP | IFR | Médias | Regressão | Buy and hold |
|---|---|---|---|---|---|---|
| Tipo | segue a tendência | aposta na volta | aposta na volta | segue a tendência | previsão estatística | nenhuma operação no meio |
| Timeframe | 30 min | 15 min | 30 min | 5 min | 1 h | — |
| Ativos testados | 9 | 8 | 9 | 9 | 9 | 9 |
| Operações no mês | 210 | 399 | 153 | 1.359 | 995 | 9 |
| Taxa de acerto | 34,3% | 43,6% | 49,7% | 25,7% | 46,2% | — |
| Payoff | 1,68 | 0,78 | 0,93 | 1,70 | 0,83 | — |
| Ganho médio por operação, antes do custo | +0,040% | +0,020% | +0,079% | +0,014% | +0,013% | — |
| Custo médio por operação | 0,094% | 0,190% | 0,114% | 0,104% | 0,077% | — |
| Esperança por operação, com custos | -0,054% | -0,170% | -0,035% | -0,091% | -0,065% | — |
| **Total com custos** | **-1,4%** | **-7,1%** | **-0,7%** | **-9,2%** | **-6,4%** | **+20,6%** |
| Total sem custos | +0,9% | +0,9% | +1,3% | +2,6% | +1,2% | +20,6% |
| Ativos com lucro | 3 de 9 | 4 de 8 | 5 de 9 | 3 de 9 | 3 de 9 | 8 de 9 |
| Ativos com vantagem (faixa acima de zero) | 0 | 0 | 0 | 1 | 0 | — |
| Ativos com desvantagem (faixa abaixo de zero) | 1 | 2 | 1 | 2 | 1 | — |
| Melhor ativo | MGLU3 (+6,9%) | Tesla (+4,5%) | Tesla (+3,6%) | MGLU3 (+8,8%) | IBOV (+6,5%) | — |
| Pior ativo | Tesla (-9,6%) | MGLU3 (-39,0%) | BTC/USD (-6,7%) | BTC/USD (-65,7%) | MGLU3 (-28,4%) | — |
| Pior drawdown | -14,0% (MGLU3) | -39,0% (MGLU3) | -11,1% (MGLU3) | -65,7% (BTC/USD) | -38,0% (MGLU3) | — |

## 2. Cada ativo (ganho ou perda com custos)

| Ativo | ORB | VWAP | IFR | Médias | Regressão | Buy and hold | Melhor abordagem | Ganhou de buy and hold? |
|---|---|---|---|---|---|---|---|---|
| EUR/USD | -0,7% | sem volume | -1,0% | -1,3% | -2,7% | -3,7% | ORB | ORB, IFR, Médias, Regressão |
| SPY | -1,6% | +0,0% | +0,9% | +0,9% | -1,5% | +2,6% | Médias | nenhuma |
| NQ | +2,2% | +1,4% | +0,8% | +8,3% | +3,1% | +4,7% | Médias | Médias |
| IBOV | -5,2% | +2,0% | +0,7% | -3,5% | +6,5% | +12,8% | Regressão | nenhuma |
| PETR4 | +4,2% | -0,3% | -0,5% | -9,1% | -5,8% | +14,6% | ORB | nenhuma |
| ITUB4 | -5,8% | -6,7% | -5,3% | -6,5% | -5,4% | +22,1% | IFR | nenhuma |
| BTC/USD | -2,8% | -18,5% | -6,7% | -65,7% | -25,4% | +5,7% | ORB | nenhuma |
| Tesla | -9,6% | +4,5% | +3,6% | -14,6% | +1,9% | +4,5% | VWAP | VWAP |
| MGLU3 | +6,9% | -39,0% | +1,6% | +8,8% | -28,4% | +122,2% | Médias | nenhuma |

## 3. Por tipo de abordagem

| Tipo | Operações | Total com custos | Total sem custos | MGLU3 |
|---|---|---|---|---|
| Seguem a tendência (ORB e Médias) | 1.569 | -5,3% | +1,8% | ORB +6,9%, Médias +8,8% |
| Apostam na volta (VWAP e IFR) | 552 | -3,7% | +1,1% | VWAP -39,0%, IFR +1,6% |
| Previsão estatística (regressão) | 995 | -6,4% | +1,2% | Regressão -28,4% |
