preco_de_entrada = 80
preco_de_saida = 100
quantidade = 10

retorno = (preco_de_saida - preco_de_entrada) / preco_de_entrada
print(f"Retorno sem custos: {retorno:.0%}")

# -------- CUSTOS -------- #
custo_de_transacao = 5
custo_de_taxas = 3
custo_total = custo_de_transacao + custo_de_taxas

valor_investido = preco_de_entrada * quantidade          # 80 x 10 = US$ 800
custo_em_porcentagem = custo_total / valor_investido     # 8 / 800 = 1%
retorno_liquido = retorno - custo_em_porcentagem         # 25% - 1% = 24%

print(f"Custo total: US$ {custo_total} ({custo_em_porcentagem:.0%} do valor investido)")
print(f"Retorno com custos: {retorno_liquido:.0%}")