# Modelo de previsão: treino nos 2 primeiros meses, teste no último mês

Candles de 1 h. Treino: 12/07 a 09/09/2026. Teste: 10/09 a 09/10/2026. Regressão linear com as 3 últimas variações. Gerado por `previsao.py`.

| Ativo | Horas no treino | Horas no teste | Erro médio do modelo | Erro de repetir o último preço | Acerto da direção | a, b1, b2, b3 |
|---|---|---|---|---|---|---|
| EUR/USD | 1029 | 506 | 0,050% | 0,049% | 49,4% | 0,0019, -0,032, 0,069, 0,010 |
| SPY | 291 | 153 | 0,168% | 0,165% | 46,7% | 0,0047, -0,081, -0,003, 0,042 |
| NQ | 953 | 505 | 0,134% | 0,132% | 48,7% | -0,0010, -0,056, -0,081, -0,004 |
| IBOV | 289 | 153 | 0,345% | 0,347% | 55,6% | 0,0205, -0,013, -0,051, -0,039 |
| PETR4 | 289 | 153 | 0,550% | 0,541% | 50,0% | 0,0705, -0,057, -0,070, 0,039 |
| ITUB4 | 289 | 153 | 0,526% | 0,514% | 49,7% | -0,0179, -0,052, -0,003, -0,085 |
| BTC/USD | 1437 | 719 | 0,237% | 0,236% | 50,1% | 0,0147, 0,012, 0,002, -0,037 |
| Tesla | 291 | 153 | 0,484% | 0,479% | 53,9% | -0,0151, 0,041, -0,014, 0,029 |
| MGLU3 | 289 | 153 | 1,358% | 1,336% | 42,9% | 0,0415, 0,116, -0,022, -0,062 |

O valor de a está em %. Acerto da direção: % das horas em que o modelo acertou se o preço subia ou caía (sem contar as horas em que o preço ficou parado).
