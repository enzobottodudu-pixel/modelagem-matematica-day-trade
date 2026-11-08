# Backtest do TCC

O *backtest* das 4 estratégias, feito em Python (seção 5.4). Treino de 12/07 a 09/09/2026 e teste de 10/09 a 09/10/2026 (seção 5.5).

## Arquivos

| Arquivo | O que faz | Situação |
|---|---|---|
| `dados.py` | Abre os *candles* de `Dados 90 dias/` e corta treino e teste | pronto |
| `RESUMO_DADOS.md` | Quantos *candles* cada ativo tem no treino e no teste | pronto |
| `REGRAS_cruzamento_medias.md` | As regras exatas do cruzamento de médias | pronto (decidido em 18/10) |
| `CUSTOS.md` e `custos.py` | Custo de cada ativo (corretagem + taxas + *slippage*), com as fontes | pronto (aprovado em 18/10) |
| `motor.py` | Simula as operações, desconta os custos e fecha tudo no fim do dia | pronto (os 8 pedaços, 19/10) |
| `desenho.py` | Desenha cada dia simulado (*candles*, entrada ▲▼, saída ✕, *stop* e alvo) | pronto (19/10) |
| `imagens/` | As imagens de cada pedaço do motor (`pedaco1_...png` a `pedaco8_...png`) | geradas ao rodar `motor.py` |
| `metricas.py` | Taxa de acerto, *payoff*, esperança, acerto mínimo, margem de erro e *drawdown* (cap. 4, com as fórmulas dos programas do Enzo) | pronto (19/10) |
| `estrategia_medias.py` | O cruzamento de médias: calcula as MMEs e escreve os sinais ("o jogador") | pronto (19/10) |

## Plano do motor (`motor.py`), construído em pedaços com o Enzo

| Pedaço | O que o motor aprende | Situação |
|---|---|---|
| 1 | Resultado de uma operação, com custo (fórmula da seção 4.1) | feito (19/10) |
| 2 | Andar *candle* por *candle*: entra no *candle* seguinte ao sinal, sai no fim do dia | feito (19/10) |
| 3 | Usar dados de verdade (PETR4, 5 minutos, 15/07/2026) | feito (19/10) |
| 4 | *Stop* e alvo, olhando a máxima e a mínima (se bater os dois no mesmo *candle*, conta o *stop*) | feito (19/10) |
| 5 | Sair por sinal da estratégia: cruzamento contrário e fechamento do outro lado da média lenta | feito (19/10) |
| 6 | Entradas B (fechamento do *candle* do sinal) e C (recuo até a média rápida) | feito (19/10) |
| 7 | Horários: só o pregão normal e sem novas entradas na última hora | feito (19/10) |
| 8 | Vários dias seguidos: rodar o treino inteiro e devolver todas as operações | feito (19/10) |

Depois do motor: `metricas.py` → `estrategia_medias.py` → treino (216 versões) → teste → tabelas e gráficos.

## Ordem das estratégias

1. Cruzamento de médias móveis
2. IFR
3. ORB
4. VWAP (por último, por causa da falta de volume em alguns ativos)
