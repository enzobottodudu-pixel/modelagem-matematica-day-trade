# Resultados das quatro estratégias com capital inicial de US$1.000

*Texto de apoio escrito pelo Claude a pedido do Enzo (02/11/2026), para ele adaptar com as próprias palavras. Todos os números vêm de `estrategias_2_9/estrategias.py`, rodando com os dados reais da pasta `Dados 90 dias/`; as tabelas completas estão em `ESTRATEGIAS.md` e as regras em `REGRAS.md`.*

---

## 1. O que foi feito

As quatro estratégias descritas na seção 2.9 (ORB, VWAP, IFR e cruzamento de médias móveis) foram aplicadas aos nove ativos do trabalho, no mês de teste, de 10/09 a 09/10/2026. Cada estratégia começou com US$1.000 em cada ativo, e a simulação seguiu as mesmas regras usadas para o modelo de previsão: operações de *day trade*, fechadas sempre no último *candle* do dia; o capital inteiro em cada operação, sem alavancagem; e o desconto do custo de cada operação (corretagem, taxas e *slippage*). Os resultados foram comparados com o modelo de previsão e com a alternativa mais simples, a de comprar o ativo no começo do mês e vender no fim ("comprar e segurar").

As regras de cada estratégia foram exatamente as dos exemplos da seção 2.9 (Figuras 33 a 36), sem mudar nenhum número. Como nada foi escolhido olhando os dados, os dois meses de treino não foram usados para ajustar as estratégias; eles serviram só para calcular o IFR e as médias móveis desde antes do começo do teste, porque esses indicadores precisam dos *candles* anteriores. Assim, o mês de teste funciona como uma prova que as estratégias nunca viram.

## 2. Como cada estratégia foi aplicada

| Estratégia | *Timeframe* | Quando entra | Quando sai com lucro (alvo) | *Stop* |
|---|---|---|---|---|
| ORB | 30 minutos | o preço passa da máxima (compra) ou da mínima (venda) do primeiro *candle* do dia; uma operação por dia | três vezes o tamanho da faixa, a partir da entrada | o outro lado da faixa |
| VWAP | 15 minutos | o *candle* fecha 0,6% ou mais acima da VWAP (vende) ou abaixo dela (compra) | o preço voltar a tocar a VWAP | 0,6% contra a operação |
| IFR | 30 minutos | o IFR de 14 períodos fica em 30 ou menos (compra) ou em 70 ou mais (vende) | o IFR voltar a 50 | 1% contra a operação |
| Médias | 5 minutos | a MME de 9 períodos cruza a de 21 para cima (compra) ou para baixo (vende) | não tem alvo: sai no cruzamento contrário e já vira a mão | 1,5% contra a operação |

Quando o *stop* e o alvo eram atingidos no mesmo *candle*, foi considerado o *stop*, que é o caso pior; assim, o resultado não fica melhor do que seria na realidade. Para conferir o programa, os exemplos da seção 2.9 que caem no mês de teste foram procurados na simulação, e os resultados foram os mesmos: na ORB da PETR4 (Figura 33), a compra de 15/09/2026 entrou a R$49,30 e saiu no alvo de R$50,11 às 12h00, e a venda de 16/09/2026 entrou a R$49,67 e saiu no alvo de R$48,74 às 12h00; no cruzamento de médias da Tesla (Figura 36), a compra das 09h40, a virada de mão às 12h15 e o fechamento às 15h55 aconteceram nos mesmos horários.

A VWAP precisa do volume negociado em cada *candle*. Para a B3, o volume veio do Profit Pro; para o BTC/USD, da Binance; e para a Tesla, da Bybit. Para o SPY e o NQ, que não têm volume no HistData, foi usado o volume do Yahoo Finance, disponível no mês de teste. O EUR/USD ficou sem VWAP, porque o mercado de câmbio não tem um volume central: cada banco e corretora negocia separado. Por isso, o total da VWAP soma oito ativos (US$8.000), e não nove.

