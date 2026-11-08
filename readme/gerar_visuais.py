"""Gera as imagens, os GIFs e os vídeos do README do GitHub (pasta readme/).

Rodar: py -3.14 readme/gerar_visuais.py

Tudo vem de dados reais ou dos resultados do próprio trabalho:
- hero_escuro.svg / hero_claro.svg: capa animada com candles diários reais do IBOV (Yahoo Finance).
- numeros_escuro.svg / numeros_claro.svg: cartões animados com os números principais.
- corrida: o capital de cada abordagem dia a dia no mês de teste (operacoes.csv e capital_modelo.csv).
- custo: o resultado sem custos e com custos de cada abordagem.
- orb, vwap, ifr, medias: as 4 estratégias candle a candle nos dias reais das Figuras 33 a 36.
- heatmap: o resultado de cada abordagem em cada ativo, com custos (Figura 39).
- drawdown: o cruzamento de médias no BTC/USD, o pior caso do trabalho.
- lei_grandes_numeros: 1.000 lançamentos de moeda simulados.
Cada animação vira um .mp4 (pasta readme/videos) e um .gif (pasta readme), feito pelo ffmpeg.
"""

import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FFMpegWriter, FuncAnimation

PASTA = Path(__file__).parent
RAIZ = PASTA.parent
DADOS = RAIZ / "Dados 90 dias"
VIDEOS = PASTA / "videos"
VIDEOS.mkdir(exist_ok=True)
FFMPEG = shutil.which("ffmpeg")
plt.rcParams["animation.ffmpeg_path"] = FFMPEG

FUNDO, PAINEL, TEXTO, CINZA, GRADE = "#0d1117", "#161b22", "#e6edf3", "#8b949e", "#30363d"
VERDE, VERMELHO, AMARELO, AZUL, ROXO, LARANJA, ROSA, CIANO = (
    "#3fb950", "#f85149", "#d29922", "#58a6ff", "#bc8cff", "#ffa657", "#ff7b72", "#39d3c3")
CORES = {"ORB": AZUL, "VWAP": LARANJA, "IFR": ROXO, "Médias": ROSA, "Regressão": CIANO, "Buy and hold": "#c9d1d9"}
ATIVOS = ["EURUSD", "SPY", "NQ", "IBOV", "PETR4", "ITUB4", "BTCUSD", "TESLA", "MGLU3"]
NOME = {"EURUSD": "EUR/USD", "BTCUSD": "BTC/USD", "TESLA": "Tesla"}


def nome(a):
    return NOME.get(a, a)


def pct(v, casas=1):
    return f"{v:+.{casas}f}%".replace(".", ",").replace("-", "−")


def dinheiro(v, moeda="US", casas=2):
    txt = f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{moeda}\\${txt}"  # o \ impede o matplotlib de ler "$...$" como fórmula


def candles(ax, c, x0=0, largura=0.6, alpha=1.0, minimo=0.0):
    for i, k in enumerate(c.itertuples()):
        cor = VERDE if k.Close >= k.Open else VERMELHO
        ax.vlines(x0 + i, k.Low, k.High, color=cor, linewidth=1.2, alpha=alpha, zorder=3)
        ax.bar(x0 + i, max(abs(k.Close - k.Open), minimo), largura, bottom=min(k.Open, k.Close), color=cor,
               alpha=alpha, zorder=3)


def eixo_escuro(ax):
    ax.set_facecolor(FUNDO)
    ax.tick_params(colors=CINZA, labelsize=9)
    for lado in ax.spines:
        ax.spines[lado].set_visible(False)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)


