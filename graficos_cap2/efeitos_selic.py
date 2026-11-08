"""3.7.1 — Esquema: o que acontece quando a Selic sobe e quando a Selic cai (texto do Enzo).

Rodar: py -3.14 efeitos_selic.py   →   salva cap2_7_efeitos_selic.png nesta pasta.
O título fica só na legenda do doc ("Figura 14 – ..."), para a letra da imagem poder ser maior.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

PASTA = Path(__file__).parent
VERMELHO, VERDE, CINZA = "#d73027", "#1a9850", "#4d4d4d"

LADOS = [
    (
        "SELIC SOBE ▲",
        "o Banco Central quer\ncombater a inflação",
        VERMELHO,
        "#fbe3e1",
        [
            ("−", "financiamentos e empréstimos\nficam mais caros"),
            ("−", "o consumo diminui"),
            ("−", "a bolsa tende a cair"),
            ("+", "a renda fixa rende mais: os\ninvestidores vão para ativos\nmais conservadores"),
            ("+", "entra capital estrangeiro\nno país"),
            ("+", "com o tempo, a inflação cai"),
        ],
    ),
    (
        "SELIC CAI ▼",
        "a inflação está controlada e o\nBanco Central quer estimular\na economia",
        VERDE,
        "#e1f3e5",
        [
            ("+", "o crédito fica mais barato"),
            ("+", "o consumo e a economia\ncrescem"),
            ("+", "a bolsa tende a subir"),
            ("+", "alivia as dívidas das\nempresas"),
            ("+", "o apetite por risco aumenta:\nos investidores saem da renda\nfixa e vão para a bolsa"),
            ("−", "sai capital estrangeiro do país,\ne a inflação pode voltar a subir"),
        ],
    ),
]

fig, ax = plt.subplots(figsize=(11, 9))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

for i, (titulo, motivo, cor, fundo, itens) in enumerate(LADOS):
    x = 1 + i * 50.5
    caixa = FancyBboxPatch(
        (x, 3), 47, 95, boxstyle="round,pad=0.4,rounding_size=2", facecolor=fundo, edgecolor=cor, linewidth=2.5
    )
    ax.add_patch(caixa)
    ax.text(x + 23.5, 93, titulo, ha="center", va="center", fontsize=24, fontweight="bold", color=cor)
    ax.text(x + 23.5, 84, motivo, ha="center", va="center", fontsize=14, style="italic", color=CINZA)
    for j, (sinal, texto) in enumerate(itens):
        y = 71 - j * 12.3
        cor_sinal = VERDE if sinal == "+" else VERMELHO
        ax.text(x + 4, y, sinal, ha="center", va="center", fontsize=26, fontweight="bold", color=cor_sinal)
        ax.text(x + 8, y, texto, ha="left", va="center", fontsize=15, color="black")

ax.text(
    50,
    -1.5,
    "+ efeito bom para a economia ou para o investidor      − efeito ruim",
    ha="center",
    fontsize=13,
    color=CINZA,
)
fig.tight_layout()
fig.savefig(PASTA / "cap2_7_efeitos_selic.png", dpi=200)
print("salvo cap2_7_efeitos_selic.png")
