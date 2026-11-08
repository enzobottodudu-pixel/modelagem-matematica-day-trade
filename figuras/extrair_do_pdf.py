"""Tira as 44 figuras do PDF final do TCC e monta a galeria LEGENDAS.md.

Assim a pasta figuras/ tem exatamente as imagens que estão no trabalho, com a
legenda e a fonte copiadas do próprio PDF.

Uso (com o python que tem o pymupdf):
    python figuras/extrair_do_pdf.py entrega/TCC_Enzo_final.pdf
"""

import io
import re
import sys
from pathlib import Path

import pymupdf
from PIL import Image

PASTA = Path(__file__).parent

# o programa que gera cada figura (o caminho é a partir da raiz do repositório)
PROGRAMA = {
    1: "graficos_2_3/grafico1_candles.py",
    2: "graficos_2_3/grafico2_juros_spy.py",
    3: "graficos_2_3/grafico3_empresa.py",
    4: "graficos_2_3/grafico4_inflacao_juros.py",
    **dict.fromkeys(range(5, 11), "graficos_2_4/indicadores.py"),
    11: "graficos_2_5/emocoes.py",
    12: "graficos_2_5/emocoes.py",
    13: "graficos_cap2/petroleo_guerra_ira.py",
    14: "graficos_cap2/efeitos_selic.py",
    15: "graficos_cap2/economia.py",
    16: "graficos_cap2/oferta_demanda.py",
    17: "graficos_cap2/economia.py",
    18: "graficos_cap2/micro_itau.py",
    19: "graficos_cap2/economia.py",
    20: "graficos_cap2/nq_covid.py",
    21: "graficos_cap2/regimes_ibov.py",
    22: "formula retorno.py",
    23: "fórmula taxa de acerto.py",
    24: "Formula payoff.py",
    25: "Esperança matemática.py",
    26: "taxa de acerto minima.py",
    27: "A lei dos grandes numeros.py",
    28: "graficos_cap3/grafico_lei_grandes_numeros.py",
    29: "margem de erro.py",
    30: "drawdown.py",
    31: "recuperacao drawdown.py",
    32: "graficos_cap4/volatilidade_ativos.py",
    33: "graficos_2_9/orb_exemplo.py",
    34: "graficos_2_9/vwap_exemplo.py",
    35: "graficos_2_9/ifr_exemplo.py",
    36: "graficos_2_9/medias_exemplo.py",
    37: "previsao/previsao.py",
    38: "previsao/simulacao.py",
    39: "comparativo/corrida_capital.py",
    **dict.fromkeys(range(40, 45), "estrategias_2_9/estrategias.py"),
}
# figuras que são a imagem de um programa do Enzo (feita por este programa)
CODIGO = range(22, 32)


def texto_com_italico(bloco):
    """Junta as linhas de um bloco do PDF, pondo *itálico* onde o PDF tem."""
    pedacos = []
    for linha in bloco["lines"]:
        for span in linha["spans"]:
            italico = bool(span["flags"] & 2) and span["text"].strip() != ""
            if pedacos and pedacos[-1][1] == italico:
                pedacos[-1][0] += span["text"]
            else:
                pedacos.append([span["text"], italico])
        pedacos[-1][0] += " "
    saida = ""
    for texto, italico in pedacos:
        if italico:
            miolo = texto.strip()
            antes = " " if texto[:1].isspace() else ""
            depois = " " if texto[-1:].isspace() else ""
            saida += f"{antes}*{miolo}*{depois}"
        else:
            saida += texto
    return re.sub(r"\s+", " ", saida).strip()


def salvar_imagem(doc, xref, smask, destino):
    """Salva a imagem do PDF em PNG, com fundo branco (como no papel)."""
    img = Image.open(io.BytesIO(doc.extract_image(xref)["image"]))
    if smask:
        mascara = Image.open(io.BytesIO(doc.extract_image(smask)["image"]))
        img = img.convert("RGB")
        img.putalpha(mascara.convert("L"))
    if img.mode in ("RGBA", "LA", "P"):
        fundo = Image.new("RGB", img.size, "white")
        fundo.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[3])
        img = fundo
    img.convert("RGB").save(destino, optimize=True)
    return img.size