def salvar(fig, desenhar, quadros, nome_arq, fps, largura_gif=760):
    """Salva a animação em MP4 (readme/videos) e converte para GIF com paleta otimizada (readme)."""
    mp4 = VIDEOS / f"{nome_arq}.mp4"
    quadros = [quadros[-1]] * 6 + list(quadros)  # 1º quadro = resultado final (o GitHub pode mostrar o GIF parado)
    escritor = FFMpegWriter(fps=fps, codec="libx264", extra_args=["-pix_fmt", "yuv420p", "-crf", "20"])
    FuncAnimation(fig, desenhar, frames=quadros).save(mp4, writer=escritor, dpi=120)
    plt.close(fig)
    gif = PASTA / f"{nome_arq}.gif"
    filtro = (f"fps={min(fps, 12)},scale={largura_gif}:-1:flags=lanczos,split[a][b];"
              "[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(mp4), "-vf", filtro, str(gif)], check=True)
    print(f"  {nome_arq}: gif {gif.stat().st_size / 1e6:.1f} MB, mp4 {mp4.stat().st_size / 1e6:.1f} MB")


# ---------------------------------------------------------------- resultados do trabalho
def resultados():
    """Capital diário (soma dos ativos) e final de cada abordagem em cada ativo."""
    ops = pd.read_csv(RAIZ / "estrategias_2_9" / "operacoes.csv")
    ops["dia"] = pd.to_datetime(ops["hora_saida"], utc=True).dt.tz_convert("America/Sao_Paulo").dt.date
    cap = pd.read_csv(RAIZ / "previsao" / "capital_modelo.csv")
    cap["dia"] = pd.to_datetime(cap["Data"], utc=True).dt.tz_convert("America/Sao_Paulo").dt.date
    dias = pd.date_range("2026-09-10", "2026-10-09").date
    ops["dia"] = ops["dia"].clip(lower=dias[0], upper=dias[-1])  # saídas na virada da noite contam no último dia
    cap["dia"] = cap["dia"].clip(lower=dias[0], upper=dias[-1])
    estrs = {"ORB": "ORB", "VWAP": "VWAP", "IFR": "IFR", "Médias": "Médias"}
    diario, final, final_sem, n_ops = {}, {}, {}, {}
    for chave, rotulo in estrs.items():
        o = ops[ops["estrategia"] == chave]
        ativos = sorted(o["ativo"].unique())
        total = np.zeros(len(dias))
        for a in ativos:
            oa = o[o["ativo"] == a]
            fator = (1 + oa["resultado"] / 100).groupby(oa["dia"]).prod()
            serie = pd.Series(1.0, index=dias)
            serie.loc[fator.index.intersection(dias)] = fator.loc[fator.index.intersection(dias)]
            total += 1000 * serie.cumprod().to_numpy()
            final[(rotulo, a)] = (1000 * (1 + oa["resultado"] / 100).prod() / 1000 - 1) * 100
            final_sem[(rotulo, a)] = ((1 + oa["sem_custo"] / 100).prod() - 1) * 100
        diario[rotulo] = (total / (1000 * len(ativos)) - 1) * 100
        n_ops[rotulo] = len(o)
    for coluna, rotulo in [("modelo", "Regressão"), ("segurar", "Buy and hold")]:
        total = np.zeros(len(dias))
        for a in ATIVOS:
            ca = cap[cap["ativo"] == a].groupby("dia")[coluna].last()
            serie = ca.reindex(dias).ffill().fillna(1000)
            total += serie.to_numpy()
            final[(rotulo, a)] = (ca.iloc[-1] / 1000 - 1) * 100
        diario[rotulo] = (total / 9000 - 1) * 100
    for a in ATIVOS:
        ca = cap[cap["ativo"] == a]
        final_sem[("Regressão", a)] = (ca["sem_custo"].iloc[-1] / 1000 - 1) * 100
    n_ops["Regressão"] = len(pd.read_csv(RAIZ / "previsao" / "operacoes_modelo.csv"))
    return dias, diario, final, final_sem, n_ops, ops


# ---------------------------------------------------------------- SVGs animados
def hero_svg(tema):
    escuro = tema == "escuro"
    fundo, borda = (FUNDO, GRADE) if escuro else ("#ffffff", "#d0d7de")
    texto, sub = (TEXTO, CINZA) if escuro else ("#1f2328", "#59636e")
    destaque = AZUL if escuro else "#0969da"
    verde, vermelho = (VERDE, VERMELHO) if escuro else ("#1a7f37", "#cf222e")
    ibov = pd.read_csv(DADOS / "IBOV" / "IBOV_24h.csv").tail(48).reset_index(drop=True)
    x0, x1, y0, y1 = 640, 1160, 40, 270
    lo, hi = ibov["Low"].min(), ibov["High"].max()
    passo = (x1 - x0) / len(ibov)

    def y(v):
        return y1 - (v - lo) / (hi - lo) * (y1 - y0)

    velas = []
    for i, k in ibov.iterrows():
        cor = verde if k["Close"] >= k["Open"] else vermelho
        cx = x0 + (i + 0.5) * passo
        topo, base = y(max(k["Open"], k["Close"])), y(min(k["Open"], k["Close"]))
        velas.append(
            f'<g class="v" style="animation-delay:{i * 0.12:.2f}s">'
            f'<line x1="{cx:.1f}" y1="{y(k["High"]):.1f}" x2="{cx:.1f}" y2="{y(k["Low"]):.1f}" '
            f'stroke="{cor}" stroke-width="1.6"/>'
            f'<rect x="{cx - passo * 0.32:.1f}" y="{topo:.1f}" width="{passo * 0.64:.1f}" '
            f'height="{max(base - topo, 1.2):.1f}" rx="1" fill="{cor}"/></g>')
    fita = ("IFR −0,7%   ·   ORB −1,4%   ·   Regressão −6,4%   ·   VWAP −7,1%   ·   Médias −9,2%   ·   "
            "Buy and hold +20,6%   ·   3.116 operações   ·   1 de 43 combinações no limite da vantagem   ·   ")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 360" width="1200" height="360" role="img">
<title>Modelagem Matemática de Estratégias de Day Trade</title>
<style>
text {{ font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; }}
.sobe {{ opacity: 0; animation: sobe .9s cubic-bezier(.2,.8,.2,1) forwards; }}
@keyframes sobe {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
.v {{ opacity: 0; animation: vela 9s ease-in-out infinite; }}
@keyframes vela {{ 0% {{ opacity: 0; transform: translateY(6px); }} 6% {{ opacity: 1; transform: none; }}
  80% {{ opacity: 1; }} 92%, 100% {{ opacity: 0; }} }}
.scan {{ animation: scan 9s linear infinite; }}
@keyframes scan {{ 0% {{ transform: translateX(0); opacity: .9; }} 62% {{ transform: translateX(520px); opacity: .9; }}
  70%, 100% {{ transform: translateX(520px); opacity: 0; }} }}
.fita {{ animation: fita 28s linear infinite; }}
@keyframes fita {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-1290px); }} }}
.pisca {{ animation: pisca 1.1s steps(1) infinite; }}
@keyframes pisca {{ 50% {{ opacity: 0; }} }}
</style>
<defs><clipPath id="corte"><rect x="1" y="1" width="1198" height="358" rx="18"/></clipPath>
<linearGradient id="brilho" x1="0" x2="1"><stop offset="0" stop-color="{destaque}" stop-opacity="0"/>
<stop offset="1" stop-color="{destaque}" stop-opacity=".35"/></linearGradient></defs>
<rect x="1" y="1" width="1198" height="358" rx="18" fill="{fundo}" stroke="{borda}" stroke-width="2"/>
<g clip-path="url(#corte)">
{''.join(velas)}
<g class="scan"><rect x="{x0 - 40}" y="{y0 - 10}" width="40" height="{y1 - y0 + 20}" fill="url(#brilho)"/>
<line x1="{x0}" y1="{y0 - 10}" x2="{x0}" y2="{y1 + 10}" stroke="{destaque}" stroke-width="2"/></g>
<text x="{x1}" y="{y1 + 26}" text-anchor="end" font-size="13" fill="{sub}">IBOV · candles diários reais · o backtest anda candle a candle, sem ver o futuro</text>
<text class="sobe" x="56" y="98" font-size="42" font-weight="700" fill="{texto}">Modelagem Matemática de</text>
<text class="sobe" style="animation-delay:.25s" x="56" y="150" font-size="42" font-weight="700" fill="{destaque}">Estratégias de Day Trade</text>
<text class="sobe" style="animation-delay:.5s" x="58" y="190" font-size="19" fill="{sub}">risco, gestão de capital e a influência da economia</text>
<text class="sobe" style="animation-delay:.75s" x="58" y="240" font-size="16" fill="{texto}">TCC · Lumiar Vila Olímpia · 9º ano · 2026</text>
<text class="sobe" style="animation-delay:1s" x="58" y="268" font-size="16" fill="{sub}">4 estratégias · regressão linear · 9 ativos · dados reais<tspan class="pisca" fill="{destaque}"> ▍</tspan></text>
<rect x="0" y="306" width="1200" height="54" fill="{destaque}" fill-opacity=".08"/>
<g class="fita"><text x="20" y="340" font-size="17" font-weight="600" fill="{texto}" textLength="1290" lengthAdjust="spacing">{fita}</text><text x="1310" y="340" font-size="17" font-weight="600" fill="{texto}" textLength="1290" lengthAdjust="spacing">{fita}</text></g>
</g></svg>"""


def numeros_svg(tema):
    escuro = tema == "escuro"
    fundo, borda = (PAINEL, GRADE) if escuro else ("#f6f8fa", "#d0d7de")
    sub = CINZA if escuro else "#59636e"
    cards = [("9", "ativos, do EUR/USD à MGLU3", AZUL if escuro else "#0969da"),
             ("3.116", "operações no mês de teste", ROXO if escuro else "#8250df"),
             ("−0,7%", "a melhor (IFR), com custos", VERMELHO if escuro else "#cf222e"),
             ("+20,6%", "buy and hold, no mesmo mês", VERDE if escuro else "#1a7f37")]
    partes = []
    for i, (num, rot, cor) in enumerate(cards):
        x = 8 + i * 298
        partes.append(
            f'<g class="card" style="animation-delay:{0.15 + i * 0.18:.2f}s">'
            f'<rect x="{x}" y="8" width="282" height="150" rx="14" fill="{fundo}" stroke="{borda}" stroke-width="1.5"/>'
            f'<rect class="barra" style="animation-delay:{0.6 + i * 0.18:.2f}s" x="{x + 22}" y="132" width="238" '
            f'height="4" rx="2" fill="{cor}"/>'
            f'<text x="{x + 22}" y="78" font-size="46" font-weight="700" fill="{cor}">{num}</text>'
            f'<text x="{x + 22}" y="112" font-size="16" fill="{sub}">{rot}</text></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 166" width="1200" height="166" role="img">
<title>Os números do trabalho</title>
<style>
text {{ font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; }}
.card {{ opacity: 0; animation: entra .8s cubic-bezier(.2,.8,.2,1) forwards; }}
@keyframes entra {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: none; }} }}
.barra {{ transform-box: fill-box; transform-origin: left; transform: scaleX(0);
  animation: cresce 1.2s cubic-bezier(.2,.8,.2,1) forwards, respira 3s ease-in-out 2s infinite; }}
@keyframes cresce {{ to {{ transform: scaleX(1); }} }}
@keyframes respira {{ 0%, 100% {{ opacity: 1; transform: scaleX(1); }} 50% {{ opacity: .45; transform: scaleX(1); }} }}
</style>
{''.join(partes)}
</svg>"""


