# Custos de cada ativo (conferidos de novo e aprovados pelo Enzo em 18/10)

O custo é descontado **em toda operação, ida e volta** (compra + venda), em % do preço (seção 3.2).
Ele tem três partes: **corretagem**, **taxas** (bolsa e órgãos reguladores) e ***slippage***
(o preço pior do que o da tela, estimado aqui como 1 "tick", o menor passo de preço, na entrada e outro na saída).

| Ativo | Corretagem | Taxas | *Slippage* (ida + volta) | **Custo total por operação** |
|---|---|---|---|---|
| PETR4 | zero (comum nas corretoras para ações) | B3 *day trade*: 0,023% na compra + 0,023% na venda = 0,046% | 2 × R$0,01 sobre R$45,52 = 0,044% | **0,090%** |
| ITUB4 | zero | 0,046% | 2 × R$0,01 sobre R$42,17 = 0,047% | **0,093%** |
| MGLU3 | zero | 0,046% | 2 × R$0,01 sobre R$5,58 = 0,359% | **0,405%** |
| IBOV | (não é negociado direto; usa as taxas das ações e o *tick* de 5 pontos do mini-índice) | 0,046% | 2 × 5 pontos sobre 180.460 = 0,006% | **0,052%** |
| SPY | zero (comum nas corretoras americanas) | taxa da SEC: US$20,60 por milhão, só na venda = 0,002% | 2 × US$0,01 sobre ≈US$765 = 0,003% | **0,005%** |
| Tesla | zero | taxa da SEC = 0,002% | 2 × US$0,01 sobre US$354 = 0,006% | **0,008%** |
| NQ | US$1,29 por lado (NinjaTrader, plano grátis) | bolsa + NFA + compensação ≈US$1,58 por lado | 2 × 0,25 ponto | (2 × US$2,87 = 0,29 ponto) + 0,5 ponto ≈ 0,79 ponto sobre 29.510 = **0,003%** |
| EUR/USD | ≈US$7 por lote, ida e volta (= 0,7 *pip*) | *spread* ≈0,2 *pip* | 2 × 0,1 *pip* | ≈1,1 *pip* sobre 1,1488 = **0,010%** |
| BTC/USD | — | Binance: 0,1% na compra + 0,1% na venda = 0,2% | 2 × 0,01% | **0,220%** |

Preços médios do período, calculados com os próprios dados de `Dados 90 dias/`.

## O que isso mostra

- **MGLU3 e BTC/USD são os mais caros de operar:** a MGLU3 porque a ação custa pouco (R$0,01 já é muito em %),
  e o BTC porque a Binance cobra 0,1% em cada ordem. Uma estratégia nesses ativos precisa ganhar mais por operação só para empatar.
- **SPY, Tesla, NQ e EUR/USD são baratos:** o custo fica abaixo de 0,01% por operação.

## Fontes

- B3: tarifas de ações à vista, *day trade*, primeira faixa (até R$0,2 milhão por dia): negociação 0,005% + CCP 0,018% = 0,023% por lado.
  <https://www.b3.com.br/pt_br/produtos-e-servicos/tarifas/listados-a-vista-e-derivativos/renda-variavel/tarifas-de-acoes-e-fundos-de-investimento/a-vista/>
- Binance: taxa *spot* de 0,1% (*maker* e *taker*) para usuário comum (VIP 0), conferida na página oficial em 18/10. <https://www.binance.com/en/fee/trading>
- SEC: taxa da Seção 31 de US$20,60 por milhão de dólares vendidos, desde 04/04/2026 (todo o período dos dados). <https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-2>
- Corretagem zero em ações na B3: Clear (grupo XP), por exemplo.
- NQ: *tick* de 0,25 ponto = US$5 (1 ponto = US$20); taxas de bolsa US$1,38, NFA US$0,01 e compensação US$0,19 por lado; corretagem de US$1,29 por lado no plano grátis da NinjaTrader. <https://ninjatrader.com/pricing/>
- EUR/USD: *spread* médio de contas ECN ≈0,2 *pip* e comissão de US$4,50 a US$7 por lote, ida e volta (sites comparadores de corretoras).

Os valores são estimativas: mudam de corretora para corretora e de um dia para outro (seção 5.6).