## 3. O resultado geral

| | ORB | VWAP | IFR | Médias | Modelo de previsão | Comprar e segurar |
|---|---|---|---|---|---|---|
| Operações no mês | 210 | 399 | 153 | 1.359 | 995 | 9 |
| Resultado com custos | −1,4% | −7,1% | −0,7% | −9,2% | −6,4% | +20,6% |
| Resultado sem custos | +0,9% | +0,9% | +1,3% | +2,6% | +1,2% | +20,6% |

Com os custos, as quatro estratégias terminaram o mês com prejuízo. A que menos perdeu foi o IFR (−0,7%), seguido da ORB (−1,4%); as que mais perderam foram a VWAP (−7,1%) e o cruzamento de médias (−9,2%). Nenhuma chegou perto de comprar e segurar, que ganhou 20,6% no mesmo mês sem fazer nenhuma operação. Sem os custos, todas teriam terminado com um ganho pequeno, entre +0,9% e +2,6%, muito menor que o de comprar e segurar.

A tabela abaixo mostra o resultado de cada ativo, com custos:

| Ativo | ORB | VWAP | IFR | Médias | Modelo | Comprar e segurar |
|---|---|---|---|---|---|---|
| EUR/USD | −0,7% | sem volume | −1,0% | −1,3% | −2,7% | −3,7% |
| SPY | −1,6% | +0,0% | +0,9% | +0,9% | −1,5% | +2,6% |
| NQ | +2,2% | +1,4% | +0,8% | +8,3% | +3,1% | +4,7% |
| IBOV | −5,2% | +2,0% | +0,7% | −3,5% | +6,5% | +12,8% |
| PETR4 | +4,2% | −0,3% | −0,5% | −9,1% | −5,8% | +14,6% |
| ITUB4 | −5,8% | −6,7% | −5,3% | −6,5% | −5,4% | +22,1% |
| BTC/USD | −2,8% | −18,5% | −6,7% | −65,7% | −25,4% | +5,7% |
| Tesla | −9,6% | +4,5% | +3,6% | −14,6% | +1,9% | +4,5% |
| MGLU3 | +6,9% | −39,0% | +1,6% | +8,8% | −28,4% | +122,2% |

Das 35 combinações de estratégia e ativo, 15 terminaram com lucro e 20 com prejuízo. Só em poucos casos uma estratégia foi melhor que comprar e segurar: o cruzamento de médias no NQ (+8,3% contra +4,7%); as três estratégias do EUR/USD, onde comprar e segurar perdeu 3,7% e elas perderam menos; e a VWAP na Tesla, que empatou com comprar e segurar (+4,5%).

## 4. O resultado de cada estratégia

### 4.1 ORB

A ORB fez 210 operações, cerca de uma por dia em cada ativo, e acertou 34,3% delas. Metade das operações (50,5%) terminou no *stop*, 34,3% foram fechadas no fim do dia e só 15,2% chegaram ao alvo de três faixas. Isso mostra que o rompimento da faixa de abertura muitas vezes falha: o preço passa da máxima ou da mínima, mas volta para dentro da faixa e atinge o *stop* no outro lado. Os melhores resultados foram na MGLU3 (+6,9%), na PETR4 (+4,2%) e no NQ (+2,2%); o pior foi na Tesla (−9,6%), com 28 operações e só 32,1% de acerto. Na Tesla, a ORB perdeu quase o mesmo sem custos (−9,4%), o que indica que lá a estratégia errou de fato, e não só por causa dos custos.

O exemplo da Figura 33 mostra como uma operação vencedora funciona com os custos: na compra de 15/09/2026, a PETR4 foi de R$49,30 a R$50,11, um ganho de (50,11 ÷ 49,30) − 1 = 1,64%; descontando o custo de 0,09%, o resultado foi de +1,56%.