# ---------------------------------------------------------------- animações
def corrida(dias, diario):
    ordem = ["Buy and hold", "IFR", "ORB", "Regressão", "VWAP", "Médias"]
    sub = 4
    dias = [dias[0] - pd.Timedelta(days=1), *dias]  # ponto de partida: 0% antes do 1º dia
    n = len(dias)
    xs = np.linspace(0, n - 1, (n - 1) * sub + 1)
    series = {k: np.interp(xs, np.arange(n), np.r_[0.0, diario[k]]) for k in ordem}
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=FUNDO)
    quadros = list(range(1, len(xs) + 1)) + [len(xs)] * 24

    def desenhar(q):
        ax.clear()
        eixo_escuro(ax)
        ax.set_xlim(0, n + 6.5)
        ax.set_ylim(-12, 24)
        ax.axhline(0, color=CINZA, linewidth=1)
        marcas = [1, 8, 15, 22, 30]
        ax.set_xticks(marcas, [f"{dias[i]:%d/%m}" for i in marcas])
        ax.yaxis.set_major_formatter(lambda v, _: pct(v, 0))
        for k in ordem:
            ys = series[k][:q]
            estilo = "--" if k == "Buy and hold" else "-"
            ax.plot(xs[:q], ys, color=CORES[k], linewidth=2.6 if k == "Buy and hold" else 2.2, linestyle=estilo)
            ax.scatter([xs[q - 1]], [ys[-1]], color=CORES[k], s=28, zorder=5)
        finais = sorted(((series[k][q - 1], k) for k in ordem), reverse=True)
        ultimo = 99.0
        for v, k in finais:  # rótulos sem encostar um no outro
            yv = min(v, ultimo - 2.3)
            ultimo = yv
            ax.text(xs[q - 1] + 0.6, yv, f"{k} {pct(v)}", color=CORES[k], fontsize=9.5, fontweight="bold",
                    va="center")
        dia = dias[min(int(xs[q - 1] + 1e-9), n - 1)]
        ax.set_title("A corrida dos US\\$1.000: quanto cada abordagem ganhou ou perdeu, com custos",
                     color=TEXTO, fontsize=12, fontweight="bold", loc="left")
        ax.text(0.01, 0.96, f"mês de teste · {dia:%d/%m/%Y} · soma dos 9 ativos (VWAP: 8)", color=CINZA,
                fontsize=9.5, transform=ax.transAxes, va="top")

    fig.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.08)
    salvar(fig, desenhar, quadros, "corrida", fps=15)


