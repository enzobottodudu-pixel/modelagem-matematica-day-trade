desvio_padrao = 0.5
numero_de_lancamentos = 1000

margem_de_erro = 2 * desvio_padrao / (numero_de_lancamentos ** 0.5)
print(f"Margem de erro: {margem_de_erro:.1%}")