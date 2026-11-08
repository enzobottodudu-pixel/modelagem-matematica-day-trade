import random

import matplotlib.pyplot as plt

random.seed(2)

desvio_padrao = 0.5
quantidades = [10, 100, 1000, 10000]
resultados = []
for lancamentos in quantidades:
    caras = 0
    for i in range(lancamentos):
        caras = caras + random.randint(0, 1)
    resultados.append(caras / lancamentos * 100)

nomes = ["10", "100", "1.000", "10.000"]
margens = [2 * desvio_padrao / (n ** 0.5) * 100 for n in quantidades]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.errorbar(nomes, [50] * 4, yerr=margens, fmt="none", ecolor="#4C72B0", elinewidth=10, alpha=0.35,
            label="Intervalo esperado: 50% ± margem de erro")
ax.plot(nomes, resultados, "o", color="#C44E52", markersize=9, label="Resultado da simulação (Figura 18)")
ax.axhline(50, color="black", linestyle="--", linewidth=1, label="Probabilidade real: 50%")
for x, m in zip(nomes, margens):
    ax.text(x, 50 + m + 2, f"± {m:.1f}%".replace(".", ","), ha="center")
ax.set_ylim(0, 100)
ax.set_xlabel("Número de lançamentos da moeda")
ax.set_ylabel("Caras (%)")
ax.legend(loc="lower right", fontsize=9)
fig.tight_layout()
fig.savefig("graficos_cap3/fig21_grafico_margem_de_erro.png", dpi=200)