def custo(final, final_sem, n_ops):
    nomes = ["IFR", "ORB", "Regressão", "VWAP", "Médias"]
    ativos_de = {k: [a for a in ATIVOS if (k, a) in final] for k in nomes}
    com = [np.mean([final[(k, a)] for a in ativos_de[k]]) for k in nomes]
    sem = [np.mean([final_sem[(k, a)] for a in ativos_de[k]]) for k in nomes]
    fig, ax = plt.subplots(figsize=(9, 5), facecolor=FUNDO)
    passos = 22
    quadros = ([("sobe", t / passos) for t in range(passos + 1)] + [("sobe", 1.0)] * 14 +
               [("desce", t / passos) for t in range(passos + 1)] + [("desce", 1.0)] * 30)

    def desenhar(q):
        fase, t = q
        t = 1 - (1 - t) ** 3  # desacelera no fim
        ax.clear()
        eixo_escuro(ax)
        ax.set_ylim(-11.5, 5.5)
        ax.axhline(0, color=CINZA, linewidth=1)
        ax.set_xticks(range(len(nomes)), [f"{k}\n{n_ops[k]:,} ops".replace(",", ".") for k in nomes],
                      color=TEXTO, fontsize=10)
        ax.yaxis.set_major_formatter(lambda v, _: pct(v, 0))
        for i, k in enumerate(nomes):
            v = sem[i] * t if fase == "sobe" else sem[i] + (com[i] - sem[i]) * t
            cor = VERDE if v >= 0 else VERMELHO
            ax.bar(i, v, 0.55, color=cor, zorder=3)
            if fase == "desce":
                ax.bar(i, sem[i], 0.55, color="none", edgecolor=VERDE, linestyle="--", linewidth=1.3, zorder=4)
            ax.text(i, v + (0.35 if v >= 0 else -0.35), pct(v), ha="center", va="bottom" if v >= 0 else "top",
                    color=TEXTO, fontsize=11, fontweight="bold", zorder=5)
        if fase == "sobe":
            titulo, cor = "1) Antes dos custos: todas ganham um pouquinho", VERDE
        else:
            titulo, cor = "2) Depois dos custos de cada operação: todas perdem", VERMELHO
        ax.set_title(titulo, color=cor, fontsize=13, fontweight="bold", loc="left")
        ax.text(0.99, 0.04, "média dos ativos · quanto mais operações, mais custo", transform=ax.transAxes,
                ha="right", color=CINZA, fontsize=9)

    fig.subplots_adjust(left=0.09, right=0.98, top=0.9, bottom=0.14)
    salvar(fig, desenhar, quadros, "custo", fps=15)


