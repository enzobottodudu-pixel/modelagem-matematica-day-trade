import random

random.seed(2)

for lancamentos in [10, 100, 1000, 10000]:
    caras = 0
    for i in range(lancamentos):
        caras = caras + random.randint(0, 1)
    porcentagem = caras / lancamentos
    print(f"{lancamentos} lançamentos: {porcentagem:.1%} de caras")
