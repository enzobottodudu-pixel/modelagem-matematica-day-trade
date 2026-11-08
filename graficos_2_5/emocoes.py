"""
GRÁFICOS DA SEÇÃO 2.5 — como o trader sente ganhos e perdas

Os dois gráficos são refeitos a partir de números publicados em estudos científicos
(não são dados inventados):

1. Teoria do Prospecto — TVERSKY, A.; KAHNEMAN, D. (1992).
   Função de valor: v(x) = x^0,88 para ganhos e v(x) = -2,25 · (-x)^0,88 para perdas.
   O 2,25 é a "aversão à perda": perder dói cerca de 2,25 vezes mais do que ganhar.

2. Efeito disposição — ODEAN, T. (1998), Tabela I.
   10.000 contas de uma corretora americana, 1987 a 1993:
   13.883 ganhos realizados e 79.658 ganhos não realizados  -> PGR = 14,8%
   11.930 perdas realizadas e 110.348 perdas não realizadas -> PLR =  9,8%

Gera 2 imagens nesta pasta:
  emocao1_teoria_do_prospecto.png
  emocao2_efeito_disposicao.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PASTA = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. TEORIA DO PROSPECTO: quanto um ganho ou uma perda "pesa" para a pessoa
# ---------------------------------------------------------------------------
ALFA = 0.88       # sensibilidade (o mesmo valor para ganhos e perdas)
LAMBDA = 2.25     # aversão à perda


def valor_sentido(x):
    """Quanto a pessoa 'sente' um ganho ou uma perda de x dólares."""
    return np.where(x >= 0, np.abs(x) ** ALFA, -LAMBDA * np.abs(x) ** ALFA)


x = np.linspace(-100, 100, 401)
y = valor_sentido(x)
ganho_100 = float(valor_sentido(np.array(100.0)))
perda_100 = float(valor_sentido(np.array(-100.0)))

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(x, y, color="black", linewidth=2.5)
ax.axhline(0, color="gray", linewidth=0.8)
ax.axvline(0, color="gray", linewidth=0.8)

# destacar o ganho e a perda de US$ 100
ax.plot([100, 100], [0, ganho_100], color="green", linestyle="--")
ax.plot([-100, -100], [0, perda_100], color="red", linestyle="--")
ax.scatter([100, -100], [ganho_100, perda_100], color=["green", "red"], s=80, zorder=5)
ax.annotate(f"Ganhar US$ 100\n\"vale\" +{ganho_100:.0f}".replace(".", ","),
            (100, ganho_100), xytext=(15, 45), color="green", fontsize=11,
            arrowprops={"arrowstyle": "->", "color": "green"})
ax.annotate(f"Perder US$ 100\n\"dói\" {perda_100:.0f}".replace(".", ","),
            (-100, perda_100), xytext=(-95, -60), color="red", fontsize=11,
            arrowprops={"arrowstyle": "->", "color": "red"})

ax.set_title("Teoria do Prospecto: perder dói cerca de 2,25 vezes mais do que ganhar")
ax.set_xlabel("Resultado da operação (US$)")
ax.set_ylabel("Valor sentido pela pessoa (unidades de satisfação)")
ax.set_xlim(-110, 110)
ax.set_ylim(-140, 75)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(PASTA / "emocao1_teoria_do_prospecto.png", dpi=200, bbox_inches="tight",
            facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------------------
# 2. EFEITO DISPOSIÇÃO: vender rápido o que está no lucro, segurar o que está no prejuízo
# ---------------------------------------------------------------------------
ganhos_realizados, ganhos_nao_realizados = 13_883, 79_658
perdas_realizadas, perdas_nao_realizadas = 11_930, 110_348

pgr = ganhos_realizados / (ganhos_realizados + ganhos_nao_realizados)
plr = perdas_realizadas / (perdas_realizadas + perdas_nao_realizadas)

fig, ax = plt.subplots(figsize=(8, 5.5))
barras = ax.bar(["Ações no LUCRO\nque foram vendidas", "Ações no PREJUÍZO\nque foram vendidas"],
                [pgr * 100, plr * 100], color=["green", "red"], width=0.55)
for barra, valor in zip(barras, [pgr, plr]):
    ax.text(barra.get_x() + barra.get_width() / 2, valor * 100 + 0.4,
            f"{valor * 100:.1f}%".replace(".", ","), ha="center", fontsize=14,
            fontweight="bold")
ax.set_title(f"Efeito disposição: o investidor vende o lucro {pgr / plr:.1f} vezes mais "
             "do que o prejuízo".replace(".", ","))
ax.set_ylabel("% das oportunidades de venda que viraram venda")
ax.set_ylim(0, 18)
ax.grid(alpha=0.3, axis="y")
fig.tight_layout()
fig.savefig(PASTA / "emocao2_efeito_disposicao.png", dpi=200, bbox_inches="tight",
            facecolor="white")
plt.close(fig)

print(f"Teoria do Prospecto: ganhar 100 = {ganho_100:.1f}; perder 100 = {perda_100:.1f}")
print(f"Efeito disposição: PGR = {pgr:.3f}; PLR = {plr:.3f}; razão = {pgr / plr:.2f}")