def heatmap(final):
    colunas = ["ORB", "VWAP", "IFR", "Médias", "Regressão", "Buy and hold"]
    m = np.full((len(ATIVOS), len(colunas)), np.nan)
    for j, k in enumerate(colunas):
        for i, a in enumerate(ATIVOS):
            if (k, a) in final:
                m[i, j] = final[(k, a)]
    fig, ax = plt.subplots(figsize=(9, 6), facecolor=FUNDO)
    ordem = [(i, j) for j in range(len(colunas)) for i in range(len(ATIVOS))]
    quadros = list(range(0, len(ordem) + 1, 2)) + [len(ordem)] * 30
    cmap = plt.get_cmap("RdYlGn")

    def desenhar(q):
        ax.clear()
        ax.set_facecolor(FUNDO)
        ax.set_xlim(-0.5, len(colunas) - 0.5)
        ax.set_ylim(len(ATIVOS) - 0.5, -0.5)
        ax.set_xticks(range(len(colunas)), [c.replace("Buy and hold", "Buy and\nhold") for c in colunas],
                      color=TEXTO, fontsize=10)
        ax.set_yticks(range(len(ATIVOS)), [nome(a) for a in ATIVOS], color=TEXTO, fontsize=10)
        ax.tick_params(length=0)
        for lado in ax.spines:
            ax.spines[lado].set_visible(False)
        ax.xaxis.tick_top()
        for i, j in ordem:
            ax.add_patch(plt.Rectangle((j - 0.47, i - 0.45), 0.94, 0.9, color=PAINEL, zorder=1))
        for i, j in ordem[:q]:
            v = m[i, j]
            if np.isnan(v):
                ax.text(j, i, "sem\nvolume", ha="center", va="center", color=CINZA, fontsize=8, zorder=3)
                continue
            cor = cmap(0.5 + np.clip(v, -20, 20) / 40)
            ax.add_patch(plt.Rectangle((j - 0.47, i - 0.45), 0.94, 0.9, color=cor, zorder=2))
            ax.text(j, i, pct(v), ha="center", va="center", fontsize=10, fontweight="bold", zorder=3,
                    color="#0d1117" if abs(v) < 12 else "white")
        ax.set_title("Cada abordagem em cada ativo, com custos (US\\$1.000 → ?)", color=TEXTO, fontsize=12,
                     fontweight="bold", loc="left", pad=34)

    fig.subplots_adjust(left=0.12, right=0.98, top=0.86, bottom=0.03)
    salvar(fig, desenhar, quadros, "heatmap", fps=15)


def drawdown(ops):
    o = ops[(ops["estrategia"] == "Médias") & (ops["ativo"] == "BTCUSD")].copy()
    o = o.sort_values("hora_saida")
    capital = 1000 * np.r_[1, np.cumprod(1 + o["resultado"].to_numpy() / 100)]
    pico = np.maximum.accumulate(capital)
    n = len(capital)
    fig, ax = plt.subplots(figsize=(9, 5), facecolor=FUNDO)
    quadros = list(range(2, n + 1, 6)) + [n] * 30
    fundo_i = int(np.argmin(capital / pico))
    queda = capital[fundo_i] / pico[fundo_i] - 1

    def desenhar(q):
        ax.clear()
        eixo_escuro(ax)
        ax.set_xlim(0, n * 1.02)
        ax.set_ylim(250, 1150)
        ax.yaxis.set_major_formatter(lambda v, _: dinheiro(v, casas=0))
        x = np.arange(q)
        ax.plot(x, pico[:q], color=AMARELO, linestyle="--", linewidth=1.3)
        ax.fill_between(x, capital[:q], pico[:q], color=VERMELHO, alpha=0.25)
        ax.plot(x, capital[:q], color=AZUL, linewidth=2)
        ax.scatter([q - 1], [capital[q - 1]], color="white", s=30, zorder=5)
        ax.set_xlabel("número de operações", color=CINZA)
        ax.set_title("O pior caso: cruzamento de médias no BTC/USD (5 min, com custos)", color=TEXTO,
                     fontsize=12, fontweight="bold", loc="left")
        dd = capital[q - 1] / pico[q - 1] - 1
        ax.text(0.01, 0.96, f"operação {q - 1} de {n - 1} · conta: {dinheiro(capital[q - 1])} · "
                f"drawdown agora: {pct(dd * 100)}", transform=ax.transAxes, color=CINZA, fontsize=9.5, va="top")
        if q == n:
            precisa = 1 / (1 + queda) - 1
            ax.text(0.98, 0.62, f"fundo: {pct(queda * 100)}\npara voltar ao topo:\n{pct(precisa * 100)}",
                    transform=ax.transAxes, ha="right", color=VERMELHO, fontsize=13, fontweight="bold")

    fig.subplots_adjust(left=0.12, right=0.98, top=0.9, bottom=0.12)
    salvar(fig, desenhar, quadros, "drawdown", fps=15)


def status_texto(ax, txt, cor):
    ax.text(0.01, 0.95, txt, transform=ax.transAxes, color=cor, fontsize=10.5, fontweight="bold", va="top")


