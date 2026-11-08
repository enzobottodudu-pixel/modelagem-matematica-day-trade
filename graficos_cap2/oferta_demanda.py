"""3.7.2 — Lei da oferta e da demanda (exemplo com números inventados), versão limpa.

Rodar: py -3.14 oferta_demanda.py   →   salva cap2_2_oferta_demanda.png nesta pasta.
Compradores: preço = 50 − 0,3 × quantidade.  Vendedores: preço = 20 + 0,3 × quantidade.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PASTA = Path(__file__).parent
AZUL, AZUL_CLARO, VERMELHO, VERDE, CINZA = "#2c7bb6", "#b5cfe6", "#d73027", "#1a9850", "#4d4d4d"
q = [0, 100]  # retas: bastam o começo e o fim


def compradores(x, extra=0):
    return 50 + extra - 0.3 * x


def vendedores(x):
    return 20 + 0.3 * x


def ponto(ax, x, y, cor, texto, deslocamento):
    ax.plot([x, x], [15, y], color=cor, linestyle=":", linewidth=1.3)
    ax.plot([0, x], [y, y], color=cor, linestyle=":", linewidth=1.3)
    ax.scatter([x], [y], s=150, color=cor, zorder=5, edgecolor="white", linewidth=2)
    ax.annotate(
        texto,
        (x, y),
        xytext=deslocamento,
        textcoords="offset points",
        fontsize=13,
        fontweight="bold",
        color=cor,
        ha="center",
    )


fig, (esq, dir_) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
for ax in (esq, dir_):
    ax.plot(q, [vendedores(x) for x in q], color=VERMELHO, linewidth=3)
    ax.text(
        100,
        vendedores(100) + 1.5,
        "vendedores\n(oferta)",
        color=VERMELHO,
        fontsize=12,
        fontweight="bold",
        ha="right",
        va="bottom",
    )
    ax.set_xlim(0, 100)
    ax.set_ylim(15, 65)
    ax.set_xlabel("Quantidade de ações negociadas", fontsize=12)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f} mil"))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"R${v:.0f}"))
    ax.tick_params(labelsize=11)
    ax.grid(alpha=0.25)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)

# 1) o encontro das duas linhas
esq.plot(q, [compradores(x) for x in q], color=AZUL, linewidth=3)
esq.text(
    100,
    compradores(100) - 1.5,
    "compradores\n(demanda)",
    color=AZUL,
    fontsize=12,
    fontweight="bold",
    ha="right",
    va="top",
)
ponto(esq, 50, 35, CINZA, "encontro:\n50 mil ações a R$35", (0, -62))
esq.set_ylabel("Preço da ação", fontsize=12)
esq.set_title("1) O preço fica onde as duas linhas se cruzam", fontsize=13, loc="left", fontweight="bold")

# 2) notícia boa: mais compradores, a linha azul sobe e o encontro muda
dir_.plot(q, [compradores(x) for x in q], color=AZUL_CLARO, linewidth=3)
dir_.plot(q, [compradores(x, 12) for x in q], color=AZUL, linewidth=3)
dir_.text(
    100,
    compradores(100, 12) + 1.5,
    "compradores depois\nda notícia boa",
    color=AZUL,
    fontsize=12,
    fontweight="bold",
    ha="right",
    va="bottom",
)
dir_.annotate(
    "",
    xy=(20, compradores(20, 12)),
    xytext=(20, compradores(20)),
    arrowprops={"arrowstyle": "->", "color": AZUL, "lw": 2},
)
dir_.scatter([50], [35], s=110, color=CINZA, zorder=5, alpha=0.6)
ponto(dir_, 70, 41, VERDE, "novo encontro:\n70 mil ações a R$41", (0, 38))
dir_.set_title("2) Chega uma notícia boa: o preço sobe", fontsize=13, loc="left", fontweight="bold")

fig.tight_layout()
fig.savefig(PASTA / "cap2_2_oferta_demanda.png", dpi=200, facecolor="white")
print("salvo cap2_2_oferta_demanda.png")
