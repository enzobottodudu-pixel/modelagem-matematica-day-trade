# Regras usadas na simulação das 4 estratégias (02/11/2026)

As regras são as dos exemplos da seção 2.9 (Figuras 33 a 36), sem nenhuma mudança e sem escolher números no treino.
Por isso o mês de treino (12/07 a 09/09) não foi usado para nada, a não ser para "aquecer" o IFR e as médias,
que precisam dos *candles* anteriores. Tudo foi simulado só no mês de teste (10/09 a 09/10/2026).
As regras definitivas, e as versões a testar (seção 2.9.5), ainda serão decididas com o orientador.

## As 4 estratégias

| Estratégia | *Timeframe* | Entrada | Saída no alvo | *Stop* | Exemplo conferido |
|---|---|---|---|---|---|
| ORB | 30 min | faixa = máxima e mínima do 1º *candle* do dia; compra quando o preço passa da máxima (no preço da máxima), vende quando passa da mínima; 1 operação por dia | 3 vezes o tamanho da faixa, a partir da entrada | o outro lado da faixa | Figura 33: PETR4 15/09 compra 49,30 → alvo 50,11 às 12h00; 16/09 venda 49,67 → alvo 48,74 às 12h00 (iguais) |
| VWAP | 15 min | o *candle* fecha 0,6% ou mais acima da VWAP → vende no fechamento; 0,6% ou mais abaixo → compra | o preço voltar a tocar a VWAP (a do *candle* anterior, que já era conhecida) | 0,6% contra | Figura 34 (03/09 é do treino, não entra) |
| IFR | 30 min | IFR de 14 períodos (Wilder) ≤ 30 → compra no fechamento; ≥ 70 → vende | o IFR voltar a 50 (sai no fechamento) | 1% contra | Figura 35 (03/08 é do treino, não entra) |
| Médias | 5 min | a MME 9 cruza a MME 21 para cima → compra no fechamento; para baixo → vende; no cruzamento contrário, vira a mão | — (sai no cruzamento contrário) | 1,5% contra | Figura 36: Tesla 16/09 compra 09h40 → vira 12h15 → fecha 15h55 (mesmos horários) |

## Iguais para as 4 (as mesmas do `backtest/motor.py` e da simulação do modelo)

- *Day trade*: tudo fecha no fechamento do último *candle* do dia, e o último *candle* não abre nada.
- O *stop* e o alvo são conferidos pela máxima e pela mínima de cada *candle*. Se os dois forem atingidos no mesmo *candle*, conta o *stop* (o caso pior). Se o *candle* já abre depois do nível (um *gap*), sai na abertura.
- No *candle* da entrada, só o *stop* é conferido (não dá para saber se a máxima veio antes ou depois da entrada).
- Depois de sair, a VWAP e o IFR só podem entrar de novo a partir do *candle* seguinte (como nas Figuras 34 e 35).
- Capital: US$1.000 em cada ativo e em cada estratégia; cada operação usa o capital inteiro, sem alavancagem.
- Resultado de cada operação = retorno − custo, em % (fórmula da seção 2.1). Custo de ida e volta do `backtest/CUSTOS.md`.
- Comparação: o modelo de previsão (`previsao/`) e comprar e segurar, no mesmo mês.

## Dados de cada ativo

| Ativo | De onde vêm os *candles* de 5, 15 e 30 min | Volume para a VWAP |
|---|---|---|
| PETR4, ITUB4, MGLU3, IBOV | Profit Pro (10h às 17h) | Profit Pro |
| BTC/USD | Binance (24 h, dia em UTC) | Binance |
| Tesla | Bybit, contrato TSLAUSDT (só 9h30 às 16h de Nova York) | Bybit |
| SPY | HistData, índice S&P 500 (só 9h30 às 16h) | Yahoo Finance, SPY (só o mês de teste) |
| NQ | HistData, índice Nasdaq-100 (dia vira às 17h de Nova York) | Yahoo Finance, NQ=F (só o mês de teste) |
| EUR/USD | HistData (dia vira às 17h de Nova York) | não existe: o câmbio não tem volume centralizado, então a VWAP não foi calculada |

## Limitações

- Um mês só de teste e uma única versão de cada estratégia (os números dos exemplos).
- O total da VWAP tem 8 ativos (sem o EUR/USD); os outros têm 9.
- Os ativos em reais e o NQ foram simulados em %, como se os US$1.000 estivessem aplicados neles.
- O HistData não tem o EUR/USD de sexta-feira, 25/09/2026.
