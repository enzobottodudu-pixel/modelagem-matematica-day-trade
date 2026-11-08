"""A corrida dos US$1.000: o capital de cada abordagem dia a dia no mês de teste, com custos.

Versão para o TCC (fundo branco) do GIF readme/corrida.gif.
Rodar: py -3.14 comparativo/corrida_capital.py
-> comparativo/imagens/corrida_capital.png (figura parada, resultado final)
-> comparativo/imagens/corrida_capital.gif (animada; o 1º quadro já é o resultado final, então no PDF ou
   impresso ela aparece completa)
-> comparativo/imagens/corrida_capital.mp4 (vídeo, para a apresentação)
Os números vêm de estrategias_2_9/operacoes.csv e previsao/capital_modelo.csv (função resultados()).
"""

import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FFMpegWriter, FuncAnimation

PASTA = Path(__file__).parent
sys.path.insert(0, str(PASTA.parent / "readme"))
from gerar_visuais import resultados

plt.rcParams["text.parse_math"] = False  # "US$" não vira fórmula
CORES = {"Buy and hold": "#9e9e9e", "IFR": "#e7298a", "ORB": "#2166ac", "Regressão": "#e66101",
         "VWAP": "#1b9e77", "Médias": "#7570b3"}
ROTULO = {"Buy and hold": "Buy and hold", "IFR": "IFR (30 min)", "ORB": "ORB (30 min)",
          "Regressão": "Regressão (1 h)", "VWAP": "VWAP (15 min)", "Médias": "Médias (5 min)"}
SUB = 4  # quadros por dia na animação


def pct(v):
    if abs(v) < 0.05:
        return "0,0%"  # evita "−0,0%"
    return f"{v:+.1f}%".replace(".", ",").replace("-", "−")


dias, diario, *_ = resultados()
eixo_x = pd.to_datetime([dias[0] - pd.Timedelta(days=1), *dias])  # 09/09 = ponto de partida, 0%
n = len(eixo_x)
t = np.linspace(0, n - 1, (n - 1) * SUB + 1)  # tempo em dias, com passos no meio do dia
x_t = eixo_x[0] + pd.to_timedelta(t, unit="D")
series = {k: np.interp(t, np.arange(n), [0.0, *diario[k]]) for k in CORES}


def desenhar(ax, q):
    """Desenha a corrida até o quadro q (q = len(t) é o mês inteiro)."""
    ax.clear()
    ax.axhline(0, color="#444444", linewidth=1)
    finais = []
    for k, cor in CORES.items():
        ys = series[k][:q]
        ax.plot(x_t[:q], ys, color=cor, linewidth=2.6 if k != "Buy and hold" else 2.4,
                linestyle="--" if k == "Buy and hold" else "-")
        ax.scatter([x_t[q - 1]], [ys[-1]], color=cor, s=36, zorder=5)
        finais.append((ys[-1], k))
    ultimo = 99.0
    for v, k in sorted(finais, reverse=True):  # nome e resultado no fim da linha, sem encostar um no outro
        y = min(v, ultimo - 2.1)
        ultimo = y
        ax.text(x_t[q - 1] + pd.Timedelta(days=0.8), y, f"{ROTULO[k]}  {pct(v)}", color=CORES[k],
                fontsize=11.5, fontweight="bold", va="center")
    ax.set_xlim(eixo_x[0] - pd.Timedelta(days=0.5), eixo_x[-1] + pd.Timedelta(days=9))
    ax.set_ylim(-13, 23)
    marcas = [eixo_x[i] for i in (1, 8, 15, 22, 30)]
    ax.set_xticks(marcas, [f"{d:%d/%m}" for d in marcas], fontsize=11)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%".replace("-", "−"))
    ax.tick_params(axis="y", labelsize=11)
    ax.set_ylabel("ganho ou perda sobre o capital inicial", fontsize=11)
    ax.grid(axis="y", color="#e0e0e0")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_title("Capital de cada abordagem dia a dia, com custos (US$1.000 em cada ativo; 10/09 a 09/10/2026)",
                 fontsize=13, fontweight="bold", loc="left")


# 1) figura parada
fig, ax = plt.subplots(figsize=(12, 6.2))
desenhar(ax, len(t))
fig.tight_layout()
fig.savefig(PASTA / "imagens" / "corrida_capital.png", dpi=200)

# 2) vídeo e GIF: começa e termina no resultado final
quadros = [len(t)] * 15 + list(range(2, len(t) + 1)) + [len(t)] * 45
mp4 = PASTA / "imagens" / "corrida_capital.mp4"
escritor = FFMpegWriter(fps=15, codec="libx264", extra_args=["-pix_fmt", "yuv420p", "-crf", "20"])
plt.rcParams["animation.ffmpeg_path"] = shutil.which("ffmpeg")
FuncAnimation(fig, lambda q: desenhar(ax, q), frames=quadros).save(mp4, writer=escritor, dpi=120)
plt.close(fig)
gif = PASTA / "imagens" / "corrida_capital.gif"
filtro = ("fps=12,scale=1200:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64:stats_mode=diff[p];"
          "[b][p]paletteuse=dither=none")
subprocess.run([shutil.which("ffmpeg"), "-y", "-loglevel", "error", "-i", str(mp4), "-vf", filtro, str(gif)],
               check=True)
print({k: round(v[-1], 1) for k, v in diario.items()},
      f"gif {gif.stat().st_size / 1e6:.1f} MB, mp4 {mp4.stat().st_size / 1e6:.1f} MB")
