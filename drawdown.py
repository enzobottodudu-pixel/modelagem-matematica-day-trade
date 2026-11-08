import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# 1. Simulação dos dados: Tempo e Capital de uma Conta Subindo
x = [1, 2, 3, 4, 5, 6, 7]
# O capital começa em 22.000, sobe, sofre um drawdown nos pontos 4 e 5, e depois se recupera atingindo novas máximas
y = [22000, 23500, 24500, 23986, 23380, 25100, 25800]

# 2. Calcular o topo histórico acumulado (High-Water Mark)
# Isso garante que o cálculo da queda comece sempre a partir do maior topo alcançado até aquele momento
topo_acumulado = []
maior_valor = y[0]
for valor in y:
    maior_valor = max(maior_valor, valor)
    topo_acumulado.append(maior_valor)

# Drawdown de cada dia, em %: (valor atual - topo) / topo
drawdown = [(valor - topo) / topo * 100 for valor, topo in zip(y, topo_acumulado)]
pior_dia = drawdown.index(min(drawdown))
print(f"Drawdown máximo: {min(drawdown):.1f}% no dia {x[pior_dia]}")

# 3. Pontos intermediários entre os dias
# Entre um dia e outro o capital anda em linha reta. O topo só pode subir quando o capital
# passa do topo antigo, então ele é calculado em vários pontos entre os dias.
x_fino = np.linspace(x[0], x[-1], 1000)
y_fino = np.interp(x_fino, x, y)
topo_fino = np.maximum.accumulate(y_fino)

# 4. Criar a figura e desenhar as linhas
plt.figure(figsize=(10, 6))
plt.plot(x_fino, topo_fino, color="green", linestyle="--", alpha=0.7, label="Topo máximo alcançado")
plt.plot(x, y, color="blue", marker="o", linewidth=2, label="Capital da conta")

# 5. Colorir a área do drawdown de vermelho (só onde o capital está abaixo do topo)
plt.fill_between(x_fino, topo_fino, y_fino, where=y_fino < topo_fino, color="red", alpha=0.3,
                 label="Drawdown")

# Marca o pior ponto com o valor do drawdown máximo
texto = f"Drawdown máximo: {min(drawdown):.1f}%".replace(".", ",")
plt.annotate(texto, (x[pior_dia], y[pior_dia]), xytext=(x[pior_dia] - 1.2, y[pior_dia] - 600),
             arrowprops={"arrowstyle": "->"})

# 6. Rótulos (o título vai na legenda da figura, como pede a ABNT)
plt.xlabel("Tempo (dias)", fontsize=12)
plt.ylabel("Valor da conta (R$)", fontsize=12)
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", ".")))
plt.grid(True, linestyle=":", alpha=0.6)
plt.legend(loc="upper left", fontsize=10)

# 7. Salvar e mostrar o gráfico
plt.savefig("grafico_drawdown_tcc.png", dpi=300, bbox_inches="tight")
print("Sucesso: Imagem salva como 'grafico_drawdown_tcc.png'!")
plt.show()