def main():
    doc = pymupdf.open(sys.argv[1])
    figuras = {}
    for numero_pagina, pagina in enumerate(doc, start=1):
        imagens = []
        for xref, smask, *_ in pagina.get_images(full=True):
            for r in pagina.get_image_rects(xref):
                imagens.append((r.y0, r.y1, xref, smask))
        if not imagens:
            continue  # a Lista de Figuras não tem imagem: fica de fora
        blocos = [b for b in pagina.get_text("dict")["blocks"] if b["type"] == 0]
        for b in blocos:
            legenda = texto_com_italico(b)
            m = re.match(r"^Figura (\d+) –", legenda)
            if not m:
                continue
            # a imagem é a primeira logo abaixo da legenda
            _, y1, xref, smask = min(
                (i for i in imagens if i[0] >= b["bbox"][3] - 2),
                key=lambda i: i[0],
            )
            # e a fonte é o primeiro "Fonte:" logo abaixo da imagem
            fonte = next(
                texto_com_italico(f)
                for f in sorted(blocos, key=lambda f: f["bbox"][1])
                if f["bbox"][1] >= y1 - 2 and texto_com_italico(f).startswith("Fonte:")
            )
            n = int(m.group(1))
            tamanho = salvar_imagem(doc, xref, smask, PASTA / f"Figura_{n:02d}.png")
            figuras[n] = (numero_pagina, legenda, fonte, tamanho)

    faltam = sorted(set(range(1, 45)) - set(figuras))
    assert not faltam, f"figuras não achadas: {faltam}"

    linhas = [
        "# Figuras do TCC",
        "",
        (
            "As 44 figuras do trabalho, **tiradas do PDF final** "
            "([`entrega/TCC_Enzo_final.pdf`](../entrega/TCC_Enzo_final.pdf)) por "
            "[`extrair_do_pdf.py`](extrair_do_pdf.py): cada imagem é exatamente a "
            "que está no TCC, com a legenda e a fonte copiadas do PDF."
        ),
        "",
        "| Partes do trabalho | Figuras |",
        "|---|---|",
        "| 1 Revisão bibliográfica (1.1 a 1.6) | [1](#figura-1) a [12](#figura-12) |",
        "| 1.7 A economia e o mercado | [13](#figura-13) a [21](#figura-21) |",
        "| 2 Método: a matemática (2.1 a 2.7) | [22](#figura-22) a [31](#figura-31) |",
        "| 2.8 e 2.9 Dados e estratégias | [32](#figura-32) a [36](#figura-36) |",
        "| 3 Resultados e discussões | [37](#figura-37) a [44](#figura-44) |",
        "",
    ]
    for n in sorted(figuras):
        pagina, legenda, fonte, (largura, altura) = figuras[n]
        programa = PROGRAMA[n]
        if n in CODIGO:
            origem = (
                f"programa do Enzo [`{programa}`](../{programa.replace(' ', '%20')}), "
                "transformado em imagem por "
                "[`graficos_cap3/imagem_codigo_retorno.py`]"
                "(../graficos_cap3/imagem_codigo_retorno.py)"
            )
        else:
            origem = f"[`{programa}`](../{programa.replace(' ', '%20')})"
        linhas += [
            f"## Figura {n}",
            "",
            f"**{legenda}**",
            "",
            f'<img src="Figura_{n:02d}.png" alt="Figura {n}" width="720">',
            "",
            f"{fonte}",
            "",
            f"<sub>Página {pagina} do PDF · {largura}×{altura} px · gerada por {origem}"
            + (" · no Google Docs ela é animada: [`Figura_39.gif`](Figura_39.gif)" if n == 39 else "")
            + "</sub>",
            "",
        ]
    (PASTA / "LEGENDAS.md").write_text("\n".join(linhas), encoding="utf-8")
    for n in sorted(figuras):
        print(n, figuras[n][0], figuras[n][3], figuras[n][1][:70])


if __name__ == "__main__":
    main()
