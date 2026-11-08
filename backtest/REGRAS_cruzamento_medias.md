# Cruzamento de médias móveis: regras exatas

Esta folha transforma a estratégia em regras que o computador consegue seguir
(1º objetivo específico do TCC). **Cada decisão é do Enzo.** A coluna "Sugestão" é só uma recomendação.

## A ideia da estratégia, em uma frase

Quando a **média rápida** (poucos *candles*) cruza **para cima** a **média lenta** (muitos *candles*),
o preço está ganhando força para subir: **compra**. Quando cruza **para baixo**: **vende**.

```
preço  ──╮        ╭──────
média rápida ─────╳─────   ← cruzou para cima: COMPRA
média lenta  ─────────────
```

## Decisões

| # | Decisão | Opções | Sugestão | Decisão do Enzo |
|---|---|---|---|---|
| 1 | **Tipo de média** | simples (MMS) ou exponencial (MME) | **MME**: reage mais rápido, e é a da Figura 5 | ✅ MME |
| 2 | **Pares de médias testados no treino** | ex.: 5/20, 9/21, 20/50 | **5/20, 9/21 e 20/50** (o treino escolhe o melhor) | ✅ 5/20, 9/21, 20/50 |
| 3 | **Direção** | só compra, ou compra e venda | **compra e venda** (seção 3.2: dá para ganhar na alta e na baixa) | ✅ compra e venda |
| 4 | **Quando entra** | abertura do próximo *candle*, fechamento do *candle* do cruzamento, ou um preço determinado | ver "Versões testadas no treino" abaixo | ✅ testar A, B e C |
| 5 | **Quando sai** | cruzamento contrário, *stop*, alvo, condição específica, fim do dia | ver "Versões testadas no treino" abaixo | ✅ alvo e condição (com e sem) |
| 6 | ***Stop*** | sem *stop*, ou *stop* fixo em % | testar **duas versões no treino**: sem *stop* e com *stop* de 1% | ✅ sem *stop* e 1% |
| 7 | **Fim do dia** | fechar no último *candle*, ou também parar de abrir operações num horário | ver "Versões testadas no treino" abaixo | ✅ sem limite e sem entradas na última hora |
| 8 | **Horário de cada mercado** | pregão normal ou 24 h | **só o pregão normal** nas bolsas (ver tabela abaixo); 24 h só onde o mercado é 24 h | ✅ |
| 9 | **Médias "zeram" todo dia?** | continuam do dia anterior, ou recomeçam | **continuam**: a média usa os *candles* anteriores, só a operação fecha no dia | ✅ continuam |
| 10 | **Como medir o resultado** | em dinheiro (US$/R$) ou em % | **em %** por operação (seção 4.1): dá para comparar ativos de preços diferentes | ✅ em % |
| 11 | **Custos** | definidos no passo 2 | ver a folha de custos (próximo passo) | |

## Versões testadas no treino (decisões 4, 5 e 7 do Enzo, 18/10)

Valores **confirmados pelo Enzo em 18/10**.

| Item | Versões | O que significa |
|---|---|---|
| **Entrada** | A) abertura do próximo *candle* | o cruzamento fecha, e a ordem entra no começo do *candle* seguinte |
| | B) fechamento do *candle* do cruzamento | entra no próprio preço de fechamento, no instante em que o cruzamento se confirma |
| | C) preço determinado: **volta até a média rápida** | depois do cruzamento, espera o preço voltar até a média rápida (um "recuo") para entrar mais barato; se não voltar até o fim do dia, não entra |
| **Alvo** | sem alvo, **1%** ou **2%** | fecha com lucro quando o preço anda essa porcentagem a favor |
| **Condição de saída** | **com e sem**: fechamento do outro lado da média lenta | se um *candle* fecha abaixo da média lenta (na compra) ou acima (na venda), a operação fecha no fechamento desse *candle* |
| **Horário-limite** | sem limite, ou **sem novas entradas na última hora** do dia | as operações abertas continuam e fecham no fim do dia |

Regras fixas, que valem para todas as versões:
- a operação também fecha no **cruzamento contrário** e, sempre, **no fim do dia**;
- se o *stop* e o alvo forem atingidos dentro do mesmo *candle*, o programa considera que o **_stop_ veio primeiro** (o caso pior, para não exagerar o resultado);
- uma operação por vez;
- **virar a mão (decisão do Enzo, 19/10):** quando sai da compra por cruzamento contrário (sinal de venda), o mesmo sinal já abre uma venda no *candle* seguinte (e vice-versa).

**Cuidado com o número de versões:** quanto mais versões o treino testa, maior a chance de uma delas ganhar só por sorte
(*overfitting*, Bailey et al., 2014). Com os valores acima, são 3 pares × 3 entradas × 2 *stops* × 3 alvos × 2 condições × 2 horários = **216 versões**
por ativo e *timeframe*. Por isso o teste (30 dias guardados) é tão importante.

## Horário de cada mercado (decisão 8)

| Ativo | Pregão usado (sugestão) | Fim do "dia" |
|---|---|---|
| PETR4, ITUB4, MGLU3, IBOV | 10h às 17h (Brasília) | 17h |
| SPY, Tesla | 9h30 às 16h (Nova York) | 16h |
| NQ | domingo 18h a sexta 17h (Nova York), quase 24 h | 17h (NY) |
| EUR/USD | 24 h, de segunda a sexta | 17h (NY), horário padrão de virada do câmbio |
| BTC/USD | 24 h, todos os dias | 0h (UTC) |

Atenção: nos *timeframes* de minuto, o SPY (CFD do HistData) e a Tesla (Bybit) têm *candles* quase 24 h por dia.
Com a decisão 8, o programa usa só os *candles* do pregão normal, para ficar igual ao ativo de verdade.

## Um detalhe dos *timeframes* grandes

Nas bolsas, o pregão tem menos de 8 h. Então, nos *timeframes* de 8 h, 12 h e 24 h, existe **um *candle* por dia**.
Em *day trade*, isso significa: o cruzamento acontece em um dia, a operação abre na abertura do dia seguinte
e fecha no fechamento desse mesmo dia. Funciona, mas gera poucas operações (já está na seção 5.6).
