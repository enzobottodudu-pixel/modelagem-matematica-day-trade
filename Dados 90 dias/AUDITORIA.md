# Auditoria dos dados (90 dias)

## 1. Inventário de timeframes

| Ativo | Fonte do arquivo | Timeframes | Faltando |
|---|---|---|---|
| BTCUSD | padrao | 13 | - |
| EURUSD | padrao | 13 | - |
| IBOV | padrao | 13 | - |
| IBOV | yahoo | 6 | 1h, 2h, 4h, 6h, 8h, 12h, 24h |
| ITUB4 | padrao | 13 | - |
| ITUB4 | yahoo | 6 | 1h, 2h, 4h, 6h, 8h, 12h, 24h |
| MGLU3 | padrao | 13 | - |
| MGLU3 | yahoo | 6 | 1h, 2h, 4h, 6h, 8h, 12h, 24h |
| NQ | histdata | 13 | - |
| NQ | padrao | 7 | 1min, 2min, 3min, 5min, 15min, 30min |
| PETR4 | padrao | 13 | - |
| PETR4 | yahoo | 6 | 1h, 2h, 4h, 6h, 8h, 12h, 24h |
| SPY | histdata | 13 | - |
| SPY | padrao | 7 | 1min, 2min, 3min, 5min, 15min, 30min |
| TESLA | bybit | 13 | - |
| TESLA | padrao | 13 | - |

## 2. Coerência entre timeframes

Cada timeframe maior é refeito a partir do menor arquivo da mesma fonte e comparado.

| Ativo | Fonte | Base | Timeframes conferidos | Diferenças |
|---|---|---|---|---|
| BTCUSD | padrao | 1min | 12 | nenhuma |
| EURUSD | padrao | 1min | 12 | nenhuma |
| IBOV | padrao | 1min | 11 | 2min (erro 0.00e+00, 2073/13203 candles); 3min (erro 0.00e+00, 1659/8827 candles); 5min (erro 0.00e+00, 249/5279 candles); 15min (erro 0.00e+00, 84/1781 candles); 30min (erro 0.00e+00, 42/891 candles); 1h (erro 1.28e-03, 21/446 candles); 2h (erro 1.28e-03, 12/255 candles); 4h (erro 1.28e-03, 6/128 candles); 6h (erro 1.28e-03, 6/127 candles); 8h (erro 1.28e-03, 3/64 candles); 12h (erro 1.28e-03, 3/64 candles) |
| IBOV | yahoo | 1min | 5 | 2min (erro 0.00e+00, 1464/6280 candles); 3min (erro 0.00e+00, 1252/2792 candles); 5min (erro 0.00e+00, 84/3444 candles); 15min (erro 0.00e+00, 28/1148 candles); 30min (erro 0.00e+00, 14/574 candles) |
| ITUB4 | padrao | 1min | 3 | 2min (erro 0.00e+00, 1637/9463 candles); 3min (erro 0.00e+00, 4676/8740 candles); 5min (erro 0.00e+00, 81/5251 candles) |
| ITUB4 | yahoo | 1min | 3 | 2min (erro 0.00e+00, 1022/6157 candles); 3min (erro 0.00e+00, 1787/2743 candles); 5min (erro 0.00e+00, 81/3385 candles) |
| MGLU3 | padrao | 1min | 3 | 2min (erro 0.00e+00, 2833/13029 candles); 3min (erro 0.00e+00, 3390/8710 candles); 5min (erro 0.00e+00, 81/5234 candles) |
| MGLU3 | yahoo | 1min | 3 | 2min (erro 0.00e+00, 812/6127 candles); 3min (erro 0.00e+00, 1237/2737 candles); 5min (erro 0.00e+00, 81/3365 candles) |
| NQ | histdata | 1min | 12 | nenhuma |
| NQ | padrao | 1h | 0 | nenhuma |
| PETR4 | padrao | 1min | 2 | 2min (erro 0.00e+00, 1632/9403 candles); 3min (erro 0.00e+00, 4840/8750 candles) |
| PETR4 | yahoo | 1min | 2 | 2min (erro 0.00e+00, 408/6180 candles); 3min (erro 0.00e+00, 2204/2751 candles) |
| SPY | histdata | 1min | 12 | nenhuma |
| SPY | padrao | 1h | 5 | nenhuma |
| TESLA | bybit | 1min | 12 | nenhuma |
| TESLA | padrao | 1min | 11 | 2min (erro 0.00e+00, 3900/5850 candles); 5min (erro 0.00e+00, 1560/3198 candles); 15min (erro 0.00e+00, 520/1066 candles); 30min (erro 0.00e+00, 260/533 candles); 1h (erro 0.00e+00, 140/448 candles); 2h (erro 0.00e+00, 80/256 candles); 4h (erro 0.00e+00, 40/128 candles); 6h (erro 0.00e+00, 40/128 candles); 8h (erro 0.00e+00, 20/64 candles); 12h (erro 0.00e+00, 20/64 candles) |

## 3. Cobertura (primeiro e último candle)