def orb():
    todos = pd.read_csv(DADOS / "PETR4" / "PETR4_30min.csv", parse_dates=["Data"])
    c = todos[todos["Data"].astype(str).str.startswith("2026-09-15")].reset_index(drop=True)
    maxima, minima = c["High"][0], c["Low"][0]
    faixa = maxima - minima
    alvo = maxima + 3 * faixa
    n = len(c)
    entrada = int(((c["High"] > maxima) & (c.index > 0)).idxmax())
    saida = int(((c["High"] >= alvo) & (c.index > entrada)).idxmax())
    fig, ax = plt.subplots(figsize=(9, 5), facecolor=FUNDO)
    quadros = [k for k in range(1, n + 1) for _ in range(3)] + [n] * 24

    def desenhar(k):
        ax.clear()
        eixo_escuro(ax)
        ax.set_xlim(-0.8, n - 0.2)
        ax.set_ylim(minima - 0.25, max(c["High"].max(), alvo) + 0.45)  # espaço em cima para o texto
        ax.set_xticks(range(0, n, 2), [f"{h:%Hh%M}" for h in c["Data"][::2]])
        ax.yaxis.set_major_formatter(lambda v, _: dinheiro(v, "R", 2))
        ax.axhspan(minima, maxima, color=AMARELO, alpha=0.15)
        ax.axhline(maxima, color=VERDE, linestyle="--", linewidth=1.1)
        ax.axhline(minima, color=VERMELHO, linestyle="--", linewidth=1.1)
        if k > entrada:
            ax.axhline(alvo, color=AZUL, linestyle=":", linewidth=1.4)
            ax.text(n - 0.3, alvo, " alvo = 3 faixas", color=AZUL, fontsize=9, va="bottom", ha="right")
        candles(ax, c.iloc[:k])
        if k <= 1:
            status_texto(ax, "1º candle (10h00–10h30): a máxima e a mínima formam a faixa de abertura", AMARELO)
        elif k <= entrada:
            status_texto(ax, "esperando o preço sair da faixa...", CINZA)
        else:
            ax.scatter([entrada], [maxima], s=110, color="white", edgecolor=VERDE, linewidth=2, zorder=6)
            if k > saida:
                ax.scatter([saida], [alvo], s=110, marker="s", color="white", edgecolor=AZUL, linewidth=2,
                           zorder=6)
                status_texto(ax, f"COMPROU a {dinheiro(maxima, 'R')} → bateu o alvo de {dinheiro(alvo, 'R')}: "
                             f"{pct((alvo / maxima - 1) * 100)}", AZUL)
            else:
                status_texto(ax, f"rompeu a máxima → COMPRA a {dinheiro(maxima, 'R')} · stop na mínima "
                             f"{dinheiro(minima, 'R')}", VERDE)
        ax.set_title("ORB na PETR4, 15/09/2026, candles de 30 min (Profit Pro)", color=TEXTO, fontsize=12,
                     fontweight="bold", loc="left")

    fig.subplots_adjust(left=0.12, right=0.98, top=0.9, bottom=0.1)
    salvar(fig, desenhar, quadros, "orb", fps=8)


def vwap():
    todos = pd.read_csv(DADOS / "ITUB4" / "ITUB4_15min.csv", parse_dates=["Data"])
    c = todos[todos["Data"].astype(str).str.startswith("2026-09-03")].reset_index(drop=True)
    n = len(c)
    tipico = (c["High"] + c["Low"] + c["Close"]) / 3
    linha = (tipico * c["Volume"]).cumsum() / c["Volume"].cumsum()
    dist = c["Close"] / linha - 1
    ops, aberta = [], None
    for i in range(1, n - 1):
        if aberta is None:
            if dist[i] >= 0.006:
                aberta = ("VENDA", i, c["Close"][i], c["Close"][i] * 1.006)
            elif dist[i] <= -0.006:
                aberta = ("COMPRA", i, c["Close"][i], c["Close"][i] * 0.994)
        else:
            lado, ie, pe, stop = aberta
            if (lado == "VENDA" and c["High"][i] >= stop) or (lado == "COMPRA" and c["Low"][i] <= stop):
                ops.append((lado, ie, pe, i, stop))
                aberta = None
            elif (lado == "VENDA" and c["Low"][i] <= linha[i]) or (lado == "COMPRA" and c["High"][i] >= linha[i]):
                ops.append((lado, ie, pe, i, linha[i]))
                aberta = None
    fig, ax = plt.subplots(figsize=(9, 5), facecolor=FUNDO)
    quadros = [k for k in range(1, n + 1) for _ in range(3)] + [n] * 24

    def desenhar(k):
        ax.clear()
        eixo_escuro(ax)
        ax.set_xlim(-0.8, n + 0.5)
        ax.set_ylim(c["Low"].min() - 0.12, c["High"].max() + 0.25)
        ax.set_xticks(range(0, n, 4), [f"{h:%Hh%M}" for h in c["Data"][::4]])
        ax.yaxis.set_major_formatter(lambda v, _: dinheiro(v, "R", 2))
        x = range(k)
        ax.plot(x, linha[:k] * 1.006, color=CINZA, linestyle=":", linewidth=1.2)
        ax.plot(x, linha[:k] * 0.994, color=CINZA, linestyle=":", linewidth=1.2)
        ax.plot(x, linha[:k], color=AZUL, linewidth=2.4, zorder=4)
        candles(ax, c.iloc[:k], minimo=0.005)
        status, cor = "a VWAP é o preço médio do dia, pesado pelo volume", AZUL
        for lado, ie, pe, isai, ps in ops:
            cor_op = VERMELHO if lado == "VENDA" else VERDE
            if k > ie:
                ax.scatter([ie], [pe], s=100, color="white", edgecolor=cor_op, linewidth=2, zorder=6)
                status, cor = f"preço a 0,6% da VWAP → {lado} a {dinheiro(pe, 'R')}", cor_op
            if k > isai:
                ax.scatter([isai], [ps], s=100, marker="s", color="white", edgecolor=AZUL, linewidth=2, zorder=6)
                ganho = (pe / ps - 1) if lado == "VENDA" else (ps / pe - 1)
                status, cor = f"voltou para a VWAP → saiu a {dinheiro(ps, 'R')} ({pct(ganho * 100)})", AZUL
        status_texto(ax, status, cor)
        ax.set_title("VWAP no ITUB4, 03/09/2026, candles de 15 min (Profit Pro)", color=TEXTO, fontsize=12,
                     fontweight="bold", loc="left")

    fig.subplots_adjust(left=0.12, right=0.98, top=0.9, bottom=0.1)
    salvar(fig, desenhar, quadros, "vwap", fps=8)


