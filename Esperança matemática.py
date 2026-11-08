taxa_de_acerto = 0.4
taxa_de_erro = 1 - taxa_de_acerto
ganho_medio = 40
perda_media = 20

E = (taxa_de_acerto * ganho_medio) - (taxa_de_erro * perda_media)
print(f"Esperança matemática: {E:.2f}")