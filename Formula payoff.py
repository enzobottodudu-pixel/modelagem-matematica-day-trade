operacoes_lucrativas = 21
operacoes_perdedoras = 14

total_ganho = 840      # soma de todos os lucros (US$)
total_perdido = 280    # soma de todos os prejuízos (US$)

ganho_medio = total_ganho / operacoes_lucrativas      # 840 / 21 = US$ 40
perda_media = total_perdido / operacoes_perdedoras    # 280 / 14 = US$ 20
payoff = ganho_medio / perda_media                    # 40 / 20 = 2

print(f"Ganho médio: US$ {ganho_medio:.2f}")
print(f"Perda média: US$ {perda_media:.2f}")
print(f"Payoff: {payoff:.2f}")