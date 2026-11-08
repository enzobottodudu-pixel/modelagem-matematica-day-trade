"""
Gera uma imagem limpa de um código do Enzo com a saída que ele mostra ao rodar,
no estilo do VS Code, para colar no capítulo 3.

Uso:  python imagem_codigo_retorno.py "arquivo.py" nome_da_imagem.png
Sem argumentos, gera a imagem do "formula retorno.py" (seção 3.1).
"""

import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt

PASTA = Path(__file__).parent
ARQUIVO = PASTA.parent / (sys.argv[1] if len(sys.argv) > 1 else "formula retorno.py")
IMAGEM = sys.argv[2] if len(sys.argv) > 2 else "cap3_0_codigo_retorno.png"

codigo = ARQUIVO.read_text(encoding="utf-8").rstrip().splitlines()
saida = subprocess.run([sys.executable, str(ARQUIVO)], capture_output=True,
                       text=True, encoding="utf-8", check=True).stdout.strip()

FUNDO, TERMINAL, TEXTO, NUMERO = "#1e1e1e", "#181818", "#d4d4d4", "#858585"
LINHA = 0.3    # altura de cada linha, em polegadas

linhas_saida = saida.splitlines()
altura = LINHA * (len(codigo) + len(linhas_saida)) + 2.3
largura = 1.2 + 0.1 * max(len(x) for x in codigo + linhas_saida)
fig = plt.figure(figsize=(largura, altura), facecolor=FUNDO)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, largura)
ax.set_ylim(0, altura)
ax.axis("off")

y = altura - 0.45
ax.text(0.25, y, ARQUIVO.name, color="#cccccc", fontsize=10, family="sans-serif", va="center")
y -= 0.55
for n, linha in enumerate(codigo, start=1):
    ax.text(0.25, y, str(n), color=NUMERO, fontsize=11, family="monospace", va="center")
    ax.text(0.75, y, linha, color=TEXTO, fontsize=11, family="monospace", va="center")
    y -= LINHA

# área do terminal com a saída do programa
topo_terminal = y - 0.1
ax.add_patch(plt.Rectangle((0, 0), largura, topo_terminal, color=TERMINAL))
ax.text(0.25, topo_terminal - 0.3, "TERMINAL (saída do programa)", color=NUMERO,
        fontsize=9, family="sans-serif", va="center")
for k, texto in enumerate(linhas_saida):
    ax.text(0.25, topo_terminal - 0.75 - k * LINHA, texto, color="#4ec9b0", fontsize=11,
            family="monospace", va="center")

fig.savefig(PASTA / IMAGEM, dpi=200, facecolor=FUNDO)
print("saída do programa:", saida)
