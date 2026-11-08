perdas = [0.10, 0.20, 0.50]

for perda in perdas:
    ganho_necessario = perda / (1 - perda)
    print(f"Perdeu {perda:.0%}: precisa ganhar {ganho_necessario:.1%} para voltar")