### 4.2 VWAP

A VWAP fez 399 operações e acertou 43,6%. Metade delas (50,6%) terminou no *stop*, 33,6% voltaram à VWAP (o alvo) e 15,8% fecharam no fim do dia. Ela foi bem na Tesla (+4,5%, com 62,9% de acerto), no IBOV (+2,0%) e no NQ (+1,4%, com 72,2% de acerto), mas perdeu muito no BTC/USD (−18,5%) e na MGLU3 (−39,0%). No SPY, o preço quase nunca se afastou 0,6% da VWAP, porque o SPY é um ativo calmo (desvio-padrão diário de 0,69%): só três *candles* do mês passaram desse limite, e a estratégia fez uma única operação.

Um exemplo de operação que deu certo: em 10/09/2026, às 10h30, a Tesla fechou mais de 0,6% acima da VWAP, e a estratégia vendeu a US$368,72; às 11h00, o preço voltou para a VWAP, e a venda foi encerrada a US$365,60, um ganho de 0,85% (0,84% depois do custo). O problema aparece na MGLU3, analisada na parte 6.

### 4.3 IFR

O IFR foi a estratégia que operou menos (153 operações) e a que menos perdeu (−0,7%). O acerto foi de 49,7%, e as saídas ficaram divididas: 36,6% no fim do dia, 32,7% no *stop* e 30,7% no alvo (IFR de volta a 50). Os melhores resultados foram na Tesla (+3,6%), na MGLU3 (+1,6%) e no SPY (+0,9%, com 80% de acerto em 10 operações); os piores, no BTC/USD (−6,7%) e no ITUB4 (−5,3%, com só 27,3% de acerto).

O BTC/USD mostra uma operação boa e uma ruim no mesmo dia (horários em UTC). Em 11/09/2026, às 12h30, o IFR passou de 70 e a estratégia vendeu a US$78.033, mas o preço continuou subindo e bateu o *stop* de 1% a US$78.813: −1,0% de queda mais 0,22% de custo, ou −1,22%. Às 14h00, o IFR passou de 70 de novo e ela vendeu a US$79.048; dessa vez o preço caiu, o IFR voltou a 50 às 17h30, e a venda foi encerrada a US$77.534, um ganho de 1,92% (1,70% depois do custo).

### 4.4 Cruzamento de médias

O cruzamento de médias foi a estratégia que mais operou (1.359 operações) e a que mais perdeu (−9,2%). Como ela vira a mão a cada cruzamento, 84,3% das operações terminaram no cruzamento contrário, 15,0% no fim do dia e só 0,7% no *stop* de 1,5%. O acerto foi de apenas 25,7%, mas as operações que acertaram ganharam bem mais que as que erraram, porque a estratégia segue a tendência: perde pouco muitas vezes, quando o preço vai e volta, e ganha muito poucas vezes, quando o preço anda numa direção só. Ela teve o melhor resultado de todo o teste, no NQ (+8,3%), e também o pior, no BTC/USD (−65,7%).

No exemplo da Figura 36, a Tesla em 16/09/2026, a compra das 09h40 rendeu +0,56% e a venda depois da virada de mão, +0,84%, já com os custos. Os preços da simulação (US$359,67 na compra) são um pouco diferentes dos da figura (US$359,29) porque, nos *candles* de minutos, a Tesla da simulação vem da Bybit, e a figura usou o Yahoo Finance; a diferença é de 0,1%.

## 5. O peso dos custos

A tabela abaixo compara, em média por operação, quanto cada estratégia ganhou antes do custo e quanto pagou de custo:

| Estratégia | Ganho médio antes do custo | Custo médio | Resultado médio por operação |
|---|---|---|---|
| ORB | +0,040% | 0,094% | −0,054% |
| VWAP | +0,020% | 0,190% | −0,170% |
| IFR | +0,079% | 0,114% | −0,035% |
| Médias | +0,014% | 0,104% | −0,091% |

