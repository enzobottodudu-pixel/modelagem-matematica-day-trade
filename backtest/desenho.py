"""
DESENHOS DO MOTOR — transforma um dia simulado em uma imagem fácil de entender.

Cada imagem mostra:
  - os candles do dia (verde = subiu, vermelho = caiu);
  - ▲ onde o motor ENTROU e ✕ onde SAIU;
  - a faixa colorida da operação (verde = lucro, vermelho = prejuízo);
  - as linhas tracejadas do STOP (vermelha) e do ALVO (verde), quando existem;
  - o resultado final, já com o custo.

As imagens ficam em backtest/imagens/.
"""

from pathlib import Path

import matplotlib.pyplot as plt

PASTA_IMAGENS = Path(__file__).resolve().parent / "imagens"

# Cores (as mesmas em todas as imagens)
VERDE = "#1a9850"
VERMELHO = "#d73027"
AZUL = "#2c7bb6"
CINZA = "#4d4d4d"
FUNDO = "#fbfbfb"
LARANJA = "#f28e2b"


def desenhar_dia(ax, candles, operacoes, titulo, media_rapida=None, media_lenta=None):
    """Desenha UM dia simulado no quadro 'ax' (e as médias, se forem passadas)."""
    ax.set_facecolor(FUNDO)
    largura = 0.6 if len(candles) <= 20 else 0.7  # candles mais finos quando o dia tem muitos

    # 0) As linhas das médias (rápida em azul, lenta em laranja)
    if media_rapida is not None:
        ax.plot(
            range(len(media_rapida)), media_rapida, color=AZUL, linewidth=1.6, alpha=0.7, zorder=4, label="média rápida"
        )
    if media_lenta is not None:
        ax.plot(
            range(len(media_lenta)), media_lenta, color=LARANJA, linewidth=1.6, alpha=0.8, zorder=4, label="média lenta"
        )
    if media_rapida is not None or media_lenta is not None:
        ax.legend(loc="upper left", fontsize=8, frameon=False)

    # 0b) A última hora do dia (pedaço 7): uma faixa cinza no fundo
    horas_finais = [i for i, c in enumerate(candles) if c.get("ultima_hora")]
    if horas_finais:
        ax.axvspan(horas_finais[0] - 0.5, horas_finais[-1] + 0.5, color=CINZA, alpha=0.10, zorder=0)
        ax.text(
            horas_finais[0] - 0.4,
            1.0,
            "última hora",
            transform=ax.get_xaxis_transform(),
            va="top",
            fontsize=8,
            color=CINZA,
        )

    # 1) Os candles
    for i, c in enumerate(candles):
        cor = VERDE if c["fechamento"] >= c["abertura"] else VERMELHO
        if "maxima" in c:  # o "pavio": a linha fina da mínima até a máxima
            ax.vlines(i, c["minima"], c["maxima"], color=cor, linewidth=1, zorder=2)
        corpo = abs(c["fechamento"] - c["abertura"]) or 0.0001  # corpo: da abertura ao fechamento
        ax.bar(i, corpo, bottom=min(c["abertura"], c["fechamento"]), width=largura, color=cor, zorder=3)

    # 2) As operações
    # Modo compacto: dia de verdade (muitos candles) com mais de 2 operações -> número no gráfico + lista ao lado
    compacto = len(candles) > 20 and len(operacoes) > 2
    lista = []
    for numero, op in enumerate(operacoes, start=1):
        ganhou = op["resultado"] >= 0
        cor_op = VERDE if ganhou else VERMELHO
        # onde a entrada aconteceu dentro do candle: abertura = começo, fechamento = fim, recuo = no meio
        ajuste = {"abertura": -largura / 2, "fechamento": largura / 2, "recuo": 0}
        x_entrada = op["candle_entrada"] + ajuste[op.get("tipo_entrada", "abertura")]
        x_saida = op["candle_saida"] + (largura / 2 if op["motivo"] != "stop" and op["motivo"] != "alvo" else 0)

        # faixa colorida entre a entrada e a saída
        ax.axvspan(x_entrada, x_saida, color=cor_op, alpha=0.08, zorder=1)

        # linhas do stop e do alvo
        if op.get("preco_stop") is not None:
            ax.hlines(op["preco_stop"], x_entrada, x_saida, colors=VERMELHO, linestyles="--", linewidth=1.2, zorder=4)
            ax.annotate(
                "stop",
                (x_saida, op["preco_stop"]),
                xytext=(16, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=8,
                color=VERMELHO,
            )
        if op.get("preco_alvo") is not None:
            ax.hlines(op["preco_alvo"], x_entrada, x_saida, colors=VERDE, linestyles="--", linewidth=1.2, zorder=4)
            ax.annotate(
                "alvo",
                (x_saida, op["preco_alvo"]),
                xytext=(16, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=8,
                color=VERDE,
            )

        # entrada (▲ compra / ▼ venda) e saída (✕)
        marca = "^" if op["direcao"] == "compra" else "v"
        ax.scatter(x_entrada, op["entrada"], marker=marca, s=110, color=AZUL, edgecolor="white", zorder=6)
        ax.scatter(x_saida, op["saida"], marker="X", s=110, color=CINZA, edgecolor="white", zorder=6)
        if compacto:
            ax.annotate(
                str(numero),
                (x_saida, op["saida"]),
                xytext=(0, 12),
                textcoords="offset points",
                ha="center",
                fontsize=8,
                fontweight="bold",
                color="white",
                zorder=8,
                bbox={"boxstyle": "circle,pad=0.25", "facecolor": cor_op, "edgecolor": "none"},
            )
            lista.append(
                f"{numero}) {op['direcao']} {op['entrada']:.2f} → {op['saida']:.2f}  "
                f"{op['resultado']:+.2f}%  ({op['motivo']})"
            )
            continue  # no modo compacto, os textos vão para a lista
        ax.annotate(
            f"{op['direcao']}\n{op['entrada']:.2f}",
            (x_entrada, op["entrada"]),
            xytext=(0, 16)
            if op.get("tipo_entrada") == "fechamento"
            else ((-10, 0) if op["direcao"] == "compra" else (-10, -20)),
            textcoords="offset points",
            ha="center" if op.get("tipo_entrada") == "fechamento" else "right",
            va="bottom" if op.get("tipo_entrada") == "fechamento" else "center",
            fontsize=8,
            color=AZUL,
            fontweight="bold",
        )

        # caixinha com o resultado
        texto = f"saiu: {op['motivo']}\n{op['saida']:.2f}  →  {op['resultado']:+.2f}%"
        ax.annotate(
            texto,
            (x_saida, op["saida"]),
            xytext=(0, 24 if ganhou else -24),
            textcoords="offset points",
            ha="center",
            va="bottom" if ganhou else "top",
            fontsize=8,
            color="white",
            fontweight="bold",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": cor_op, "edgecolor": "none"},
            zorder=7,
        )

    if lista:
        ax.text(
            1.01,
            1.0,
            "\n".join(lista),
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=8,
            family="monospace",
            bbox={"boxstyle": "round,pad=0.5", "facecolor": "white", "edgecolor": "#dddddd"},
        )

    if not operacoes:
        ax.text(
            0.5,
            0.88,
            "nenhuma operação neste dia",
            transform=ax.transAxes,
            ha="center",
            fontsize=9,
            color=CINZA,
            fontweight="bold",
            bbox={"boxstyle": "round,pad=0.4", "facecolor": "#eeeeee", "edgecolor": "none"},
        )

    # 3) Eixos e título
    rotulos = [c.get("horario", f"candle {i}") for i, c in enumerate(candles)]
    passo = max(1, len(candles) // 10)  # no máximo ~10 rótulos, para não amontoar
    ax.set_xticks(range(0, len(candles), passo))
    ax.set_xticklabels(rotulos[::passo], fontsize=8)
    sobra = max(1.2, len(candles) * 0.08)
    ax.set_xlim(-sobra, len(candles) - 1 + sobra)
    ax.margins(y=0.25)
    ax.set_ylabel("Preço", fontsize=9)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="y", alpha=0.25)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_title(titulo, fontsize=10, loc="left", fontweight="bold")


def salvar_painel(dias, titulo_geral, nome_arquivo, colunas=1):
    """Junta vários dias numa imagem só (um quadro embaixo do outro) e salva em backtest/imagens/."""
    PASTA_IMAGENS.mkdir(exist_ok=True)
    linhas = -(-len(dias) // colunas)  # divisão arredondando para cima
    fig, quadros = plt.subplots(linhas, colunas, figsize=(10 * colunas, 3.6 * linhas), squeeze=False)
    fig.patch.set_facecolor("white")
    # cada dia: (candles, operações, título) ou (candles, operações, título, média rápida)
    for ax, dia in zip(quadros.T.flatten(), dias):  # preenche coluna por coluna
        desenhar_dia(ax, *dia)
    fig.suptitle(titulo_geral, fontsize=13, fontweight="bold", x=0.01, ha="left")
    fig.text(
        0.01,
        0.005,
        "▲ compra   ▼ venda   ✕ saída   -- stop (vermelho) / alvo (verde)   resultados já com o custo",
        fontsize=8,
        color=CINZA,
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    caminho = PASTA_IMAGENS / nome_arquivo
    fig.savefig(caminho, dpi=130)
    plt.close(fig)
    return caminho


def salvar_pedaco1(exemplos, nome_arquivo):
    """Pedaço 1: mostra a conta de cada operação em 3 barras (variação do preço, custo e resultado).

    exemplos: lista de (direcao, preco_entrada, preco_saida, custo, resultado)
    """
    PASTA_IMAGENS.mkdir(exist_ok=True)
    fig, quadros = plt.subplots(1, len(exemplos), figsize=(4 * len(exemplos), 4.2), sharey=True)
    fig.patch.set_facecolor("white")
    for ax, (direcao, entrada, saida, custo, resultado) in zip(quadros, exemplos):
        variacao = resultado + custo  # o que o preço andou a favor (ou contra), antes do custo
        valores = [variacao, -custo, resultado]
        nomes = ["ganho/perda\ncom o preço", "custo", "resultado\nfinal"]
        cores = [VERDE if variacao >= 0 else VERMELHO, VERMELHO, VERDE if resultado >= 0 else VERMELHO]
        barras = ax.bar(nomes, valores, color=cores, width=0.55, zorder=3)
        barras[2].set_edgecolor(CINZA)
        barras[2].set_linewidth(1.5)
        for barra, valor in zip(barras, valores):
            ax.annotate(
                f"{valor:+.2f}%",
                (barra.get_x() + barra.get_width() / 2, valor),
                xytext=(0, 5 if valor >= 0 else -5),
                textcoords="offset points",
                ha="center",
                va="bottom" if valor >= 0 else "top",
                fontsize=10,
                fontweight="bold",
            )
        ax.axhline(0, color=CINZA, linewidth=1)
        ax.set_facecolor(FUNDO)
        ax.grid(axis="y", alpha=0.25)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        verbo = "vende" if direcao == "compra" else "recompra"
        ax.set_title(f"{direcao.capitalize()} a {entrada:g} → {verbo} a {saida:g}", fontsize=11, fontweight="bold")
    quadros[0].set_ylabel("% do preço de entrada")
    quadros[0].margins(y=0.2)
    fig.suptitle(
        "Pedaço 1: a conta de uma operação (custo de 0,09%, o da PETR4)",
        fontsize=13,
        fontweight="bold",
        x=0.01,
        ha="left",
    )
    fig.text(
        0.01,
        0.01,
        "resultado final = ganho (ou perda) com o preço − custo   (números inventados)",
        fontsize=8,
        color=CINZA,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    caminho = PASTA_IMAGENS / nome_arquivo
    fig.savefig(caminho, dpi=130)
    plt.close(fig)
    return caminho


def salvar_pedaco8(operacoes, titulo, nome_arquivo):
    """Pedaço 8: o resultado de CADA operação do período (em cima) e a soma acumulada (embaixo)."""
    PASTA_IMAGENS.mkdir(exist_ok=True)
    resultados = [op["resultado"] for op in operacoes]
    acumulado, soma = [], 0.0
    for r in resultados:
        soma += r
        acumulado.append(soma)
    numeros = range(1, len(resultados) + 1)

    fig, (cima, baixo) = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True, gridspec_kw={"height_ratios": [1, 1]})
    fig.patch.set_facecolor("white")

    cores = [VERDE if r >= 0 else VERMELHO for r in resultados]
    cima.bar(numeros, resultados, color=cores, width=0.8, zorder=3)
    cima.axhline(0, color=CINZA, linewidth=1)
    cima.set_ylabel("resultado (%)", fontsize=9)
    ganhos = sum(1 for r in resultados if r > 0)
    cima.set_title(
        f"Cada barra é uma operação: {ganhos} com lucro (verde) e {len(resultados) - ganhos} com prejuízo (vermelho)",
        fontsize=10,
        loc="left",
        fontweight="bold",
    )

    cor_linha = VERDE if acumulado and acumulado[-1] >= 0 else VERMELHO
    baixo.plot(numeros, acumulado, color=cor_linha, linewidth=2, zorder=3)
    baixo.fill_between(numeros, acumulado, 0, color=cor_linha, alpha=0.12)
    baixo.axhline(0, color=CINZA, linewidth=1)
    baixo.set_ylabel("soma acumulada (%)", fontsize=9)
    baixo.set_xlabel("número da operação (em ordem de data)", fontsize=9)
    if acumulado:
        baixo.annotate(
            f"soma final: {acumulado[-1]:+.2f}%",
            (len(acumulado), acumulado[-1]),
            xytext=(-6, -16),
            textcoords="offset points",
            ha="right",
            fontsize=9,
            fontweight="bold",
            color=cor_linha,
        )
    baixo.set_title("A soma das operações ao longo do tempo", fontsize=10, loc="left", fontweight="bold")

    for ax in (cima, baixo):
        ax.set_facecolor(FUNDO)
        ax.grid(axis="y", alpha=0.25)
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    fig.suptitle(titulo, fontsize=13, fontweight="bold", x=0.01, ha="left")
    fig.text(0.01, 0.005, "resultados já com o custo", fontsize=8, color=CINZA)
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    caminho = PASTA_IMAGENS / nome_arquivo
    fig.savefig(caminho, dpi=130)
    plt.close(fig)
    return caminho