def ifr():
    todos = pd.read_csv(DADOS / "BTCUSD" / "BTCUSD_30min.csv", parse_dates=["Data"])
    var = todos["Close"].diff()
    altas = var.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    quedas = (-var.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    todos["IFR"] = 100 - 100 / (1 + altas / quedas)
    c = todos[todos["Data"].astype(str).str.startswith("2026-08-03")].reset_index(drop=True)
    n = len(c)
    v = c["IFR"]
    ops, aberta = [], None
    for i in range(1, n):
        if aberta is None:
            if v[i] <= 30:
                aberta = ("COMPRA", i, c["Close"][i], c["Close"][i] * 0.99)
            elif v[i] >= 70:
                aberta = ("VENDA", i, c["Close"][i], c["Close"][i] * 1.01)
        else:
            lado, ie, pe, stop = aberta
            if (lado == "VENDA" and c["High"][i] >= stop) or (lado == "COMPRA" and c["Low"][i] <= stop):
                ops.append((lado, ie, pe, i, stop))
                aberta = None
            elif (lado == "VENDA" and v[i] <= 50) or (lado == "COMPRA" and v[i] >= 50):
                ops.append((lado, ie, pe, i, c["Close"][i]))
                aberta = None
    fig, (ax, axi) = plt.subplots(2, 1, figsize=(9, 5.6), facecolor=FUNDO, sharex=True,
                                  gridspec_kw={"height_ratios": [2.6, 1.3]})
    quadros = [k for k in range(1, n + 1) for _ in range(2)] + [n] * 24

    def desenhar(k):
        for a in (ax, axi):
            a.clear()
            eixo_escuro(a)
        ax.set_xlim(-0.8, n - 0.2)
        ax.set_ylim(c["Low"].min() - 250, c["High"].max() + 450)
        ax.yaxis.set_major_formatter(lambda y, _: dinheiro(y, casas=0))
        candles(ax, c.iloc[:k], minimo=8)
        axi.set_ylim(10, 90)
        for nivel, cor in [(70, VERMELHO), (30, VERDE), (50, AZUL)]:
            axi.axhline(nivel, color=cor, linestyle=":" if nivel != 50 else "--", linewidth=1.2)
        axi.plot(range(k), v[:k], color=TEXTO, linewidth=1.8)
        axi.set_yticks([30, 50, 70])
        axi.set_xticks(range(0, n, 8), [f"{h:%Hh%M}" for h in c["Data"][::8]])
        axi.text(0.005, 0.9, "IFR (14)", transform=axi.transAxes, color=CINZA, fontsize=9, va="top")
        status, cor = "IFR abaixo de 30 = sobrevendido (compra) · acima de 70 = sobrecomprado (venda)", CINZA
        for lado, ie, pe, isai, ps in ops:
            cor_op = VERMELHO if lado == "VENDA" else VERDE
            if k > ie:
                ax.scatter([ie], [pe], s=90, color="white", edgecolor=cor_op, linewidth=2, zorder=6)
                axi.scatter([ie], [v[ie]], s=50, color=cor_op, zorder=6)
                status, cor = f"IFR em {v[ie]:.0f} → {lado} a {dinheiro(pe, casas=0)}", cor_op
            if k > isai:
                ax.scatter([isai], [ps], s=90, marker="s", color="white", edgecolor=AZUL, linewidth=2, zorder=6)
                ganho = (pe / ps - 1) if lado == "VENDA" else (ps / pe - 1)
                status, cor = f"IFR voltou a 50 → saiu a {dinheiro(ps, casas=0)} ({pct(ganho * 100)})", AZUL
        status_texto(ax, status, cor)
        ax.set_title("IFR no BTC/USD, 03/08/2026, candles de 30 min (Binance, UTC)", color=TEXTO, fontsize=12,
                     fontweight="bold", loc="left")

    fig.subplots_adjust(left=0.12, right=0.98, top=0.92, bottom=0.08, hspace=0.08)
    salvar(fig, desenhar, quadros, "ifr", fps=10)


def medias():
    todos = pd.read_csv(DADOS / "TESLA" / "TESLA_5min.csv")
    todos["Data"] = pd.to_datetime(todos["Data"].str[:19])
    todos["rapida"] = todos["Close"].ewm(span=9, adjust=False).mean()
    todos["lenta"] = todos["Close"].ewm(span=21, adjust=False).mean()
    c = todos[todos["Data"].astype(str).str.startswith("2026-09-16")].reset_index(drop=True)
    n = len(c)
    acima = c["rapida"] > c["lenta"]
    cruz = [i for i in range(1, n - 1) if acima[i] != acima[i - 1]]
    fig, ax = plt.subplots(figsize=(9, 5), facecolor=FUNDO)
    quadros = list(range(2, n + 1)) + [n] * 24

    def desenhar(k):
        ax.clear()
        eixo_escuro(ax)
        ax.set_xlim(-1, n + 0.5)
        ax.set_ylim(c["Low"].min() - 0.8, c["High"].max() + 1.6)
        ax.set_xticks(range(0, n, 12), [f"{h:%Hh%M}" for h in c["Data"][::12]])
        ax.yaxis.set_major_formatter(lambda y, _: dinheiro(y, casas=0))
        candles(ax, c.iloc[:k], largura=0.65, minimo=0.05)
        ax.plot(range(k), c["rapida"][:k], color=AZUL, linewidth=2.2, zorder=4, label="MME 9 (rápida)")
        ax.plot(range(k), c["lenta"][:k], color=ROXO, linewidth=2.2, zorder=4, label="MME 21 (lenta)")
        ax.legend(loc="lower left", facecolor=PAINEL, edgecolor=GRADE, labelcolor=TEXTO, fontsize=9)
        status, cor = "esperando a média rápida cruzar a lenta...", CINZA
        for j, i in enumerate(cruz):
            if k > i:
                lado = "COMPRA" if acima[i] else "VENDA"
                cor_op = VERDE if lado == "COMPRA" else VERMELHO
                ax.scatter([i], [c["Close"][i]], s=100, color="white", edgecolor=cor_op, linewidth=2, zorder=6)
                status = f"cruzou {'para cima' if lado == 'COMPRA' else 'para baixo'} → {lado} a " \
                         f"{dinheiro(c['Close'][i])}" + (" (virou a mão)" if j > 0 else "")
                cor = cor_op
        if k == n and cruz:
            ultimo = cruz[-1]
            lado = "COMPRA" if acima[ultimo] else "VENDA"
            pe, ps = c["Close"][ultimo], c["Close"][n - 1]
            ganho = (pe / ps - 1) if lado == "VENDA" else (ps / pe - 1)
            ax.scatter([n - 1], [ps], s=100, marker="s", color="white", edgecolor=AZUL, linewidth=2, zorder=6)
            status, cor = f"fim do dia → fechou a {dinheiro(ps)} ({pct(ganho * 100)})", AZUL
        status_texto(ax, status, cor)
        ax.set_title("Cruzamento de médias na Tesla, 16/09/2026, candles de 5 min (Yahoo)", color=TEXTO,
                     fontsize=12, fontweight="bold", loc="left")

    fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.1)
    salvar(fig, desenhar, quadros, "medias", fps=12)