Nas quatro estratégias, o ganho médio antes do custo foi positivo, mas menor que o custo. É como uma loja que vende cada produto com lucro de R$0,04, mas paga R$0,09 de frete por venda: quanto mais ela vende, mais ela perde. Por isso, as estratégias que operaram mais perderam mais: o cruzamento de médias fez 1.359 operações e perdeu 9,2%, enquanto o IFR fez 153 e perdeu 0,7%.

O BTC/USD é o caso mais extremo. A Binance cobra 0,1% na compra e 0,1% na venda, e com o *slippage* cada operação custa 0,22%. O cruzamento de médias fez 435 operações no BTC/USD: mesmo sem custos ele já perderia 10,6%, e com os custos, 435 operações × 0,22% de custo levaram a conta de US$1.000 para US$342,74 (−65,7%). Na MGLU3, a ação custava pouco (cerca de R$5,50 no começo do teste), e um centavo de *slippage* na entrada e outro na saída já representam 0,02 ÷ 5,50 = 0,36%; somando as taxas da B3, cada operação custou cerca de 0,4%.

## 6. Seguir a tendência ou apostar na volta do preço

Como foi visto na seção 2.9, duas estratégias seguem a tendência (ORB e médias) e duas apostam na volta do preço (VWAP e IFR). O mês de teste foi de alta forte na B3: o IBOV subiu 12,8%, a PETR4 14,6%, o ITUB4 22,1% e a MGLU3 122,2%. Em um mês assim, a diferença entre os dois tipos de estratégia aparece com clareza na MGLU3: as que seguem a tendência ganharam (ORB +6,9% e médias +8,8%), e a VWAP, que aposta na volta, perdeu 39,0%.

O motivo fica claro olhando as operações. Em 10/09/2026, a MGLU3 subiu de cerca de R$5,50 para R$5,80. A cada vez que o preço se afastava 0,6% acima da VWAP, a estratégia vendia, apostando que ele ia voltar; mas o preço continuava subindo e batia o *stop*. Só nesse dia, entre 10h30 e 13h30, foram quatro vendas seguidas, todas no *stop*, cada uma com perda de cerca de 1% (0,6% do *stop* e 0,4% de custo). No mês inteiro, a VWAP fez 135 operações na MGLU3 e acertou só 29,6%. Isso combina com a seção 1.7.5: uma estratégia não funciona do mesmo jeito em todos os momentos do mercado, e as que apostam na volta do preço sofrem nos períodos de tendência forte.

## 7. Acerto e *payoff*

Uma taxa de acerto alta não garante lucro, e uma baixa não garante prejuízo; o que importa é a combinação entre o acerto e o *payoff*, como foi visto na seção 2.4. A taxa de acerto mínima para empatar é:

taxa de acerto mínima = 1 ÷ (1 + *payoff*)

Três exemplos do teste mostram isso:

- **VWAP no NQ:** o *payoff* foi de 0,59 (as perdas foram maiores que os ganhos). O acerto mínimo era de 1 ÷ (1 + 0,59) = 62,9%. Como a estratégia acertou 72,2%, acima do mínimo, ela ganhou: esperança de +0,076% por operação.
- **Cruzamento de médias no NQ:** o *payoff* foi de 2,37, e o acerto mínimo, de 1 ÷ (1 + 2,37) = 29,7%. A estratégia acertou só 39,3%, mas como isso está acima do mínimo, ela também ganhou: +0,038% por operação.
- **ORB na Tesla:** o *payoff* foi de 0,47, e o acerto mínimo, de 1 ÷ (1 + 0,47) = 68,0%. A estratégia acertou só 32,1%, muito abaixo do mínimo, e perdeu: −0,356% por operação.

## 8. Foi sorte ou vantagem?

