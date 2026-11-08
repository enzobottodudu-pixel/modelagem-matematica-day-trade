# Comparativo de todos os resultados: as quatro estratégias e a regressão linear

*Texto de apoio escrito pelo Claude a pedido do Enzo (02/11/2026), para ele adaptar com as próprias palavras. Os números vêm de `comparativo/comparativo.py`, que junta as operações das quatro estratégias (`estrategias_2_9/`) e da regressão linear (`previsao/`); as tabelas completas estão em `COMPARATIVO.md`.*

---

## 1. O que foi comparado

Foram comparadas seis formas de usar US$1.000 em cada um dos nove ativos, no mesmo mês de teste (10/09 a 09/10/2026): as quatro estratégias da seção 2.9 (ORB, VWAP, IFR e cruzamento de médias), a regressão linear, que tenta prever a variação da próxima hora, e comprar e segurar, que compra o ativo no começo do mês e vende no fim. Para que a comparação fosse justa, todas seguiram as mesmas regras: operações de *day trade*, o capital inteiro em cada operação e os mesmos custos. Também foram calculadas, para todas, as mesmas medidas do capítulo 2: taxa de acerto, *payoff*, esperança matemática, margem de erro e *drawdown*.

## 2. O quadro geral

| Medida | ORB | VWAP | IFR | Médias | Regressão | Comprar e segurar |
|---|---|---|---|---|---|---|
| Tipo | segue a tendência | aposta na volta | aposta na volta | segue a tendência | previsão estatística | sem operações no meio |
| *Timeframe* | 30 min | 15 min | 30 min | 5 min | 1 h | — |
| Operações no mês | 210 | 399 | 153 | 1.359 | 995 | 9 |
| Taxa de acerto | 34,3% | 43,6% | 49,7% | 25,7% | 46,2% | — |
| *Payoff* | 1,68 | 0,78 | 0,93 | 1,70 | 0,83 | — |
| Ganho médio por operação antes do custo | +0,040% | +0,020% | +0,079% | +0,014% | +0,013% | — |
| Custo médio por operação | 0,094% | 0,190% | 0,114% | 0,104% | 0,077% | — |
| Esperança por operação com custos | −0,054% | −0,170% | −0,035% | −0,091% | −0,065% | — |
| **Total com custos** | **−1,4%** | **−7,1%** | **−0,7%** | **−9,2%** | **−6,4%** | **+20,6%** |
| Total sem custos | +0,9% | +0,9% | +1,3% | +2,6% | +1,2% | +20,6% |
| Ativos com lucro | 3 de 9 | 4 de 8 | 5 de 9 | 3 de 9 | 3 de 9 | 8 de 9 |
| Ativos com vantagem | 0 | 0 | 0 | 1 | 0 | — |
| Pior *drawdown* | −14,0% (MGLU3) | −39,0% (MGLU3) | −11,1% (MGLU3) | −65,7% (BTC/USD) | −38,0% (MGLU3) | — |

Com os custos, a ordem do melhor para o pior foi: IFR (−0,7%), ORB (−1,4%), regressão (−6,4%), VWAP (−7,1%) e cruzamento de médias (−9,2%). As cinco abordagens que operam perderam dinheiro, e só comprar e segurar ganhou (+20,6%). O IFR foi também o que teve lucro em mais ativos (cinco de nove).

## 3. Os custos mudam a ordem

Sem os custos, a ordem quase se inverte: o cruzamento de médias, que era o pior, passa a ser o melhor (+2,6%), seguido do IFR (+1,3%), da regressão (+1,2%), da ORB e da VWAP (+0,9% cada). Isso mostra que, antes dos custos, as cinco abordagens ficaram muito parecidas e perto de zero; o que separou as boas das ruins foi principalmente quanto cada uma pagou de custo.

Em todas as abordagens, o custo médio de uma operação foi maior que o ganho médio antes do custo. No IFR, por exemplo, cada operação ganhava em média 0,079%, mas pagava 0,114%, sobrando −0,035%. Na VWAP, o ganho médio era de 0,020% e o custo, de 0,190%, quase dez vezes maior, porque ela operou muito em ativos caros de negociar (99 operações no BTC/USD e 135 na MGLU3). A regressão foi a que teve o menor ganho antes do custo (0,013%), o que combina com o que foi visto no teste do modelo: as previsões dela são muito pequenas, quase iguais a repetir o último preço.

## 4. Quanto mais operações, maior a perda

Cada uma das 44 combinações de abordagem e ativo foi colocada num gráfico com o número de operações e o resultado. Em média, as combinações que operaram mais perderam mais:

| Número de operações no mês | Combinações | Resultado médio com custos |
|---|---|---|
| até 30 | 20 | −0,4% |
| de 31 a 100 | 16 | −4,4% |
| mais de 100 | 8 | −17,2% |

O caso mais forte foi o cruzamento de médias no BTC/USD: 435 operações, cada uma custando 0,22%, levaram a conta de US$1.000 para US$342,74 (−65,7%). Não é uma regra perfeita, porque o cruzamento de médias no NQ fez 211 operações e ganhou 8,3%; mas lá cada operação custava só 0,003%, quase nada. O que pesa, portanto, é a soma dos custos: o número de operações multiplicado pelo custo de cada uma.

## 5. Não existe uma abordagem que ganhe em todos os ativos

A melhor abordagem mudou de ativo para ativo:

| Ativo | Melhor abordagem | Resultado | Comprar e segurar |
|---|---|---|---|
| EUR/USD | ORB | −0,7% | −3,7% |
| SPY | Médias | +0,9% | +2,6% |
| NQ | Médias | +8,3% | +4,7% |
| IBOV | Regressão | +6,5% | +12,8% |
| PETR4 | ORB | +4,2% | +14,6% |
| ITUB4 | IFR | −5,3% | +22,1% |
| BTC/USD | ORB | −2,8% | +5,7% |
| Tesla | VWAP | +4,5% | +4,5% |
| MGLU3 | Médias | +8,8% | +122,2% |

A ORB foi a melhor em três ativos, o cruzamento de médias em três, e a regressão, o IFR e a VWAP em um cada. Isso indica que nenhuma delas tem uma vantagem geral: o resultado depende muito do ativo e do que ele fez no mês. Só em três ativos alguma abordagem superou comprar e segurar: no EUR/USD, que caiu no mês, quatro abordagens perderam menos que os −3,7% de comprar e segurar; no NQ, o cruzamento de médias ganhou 8,3% contra 4,7%; e na Tesla, a VWAP empatou com comprar e segurar (+4,5%).

## 6. O tipo de abordagem e o tipo de mercado

| Tipo | Operações | Total com custos | Total sem custos | Na MGLU3 |
|---|---|---|---|---|
| Seguem a tendência (ORB e médias) | 1.569 | −5,3% | +1,8% | ORB +6,9%, médias +8,8% |
| Apostam na volta (VWAP e IFR) | 552 | −3,7% | +1,1% | VWAP −39,0%, IFR +1,6% |
| Previsão estatística (regressão) | 995 | −6,4% | +1,2% | −28,4% |

Sem custos, as estratégias que seguem a tendência foram um pouco melhores (+1,8%) que as que apostam na volta (+1,1%), o que combina com um mês de alta forte na B3. Com custos, a ordem se inverte, porque as de tendência fizeram quase três vezes mais operações. A MGLU3, que subiu 122,2% no mês, mostra a diferença com mais clareza: as estratégias de tendência ganharam, e a VWAP, que vendia a cada subida esperando a volta do preço, perdeu 39,0%. A regressão também perdeu muito na MGLU3 (−28,4%), porque a ação é cara de negociar em porcentagem e o modelo operou 76 vezes.

A volatilidade também fez diferença. Nos três ativos mais calmos (EUR/USD, SPY e NQ), todos os resultados ficaram entre −2,7% e +8,3%. Nos mais voláteis (BTC/USD, Tesla e MGLU3), eles foram de −65,7% a +8,8%, e foi neles que apareceram todos os *drawdowns* acima de 30%. Quanto mais o preço se mexe, maior o risco de uma estratégia errada causar uma perda grande.

## 7. Sorte ou vantagem

Para cada combinação, foi calculada a faixa da esperança com a margem de erro (seção 2.6). Das 43 combinações com mais de uma operação, só uma teve a faixa inteira acima de zero: o cruzamento de médias no NQ, com esperança de +0,038% por operação e faixa de 0,000% a 0,076%, exatamente no limite. Por outro lado, sete combinações tiveram a faixa inteira abaixo de zero, ou seja, perderam de forma consistente, e não por azar: a ORB na Tesla, a VWAP no BTC/USD e na MGLU3, o IFR no ITUB4, o cruzamento de médias no BTC/USD e na Tesla, e a regressão no BTC/USD. Com tantos testes, encontrar uma única combinação no limite é o que se espera do acaso, como alertam Bailey et al. (2014). Por isso, nenhum dos resultados mostra uma vantagem real.

## 8. Regressão linear ou estratégias?

A regressão linear e as estratégias têm origens diferentes: a regressão é uma conta cujos pesos o computador escolheu nos dois meses de treino, enquanto as estratégias são regras criadas por pessoas a partir de indicadores do gráfico. Mesmo assim, o resultado foi parecido. A regressão teve lucro em 46,2% das operações, perto dos 50% de uma moeda, e teve o menor ganho antes do custo de todas (0,013% por operação). As estratégias não foram muito melhores: a que mais acertou, o IFR, ficou em 49,7%, também perto de uma moeda. O que fez o IFR e a ORB perderem menos que a regressão não foi prever melhor, e sim operar menos (153 e 210 operações, contra 995 da regressão).

## 9. Conclusão do comparativo

Juntando todos os resultados, nenhuma abordagem, nem as estratégias de análise técnica nem a regressão linear, conseguiu ganhar dinheiro de forma consistente no mês de teste depois dos custos. Antes dos custos, todas ficaram perto de zero, entre +0,9% e +2,6%, o que é compatível com a hipótese do mercado eficiente de Fama (1970): se os preços passados não ajudam a prever os próximos, nenhuma regra baseada neles deveria ganhar muito. O fator que mais separou os resultados foi o custo: as abordagens que operaram pouco perderam pouco, e as que operaram muito, em ativos caros de negociar, perderam muito. Comprar e segurar foi a melhor alternativa neste mês porque os mercados subiram, mas ela também perde quando o mercado cai, como no EUR/USD.

Esses resultados valem para as condições testadas: um único mês, uma versão de cada estratégia (a dos exemplos da seção 2.9) e o capital inteiro em cada operação. As próximas etapas são testar várias versões de cada estratégia no treino (seção 2.9.5), verificar se a melhor delas se mantém no teste e estudar quanto arriscar em cada operação (seção 3.8), para reduzir os *drawdowns* que apareceram nos ativos mais voláteis.