| Arquivo | Primeiro | Último | Candles |
|---|---|---|---|
| BTCUSD_1min.csv | 12/07/2026 00:00 UTC | 09/10/2026 23:59 UTC | 129600 |
| BTCUSD_1h.csv | 12/07/2026 00:00 UTC | 09/10/2026 23:00 UTC | 2160 |
| BTCUSD_24h.csv | 12/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 90 |
| EURUSD_1min.csv | 12/07/2026 21:00 UTC | 09/10/2026 20:58 UTC | 91869 |
| EURUSD_1h.csv | 12/07/2026 21:00 UTC | 09/10/2026 20:00 UTC | 1539 |
| EURUSD_24h.csv | 12/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 77 |
| IBOV_1min.csv | 04/09/2026 18:29 UTC | 09/10/2026 19:54 UTC | 10000 |
| IBOV_1h.csv | 13/07/2026 13:00 UTC | 09/10/2026 19:00 UTC | 446 |
| IBOV_24h.csv | 13/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 64 |
| IBOV_1min_yahoo.csv | 14/09/2026 13:03 UTC | 09/10/2026 19:59 UTC | 8359 |
| ITUB4_1min.csv | 05/08/2026 14:32 UTC | 09/10/2026 19:54 UTC | 19168 |
| ITUB4_1h.csv | 13/07/2026 13:00 UTC | 09/10/2026 19:00 UTC | 446 |
| ITUB4_24h.csv | 13/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 64 |
| ITUB4_1min_yahoo.csv | 14/09/2026 13:10 UTC | 09/10/2026 19:54 UTC | 8181 |
| MGLU3_1min.csv | 05/08/2026 15:09 UTC | 09/10/2026 19:54 UTC | 18984 |
| MGLU3_1h.csv | 13/07/2026 13:00 UTC | 09/10/2026 19:00 UTC | 446 |
| MGLU3_24h.csv | 13/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 64 |
| MGLU3_1min_yahoo.csv | 14/09/2026 13:10 UTC | 09/10/2026 19:54 UTC | 8138 |
| NQ_1min_histdata.csv | 12/07/2026 22:00 UTC | 09/10/2026 20:13 UTC | 85347 |
| NQ_1h_histdata.csv | 12/07/2026 22:00 UTC | 09/10/2026 20:00 UTC | 1470 |
| NQ_24h_histdata.csv | 12/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 77 |
| NQ_1h.csv | 12/07/2026 22:00 UTC | 09/10/2026 20:00 UTC | 1464 |
| NQ_24h.csv | 13/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 64 |
| PETR4_1min.csv | 05/08/2026 19:03 UTC | 09/10/2026 19:54 UTC | 18927 |
| PETR4_1h.csv | 13/07/2026 13:00 UTC | 09/10/2026 19:00 UTC | 446 |
| PETR4_24h.csv | 13/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 64 |
| PETR4_1min_yahoo.csv | 14/09/2026 13:03 UTC | 09/10/2026 19:54 UTC | 8208 |
| SPY_1min_histdata.csv | 12/07/2026 22:00 UTC | 09/10/2026 20:13 UTC | 85130 |
| SPY_1h_histdata.csv | 12/07/2026 22:00 UTC | 09/10/2026 20:00 UTC | 1470 |
| SPY_24h_histdata.csv | 12/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 77 |
| SPY_1h.csv | 13/07/2026 13:30 UTC | 09/10/2026 19:30 UTC | 448 |
| SPY_24h.csv | 13/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 64 |
| TESLA_1min_bybit.csv | 12/07/2026 00:00 UTC | 09/10/2026 23:59 UTC | 129600 |
| TESLA_1h_bybit.csv | 12/07/2026 00:00 UTC | 09/10/2026 23:00 UTC | 2160 |
| TESLA_24h_bybit.csv | 12/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 90 |
| TESLA_1min.csv | 14/09/2026 13:30 UTC | 09/10/2026 19:59 UTC | 7799 |
| TESLA_1h.csv | 13/07/2026 13:30 UTC | 09/10/2026 19:30 UTC | 448 |
| TESLA_24h.csv | 13/07/2026 00:00 UTC | 09/10/2026 00:00 UTC | 64 |

## 4. Minutos faltando no horário de pregão (arquivos de 1 minuto)

| Arquivo | Dias de pregão | Minutos esperados | Minutos presentes | Cobertura |
|---|---|---|---|---|
| IBOV_1min.csv | 25 | 10000 | 9686 | 96.9% |
| IBOV_1min_yahoo.csv | 20 | 8000 | 8000 | 100.0% |
| ITUB4_1min.csv | 47 | 18800 | 18704 | 99.5% |
| ITUB4_1min_yahoo.csv | 20 | 8000 | 7995 | 99.9% |
| MGLU3_1min.csv | 47 | 18800 | 18601 | 98.9% |
| MGLU3_1min_yahoo.csv | 20 | 8000 | 7972 | 99.7% |
| NQ_1min_histdata.csv | 64 | 24960 | 24779 | 99.3% |
| PETR4_1min.csv | 47 | 18800 | 18437 | 98.1% |
| PETR4_1min_yahoo.csv | 20 | 8000 | 7995 | 99.9% |
| SPY_1min_histdata.csv | 64 | 24960 | 24760 | 99.2% |
| TESLA_1min_bybit.csv | 65 | 25350 | 25350 | 100.0% |
| TESLA_1min.csv | 20 | 7800 | 7799 | 100.0% |

## 5. Volume

| Arquivo de 1 minuto (ou o menor) | Candles com volume zero |
|---|---|
| BTCUSD_1min.csv | 0.0% |
| EURUSD_1min.csv | 100.0% |
| IBOV_1min.csv | 0.1% |
| IBOV_1min_yahoo.csv | 100.0% |
| ITUB4_1min.csv | 0.0% |
| ITUB4_1min_yahoo.csv | 0.2% |
| MGLU3_1min.csv | 0.0% |
| MGLU3_1min_yahoo.csv | 0.9% |
| NQ_1min_histdata.csv | 100.0% |
| NQ_1h.csv | 4.0% |
| PETR4_1min.csv | 0.0% |
| PETR4_1min_yahoo.csv | 0.2% |
| SPY_1min_histdata.csv | 100.0% |
| SPY_1h.csv | 0.4% |
| TESLA_1min_bybit.csv | 15.8% |
| TESLA_1min.csv | 0.0% |