Para saber se um resultado positivo mostra uma vantagem real ou foi sorte, foi usada a margem de erro da seção 2.6: a esperança de cada operação, com uma faixa de mais ou menos duas vezes o desvio-padrão dividido pela raiz do número de operações. Se a faixa inteira fica acima de zero, há sinal de vantagem; se ela passa pelo zero, o resultado pode ter sido sorte.

Das 35 combinações, só uma teve a faixa inteira acima de zero: o cruzamento de médias no NQ, com esperança de +0,038% por operação e faixa de 0,000% a 0,076%, exatamente no limite. A VWAP no SPY fez uma única operação, e com uma operação só não dá para calcular a margem de erro. Mesmo o caso do NQ precisa ser visto com cuidado: com 35 testes, é esperado que pelo menos um passe pelo critério só por acaso, que é o problema apontado por Bailey et al. (2014). Por outro lado, seis combinações tiveram a faixa inteira abaixo de zero, ou seja, perderam de forma consistente: a ORB na Tesla, a VWAP no BTC/USD e na MGLU3, o IFR no ITUB4 e o cruzamento de médias no BTC/USD e na Tesla.

## 9. *Drawdown*

O *drawdown* máximo mostra a maior queda da conta, do ponto mais alto até o mais baixo. Os piores casos foram o cruzamento de médias no BTC/USD (−65,7%) e a VWAP na MGLU3 (−39,0%). Como foi visto na seção 2.7, recuperar uma perda exige um ganho maior que ela: depois de perder 65,7%, a conta de US$342,74 precisaria ganhar (1.000 ÷ 342,74) − 1 = 191,8% só para voltar aos US$1.000; depois de perder 39,0%, a conta de US$610,47 precisaria ganhar (1.000 ÷ 610,47) − 1 = 63,8%. Nos ativos mais calmos, os *drawdowns* foram pequenos: no EUR/USD e no SPY, nenhuma estratégia passou de −2,6%.

## 10. Comparação com o modelo de previsão e com comprar e segurar

O modelo de previsão perdeu 6,4% no total, um resultado no meio das estratégias: melhor que a VWAP (−7,1%) e o cruzamento de médias (−9,2%), e pior que o IFR (−0,7%) e a ORB (−1,4%). Sem custos, as cinco abordagens ficaram muito parecidas, entre +0,9% e +2,6%, quase no zero. Já comprar e segurar ganhou 20,6%, porque o mês foi de alta na maioria dos ativos. Isso não quer dizer que comprar e segurar seja sempre melhor: no EUR/USD, que caiu no mês, comprar e segurar perdeu 3,7%, mais do que qualquer estratégia. O resultado de comprar e segurar depende da direção do mercado no período, enquanto as estratégias de *day trade* tentam ganhar com os movimentos dentro de cada dia.

## 11. O que esses resultados mostram

Com as regras dos exemplos da seção 2.9, nenhuma das quatro estratégias mostrou uma vantagem que sobreviva aos custos. Antes dos custos, elas ganharam um pouco, o que pode indicar uma vantagem pequena, mas esse ganho foi menor que o custo de operar. As estratégias que operam pouco (IFR e ORB) perderam pouco, e as que operam muito (VWAP e médias) perderam muito. O tipo de mercado também importou: no mês de alta forte da B3, as estratégias que seguem a tendência foram melhores que as que apostam na volta do preço.

Esses resultados têm limitações. Foi testado um único mês, e cada estratégia foi testada numa só versão, a dos exemplos da seção 2.9, sem escolher no treino os melhores números de *stop*, alvo, período ou *timeframe*. Os ativos em reais e o NQ foram simulados em porcentagem, como se os US$1.000 estivessem aplicados neles, e o EUR/USD ficou sem a VWAP e sem os dados de 25/09/2026. As próximas etapas, combinadas com o orientador, são testar várias versões de cada estratégia no treino (seção 2.9.5), escolher a melhor de cada uma e só então verificar se ela se mantém no teste.
