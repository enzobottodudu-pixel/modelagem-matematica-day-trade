# Modelo de previsão e simulação com capital

*Texto de apoio escrito pelo Claude a pedido do Enzo (02/11/2026), para ele adaptar com as próprias palavras. Os números vêm de `previsao.py`, `simulacao.py` e `conferir.py`, rodando com os dados reais da pasta `Dados 90 dias/`.*

---

## 1. O que foi testado

Os resultados desta parte do trabalho não vieram de nenhuma das quatro estratégias descritas na seção 2.9 (ORB, VWAP, IFR e cruzamento de médias móveis). Eles vieram de um modelo estatístico de previsão, uma regressão linear, que tenta adivinhar quanto o preço vai variar na próxima hora a partir das variações das horas anteriores. A pergunta que esse modelo responde é mais simples e vem antes das estratégias: usando só os preços passados, é possível prever o preço futuro melhor do que o acaso? Se nem um modelo matemático feito para prever consegue isso, fica mais claro por que uma regra olhando o gráfico também precisa ser testada com cuidado. As quatro estratégias ainda serão testadas no *backtest*, com a mesma divisão dos dados e a mesma simulação com capital descritas aqui.

## 2. Os dados

Foram usados os nove ativos escolhidos para o trabalho: EUR/USD, SPY, NQ, IBOV, PETR4, ITUB4, BTC/USD, Tesla e MGLU3. Em todos eles foram usados *candles* de 1 hora (*timeframe* de 1 hora), de 12/07/2026 a 09/10/2026, cerca de 90 dias. Os dados vieram do Yahoo Finance (SPY, NQ, Tesla e as ações e o índice da B3), da Binance (BTC/USD) e do HistData (EUR/USD). Cada ativo foi lido no horário do seu próprio mercado: Nova York para EUR/USD, SPY, NQ e Tesla; São Paulo para a B3; e o horário universal (UTC) para o BTC/USD, que é negociado 24 horas por dia.

Antes de usar os dados, eles foram conferidos hora por hora com uma segunda fonte independente: o Profit Pro para a B3, a Bybit para a Tesla, o HistData para o SPY e o NQ, e o Yahoo Finance para o EUR/USD e o BTC/USD. A diferença média entre as duas fontes ficou entre 0,004% e 0,10%, e de 95% a 99,7% das horas subiram ou caíram igual nas duas. Os maiores saltos também foram confirmados nas duas fontes, como a alta de 25% da MGLU3 na abertura de 05/10/2026, o primeiro pregão depois do primeiro turno da eleição, e a queda de 13,4% da Tesla em 23/07/2026. A conferência encontrou um erro, que foi corrigido: no dia 14/09/2026, a série do NQ no Yahoo trocou o contrato futuro de setembro pelo de dezembro, e o preço "pulou" 1% sem o mercado ter se mexido. Os preços de antes da troca foram ajustados para a série ficar contínua.

## 3. Divisão em treino e teste

Os dados de cada ativo foram divididos em duas partes. A parte de treino vai de 12/07 a 09/09/2026 (cerca de dois meses) e é a única que o modelo pode usar para aprender. A parte de teste vai de 10/09 a 09/10/2026 (o último mês) e fica guardada até o fim: o modelo não a vê durante o treino. Na PETR4, por exemplo, isso deu 289 horas de treino e 153 horas de teste.

Essa separação é importante porque um modelo sempre parece bom nos dados que ele usou para aprender. É como um aluno que decora as respostas da lista de exercícios: ele acerta tudo na lista, mas isso não mostra se ele vai bem na prova. Bailey et al. (2014) mostram que testar muitas versões de uma estratégia nos mesmos dados quase sempre produz uma versão que parece lucrativa só por acaso, o chamado sobreajuste (*overfitting*). Só o resultado na parte de teste mostra se o modelo funciona em dados novos.

## 4. O modelo: regressão linear com as 3 últimas variações

Primeiro, o preço de cada hora foi transformado em variação percentual, isto é, quanto o preço mudou em relação à hora anterior:

variação = (fechamento da hora ÷ fechamento da hora anterior) − 1

Se a PETR4 fechou uma hora em R$50,00 e a hora seguinte em R$50,50, a variação foi de (50,50 ÷ 50,00) − 1 = 0,01, ou seja, +1%.

O modelo tenta prever a variação da próxima hora com uma conta que usa as três últimas variações:

variação prevista = a + b₁ × última variação + b₂ × penúltima variação + b₃ × antepenúltima variação

Os números a, b₁, b₂ e b₃ são os "pesos" do modelo. Eles foram escolhidos pelo método dos mínimos quadrados, usando só a parte de treino: o computador testa os pesos que deixam a soma dos erros ao quadrado a menor possível nos dois meses de treino. Cada ativo tem os seus próprios pesos. Depois, o preço previsto é calculado a partir do último preço real:

preço previsto = último preço × (1 + variação prevista)

