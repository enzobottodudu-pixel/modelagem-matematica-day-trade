import random

import matplotlib.pyplot as plt

random.seed(2)

quantidades = [10, 100, 1000, 10000]
resultados = []
for lancamentos in quantidades:
    caras = 0
    for i in range(lancamentos):
        caras = caras + random.randint(0, 1)
    resultados.append(caras / lancamentos * 100)

nomes = ["10", "100", "1.000", "10.000"]
fig, ax = plt.subplots(figsize=(8, 4.5))
barras = ax.bar(nomes, resultados, color="#4C72B0", width=0.6)
ax.axhline(50, color="black", linestyle="--", label="Probabilidade real: 50%")
for barra, valor in zip(barras, resultados):
    texto = f"{valor:.1f}%".replace(".", ",")
    ax.text(barra.get_x() + barra.get_width() / 2, valor + 1.5, texto, ha="center")
ax.set_ylim(0, 70)
ax.set_xlabel("Número de lançamentos da moeda")
ax.set_ylabel("Caras (%)")
ax.legend(loc="upper right")
fig.tight_layout()
fig.savefig("graficos_cap3/fig19_grafico_lei_grandes_numeros.png", dpi=200)