def lei():
    rng = np.random.default_rng(7)
    pct_caras = np.cumsum(rng.integers(0, 2, 1000)) / np.arange(1, 1001) * 100
    paradas = sorted({int(x) for x in np.geomspace(1, 1000, 60)}) + [1000] * 24
    fig, ax = plt.subplots(figsize=(9, 4.8), facecolor=FUNDO)

    def desenhar(k):
        ax.clear()
        eixo_escuro(ax)
        ax.set_xscale("log")
        ax.set_xlim(1, 1000)
        ax.set_xticks([1, 10, 100, 1000], ["1", "10", "100", "1.000"])
        ax.set_ylim(0, 100)
        margem = 2 * 0.5 / np.sqrt(np.arange(1, 1001)) * 100
        xs = np.arange(1, 1001)
        ax.fill_between(xs, 50 - margem, 50 + margem, color=AMARELO, alpha=0.12)
        ax.axhline(50, color=AMARELO, linestyle="--", linewidth=1.2)
        ax.text(1.1, 52, "50% real · faixa amarela = margem de erro (2 × 0,5 ÷ √n)", color=AMARELO, fontsize=9)
        ax.plot(xs[:k], pct_caras[:k], color=AZUL, linewidth=2)
        ax.scatter([k], [pct_caras[k - 1]], color="white", s=40, zorder=5)
        ax.set_xlabel("número de lançamentos (escala log)", color=CINZA)
        ax.set_ylabel("% de caras", color=CINZA)
        txt = f"Lei dos grandes números: {k:,} lançamentos → {pct_caras[k - 1]:.1f}% de caras"
        ax.set_title(txt.replace(".", ",").replace("1,000", "1.000"), color=TEXTO, fontsize=12,
                     fontweight="bold", loc="left")

    fig.subplots_adjust(left=0.1, right=0.97, top=0.9, bottom=0.14)
    salvar(fig, desenhar, paradas, "lei_grandes_numeros", fps=10)


def main():
    for tema in ("escuro", "claro"):
        (PASTA / f"hero_{tema}.svg").write_text(hero_svg(tema), encoding="utf-8")
        (PASTA / f"numeros_{tema}.svg").write_text(numeros_svg(tema), encoding="utf-8")
    dias, diario, final, final_sem, n_ops, ops = resultados()
    print("finais (com custos):", {k: round(v[-1], 1) for k, v in diario.items()})
    corrida(dias, diario)
    custo(final, final_sem, n_ops)
    heatmap(final)
    drawdown(ops)
    orb()
    vwap()
    ifr()
    medias()
    lei()
    print("pronto")


if __name__ == "__main__":
    main()