Na PETR4, os pesos encontrados no treino foram a = 0,0705%, b₁ = −0,057, b₂ = −0,070 e b₃ = 0,039. Se as três últimas horas tivessem variado +1,0%, 0,0% e −0,5%, a previsão seria:

0,0705% + (−0,057 × 1,0%) + (−0,070 × 0,0%) + (0,039 × −0,5%) = 0,0705% − 0,057% − 0% − 0,0195% = −0,006%

Com a PETR4 a R$50,00, o preço previsto para a próxima hora seria R$50,00 × (1 − 0,00006) = R$49,997. Na prática, o modelo prevê que o preço vai ficar quase igual. Os pesos são números pequenos e perto de zero, o que já indica que as variações passadas quase não ajudam a adivinhar a próxima.

## 5. Como o modelo foi avaliado

No mês de teste, a cada hora, o modelo previu o preço da hora seguinte, e a previsão foi comparada com o preço que de fato aconteceu. Foram usadas três medidas:

- **Erro médio:** a diferença média, em %, entre o preço previsto e o real.
- **Palpite ingênuo:** para saber se o modelo ajuda, ele foi comparado com o palpite mais simples possível, de que a próxima hora fecha no mesmo preço da última. Se o modelo não erra menos que esse palpite, ele não está prevendo nada.
- **Acerto da direção:** em quantas horas o modelo acertou se o preço ia subir ou cair. Jogando uma moeda, o acerto esperado é de 50%.

| Ativo | Erro médio do modelo | Erro do palpite ingênuo | Acerto da direção |
|---|---|---|---|
| EUR/USD | 0,050% | 0,049% | 49,4% |
| SPY | 0,168% | 0,165% | 46,7% |
| NQ | 0,134% | 0,132% | 48,7% |
| IBOV | 0,345% | 0,347% | 55,6% |
| PETR4 | 0,550% | 0,541% | 50,0% |
| ITUB4 | 0,526% | 0,514% | 49,7% |
| BTC/USD | 0,237% | 0,236% | 50,1% |
| Tesla | 0,484% | 0,479% | 53,9% |
| MGLU3 | 1,358% | 1,336% | 42,9% |

Em oito dos nove ativos, o modelo errou igual ou um pouco mais que o palpite ingênuo; só no IBOV ele foi 0,002 ponto percentual melhor. O acerto da direção ficou entre 42,9% e 55,6%, perto dos 50% de uma moeda. Nos gráficos de preço real e previsto, a linha prevista parece acompanhar a real, mas isso acontece porque ela é praticamente a linha real atrasada uma hora: o modelo quase sempre repete o último preço. O tamanho das previsões mostra isso: na PETR4, o modelo previu em média variações de 0,08% por hora, enquanto o preço real variou em média 0,54%, quase sete vezes mais.

## 6. Simulação com capital inicial de US$1.000

Para saber o que aconteceria com dinheiro, foi feita uma simulação com US$1.000 em cada ativo, no mês de teste, seguindo estas regras:

1. No fim de cada hora, se o modelo prevê alta, a simulação fica comprada na hora seguinte; se prevê queda, fica vendida (ganha se o preço cair).
2. Enquanto a previsão não muda de lado, a operação continua aberta. Quando muda, a operação é fechada e outra é aberta no sentido contrário ("virar a mão").
3. Como é *day trade*, tudo é fechado no último *candle* do dia, e nenhuma operação passa a noite aberta.
4. Cada operação usa o capital inteiro, sem alavancagem.
5. Em cada operação é descontado o custo de ida e volta (corretagem, taxas da bolsa e *slippage* de um *tick* na entrada e outro na saída). Em média, esse custo foi de 0,003% no NQ, 0,005% no SPY, 0,007% na Tesla, 0,010% no EUR/USD, 0,051% no IBOV, 0,086% na PETR4, 0,091% no ITUB4, 0,22% no BTC/USD e 0,34% na MGLU3 (a ação custa pouco, então um centavo de *slippage* pesa muito em porcentagem).

Para comparar, também foi calculado o resultado de só comprar o ativo no começo do teste e vender no fim, sem fazer nenhuma operação no meio ("comprar e segurar"). Os ativos negociados em reais e o NQ foram simulados em porcentagem, como se os US$1.000 estivessem aplicados neles, sem considerar o câmbio nem o tamanho mínimo do contrato do NQ.

