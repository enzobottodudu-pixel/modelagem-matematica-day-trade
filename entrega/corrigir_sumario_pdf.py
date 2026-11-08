"""Corrige os números de página do SUMÁRIO no PDF exportado do Google Docs.

Por quê: o Docs calcula as páginas do sumário na tela do editor, mas o PDF é
montado de outro jeito (figuras e equações ocupam um pouco mais de espaço).
Resultado: no PDF o sumário fica 1 a 2 páginas atrás.

Como: o próprio PDF já sabe onde cada título está (os "marcadores" do PDF).
O programa lê essa página certa, apaga o número velho do sumário e escreve
o número certo no mesmo lugar, com a mesma fonte (Arial 11).

Uso: py -3.14 entrega/corrigir_sumario_pdf.py ENTRADA.pdf SAIDA.pdf
"""

import sys

import pymupdf

ARIAL = "C:/Windows/Fonts/arial.ttf"


def linhas_do_sumario(pagina):
    """Devolve (titulo, span_do_numero) de cada linha do sumário."""
    linhas = {}
    for bloco in pagina.get_text("dict")["blocks"]:
        for linha in bloco.get("lines", []):
            for span in linha["spans"]:
                y = round(span["origin"][1])
                linhas.setdefault(y, []).append(span)
    resultado = []
    for y in sorted(linhas):
        spans = sorted(linhas[y], key=lambda s: s["bbox"][0])
        numero = [s for s in spans if s["text"].strip().isdigit() and s["bbox"][0] > 480]
        if not numero:
            continue
        titulo = "".join(s["text"] for s in spans if s is not numero[0])
        titulo = titulo.replace("\u200b", "").strip()
        resultado.append((titulo, numero[0]))
    return resultado


def main(entrada, saida):
    doc = pymupdf.open(entrada)
    pag_sumario = next(i for i in range(20) if "SUMÁRIO" in doc[i].get_text())
    pagina = doc[pag_sumario]
    # marcadores do PDF = títulos de verdade, com a página certa
    marcadores = [(t.strip(), p) for _, t, p in doc.get_toc() if t.strip()]
    linhas = linhas_do_sumario(pagina)
    assert len(linhas) == len(marcadores), (len(linhas), len(marcadores))

    links = pagina.get_links()
    trocas = []
    for (titulo, span), (marcador, certa) in zip(linhas, marcadores):
        # o título do sumário e o do marcador têm de ser o mesmo
        assert titulo[:20] == marcador[:20], (titulo, marcador)
        velha = int(span["text"])
        if velha != certa:
            trocas.append((titulo, velha, certa, span))
            x0, y0, x1, y1 = span["bbox"]
            pagina.add_redact_annot(pymupdf.Rect(x0, y0 + 1, x1, y1 - 1))
    pagina.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    for _, _, certa, span in trocas:
        pagina.insert_text(span["origin"], str(certa), fontsize=span["size"], fontname="ArialMT", fontfile=ARIAL)
    # os links do sumário (clicar e ir para o capítulo) continuam iguais
    # (apagar o número apaga o link da linha junto; então refaz todos)
    for link in pagina.get_links():
        pagina.delete_link(link)
    for link in links:
        pagina.insert_link(link)
    doc.save(saida, garbage=3, deflate=True)
    for titulo, velha, certa, _ in trocas:
        print(f"{velha:>3} -> {certa:>3}  {titulo}")
    print(f"{len(trocas)} números corrigidos de {len(linhas)}.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