| Ativo | Operações | Final com custos | Final sem custos | Comprar e segurar |
|---|---|---|---|---|
| IBOV | 50 | US$1.064,92 (+6,5%) | US$1.092,57 | US$1.128,23 |
| NQ | 166 | US$1.031,30 (+3,1%) | US$1.035,73 | US$1.046,56 |
| Tesla | 79 | US$1.018,64 (+1,9%) | US$1.024,62 | US$1.044,80 |
| SPY | 75 | US$984,86 (−1,5%) | US$988,26 | US$1.026,12 |
| EUR/USD | 271 | US$972,56 (−2,7%) | US$998,08 | US$962,72 |
| ITUB4 | 80 | US$945,65 (−5,4%) | US$1.017,32 | US$1.220,51 |
| PETR4 | 48 | US$941,74 (−5,8%) | US$981,27 | US$1.146,34 |
| BTC/USD | 150 | US$745,65 (−25,4%) | US$1.037,55 | US$1.056,98 |
| MGLU3 | 76 | US$715,78 (−28,4%) | US$930,19 | US$2.221,82 |
| **Total** | **995** | **US$8.421,09 (−6,4%)** | **US$9.105,59 (+1,2%)** | **US$10.854,08 (+20,6%)** |

## 7. O que os resultados mostram

O modelo terminou com lucro em três ativos (IBOV, NQ e Tesla) e com prejuízo em seis. Somando os nove, os US$9.000 iniciais viraram US$8.421,09, uma perda de 6,4%. Mesmo nos três ativos com lucro, só comprar no começo e vender no fim deu mais dinheiro, sem nenhuma operação. Isso indica que o lucro nesses ativos veio da alta do mercado no mês, e não de uma capacidade real de prever.

Os custos foram decisivos. Sem custos, o total teria sido de US$9.105,59 (+1,2%), muito perto de zero; com custos, a perda foi de US$684,50 a mais. O BTC/USD mostra isso com clareza: sem custos, o modelo teria terminado com US$1.037,55, mas com 150 operações e um custo de 0,22% em cada uma, terminou com US$745,65. A variação média que o modelo previa no BTC/USD era de só 0,017% por hora, treze vezes menor que o custo de uma operação. Um modelo que prevê variações menores que o custo não tem como ganhar dinheiro, mesmo quando acerta a direção.

Esses resultados combinam com a hipótese do mercado eficiente de Fama (1970): se o preço de agora já reflete as informações do passado, as variações passadas não ajudam a prever as próximas, e o preço se comporta quase como um passeio aleatório. O modelo de regressão serve, portanto, como uma referência para o resto do trabalho: qualquer estratégia que diga ganhar dinheiro com os mesmos dados precisa fazer melhor do que ele e do que só comprar e segurar, e depois de descontar os custos.

## 8. Relação com as quatro estratégias do trabalho

O modelo de regressão é diferente das quatro estratégias da seção 2.9. Ele não usa nenhum indicador técnico: só faz uma conta com as três últimas variações do preço, e os pesos dessa conta são escolhidos pelo computador. As estratégias, por outro lado, são regras escritas por pessoas, baseadas em indicadores do gráfico:

- **ORB (rompimento da faixa de abertura):** marca a máxima e a mínima do começo do pregão e compra quando o preço passa acima dessa faixa, ou vende quando passa abaixo. Zarattini, Barbon e Aziz (2024) encontraram ganhos com ela só em ações com volume fora do normal no dia.
- **VWAP (preço médio ponderado pelo volume):** compara o preço com o preço médio do dia, pesado pelo volume negociado, e aposta na volta do preço para essa média. Ela precisa de dados de volume, que faltam em alguns ativos (EUR/USD, e o SPY e o NQ do HistData).
- **IFR (índice de força relativa):** mede, numa escala de 0 a 100, se as altas recentes foram maiores que as quedas; compra quando o IFR está abaixo de 30 (sobrevendido) e vende quando está acima de 70 (sobrecomprado), com 14 períodos, como propôs Wilder (1978).
- **Cruzamento de médias móveis:** usa uma média rápida e outra lenta; compra quando a rápida cruza a lenta para cima e vende quando cruza para baixo. Brock, Lakonishok e LeBaron (1992) encontraram resultados a favor dessas regras no índice Dow Jones de 1897 a 1986.

As quatro estratégias também usam o passado para decidir se compram ou vendem, como o modelo de regressão. Por isso, elas serão testadas do mesmo jeito: treino de 12/07 a 09/09/2026 para escolher a melhor versão de cada uma, teste de 10/09 a 09/10/2026 para ver o resultado em dados novos, a mesma simulação com US$1.000 em cada ativo, os mesmos custos e a mesma comparação com comprar e segurar.

## 9. Limitações

- O teste tem só um mês, de 10/09 a 09/10/2026; outro mês poderia dar resultados diferentes.
- Foi usado só o *timeframe* de 1 hora e um único modelo, com três variações passadas.
- Os ativos em reais e o NQ foram simulados em porcentagem, sem câmbio e sem o tamanho real do contrato do NQ, que exige muito mais que US$1.000.
- Cada operação usa o capital inteiro; na prática, um *trader* arriscaria só uma parte (seção 3.8).
- Os custos são estimativas e mudam de corretora para corretora; o *slippage* foi estimado em um *tick* na entrada e outro na saída.
- O EUR/USD não tem os dados de sexta-feira, 25/09/2026, na fonte usada (HistData), então ficou com um dia a menos no teste.
