"""Transforma a exportação em Markdown do Google Docs no TCC_texto.md.

O Docs exporta (Arquivo > Fazer download > Markdown) com as imagens dentro do
arquivo, em base64. Este programa:
- troca cada imagem pela figura da pasta figuras/ (a 1ª imagem é a Figura 1...);
- tira as âncoras {#...} e os títulos vazios;
- refaz o sumário com links que funcionam no GitHub (sem número de página,
  porque a página certa é a do PDF em entrega/);
- deixa as equações do Docs prontas para o GitHub (as de destaque em $$ e o
  "US$" e o "R$" de dentro das contas escritos como texto + cifrão);
- troca a caixa do código do Apêndice A (que o Docs exporta como uma tabela
  de uma linha só) pelo código de verdade, conferindo que é o mesmo texto;
- arruma os títulos do glossário em itálico ("***Stop*****:**" mostrava
  asteriscos soltos no GitHub).

Uso: py -3.14 documento/limpar_markdown.py EXPORTACAO.md documento/TCC_texto.md
"""

import re
import sys
from pathlib import Path

AVISO = (
    "> [!NOTE]\n"
    "> Texto final do TCC, exportado do Google Docs em 08/11/2026 para ler no "
    "GitHub. A versão de entrega, com as páginas, é o PDF "
    "[`entrega/TCC_Enzo_final.pdf`](../entrega/TCC_Enzo_final.pdf). "
    "As figuras estão em [`figuras/`](../figuras/LEGENDAS.md).\n"
)


def ancora_github(titulo):
    """O link que o GitHub cria para um título."""
    t = re.sub(r"[*_`]", "", titulo).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return "#" + t.replace(" ", "-")


def linha_do_sumario(linha):
    """'[1.1 Título<TAB>13](#...)' vira '- [1.1 Título](#link)'."""
    m = re.match(r"^\[(.+?)\t\d+\]\([^)]*\)\s*$", linha)
    if not m:
        return None
    titulo = re.sub(r"\*\*", "", m.group(1)).strip()
    numero = titulo.split(" ")[0]
    nivel = numero.count(".") if numero[:1].isdigit() else 0
    return "  " * nivel + f"- [{titulo}]({ancora_github(titulo)})"


TRECHO_APENDICE_A = Path(__file__).parent.parent / "estrategias_2_9" / "apendice_A_trecho.py"


def codigo_do_apendice_a(celula):
    """A caixa do Apêndice A vira um bloco de código Python.

    O código vem do arquivo apendice_A_trecho.py; antes, confere que ele tem o
    mesmo texto da caixa do Docs (sem contar espaços e quebras de linha).
    """
    codigo = TRECHO_APENDICE_A.read_text(encoding="utf-8").rstrip()
    do_docs = re.sub(r"\\([!-/:-@\[-`{-~])", r"\1", celula.strip("| "))
    sem_espaco = re.compile(r"\s+")
    if sem_espaco.sub("", do_docs) != sem_espaco.sub("", codigo):
        raise SystemExit("o código do Apêndice A no Docs mudou: conferir")
    return ["```python", codigo, "```"]


def contas_para_o_github(linha):
    """Dentro das contas, 'US$' e 'R$' viram texto (senão o $ fecha a conta)."""
    linha = re.sub(r"(?<![\\\w])(US|R)\$(?=\d)", r"\\text{\1}\\$", linha)
    # equação sozinha na linha: vira bloco $$ (equação de destaque)
    m = re.match(r"^\$(\\\s)?([^$]+)\$\s*$", linha)
    if m:
        return ["", "$$", m.group(2).strip(), "$$", ""]
    # conta dentro da frase com cifrão: vai entre crases ($`...`$), o jeito do
    # GitHub que não troca o \$ por $ antes de desenhar a conta
    partes = re.split(r"(?<!\\)\$", linha)
    if len(partes) % 2:
        for i in range(1, len(partes), 2):
            if "\\$" in partes[i]:
                partes[i] = f"`{partes[i]}`"
        linha = "$".join(partes)
    return [linha]


def main():
    bruto = Path(sys.argv[1]).read_text(encoding="utf-8")
    bruto = re.sub(r"^\[image\d+\]: <data:[^>]*>\s*$", "", bruto, flags=re.MULTILINE)

    figura = 0

    def trocar_imagem(_):
        nonlocal figura
        figura += 1
        arquivo = "Figura_39.gif" if figura == 39 else f"Figura_{figura:02d}.png"
        return f'<img src="../figuras/{arquivo}" alt="Figura {figura}" width="640">'

    bruto = re.sub(r"!\[\]\[image\d+\]", trocar_imagem, bruto)

    saida = [AVISO]
    pular_divisoria = False
    for linha in bruto.splitlines():
        if re.match(r"^#+\s*$", linha):
            continue  # título vazio
        if linha.startswith("| ") and "volume\\_do\\_yahoo" in linha:
            saida.extend(codigo_do_apendice_a(linha))
            pular_divisoria = True
            continue
        if pular_divisoria and re.match(r"^\| :?-+:? \|\s*$", linha):
            pular_divisoria = False
            continue  # a linha "| :---- |" da tabela de uma célula
        linha = re.sub(r"\s*\{#[^}]*\}\s*$", "", linha)
        # parágrafo que começa com Tab: no GitHub viraria caixa de código
        linha = linha.lstrip("\t")
        # glossário: "***Stop*****:**" vira "**_Stop_:**"
        linha = re.sub(r"^\*\*\*([^*]+)\*\*\*\*\*:\*\*", r"**_\1_:**", linha)
        sumario = linha_do_sumario(linha)
        if sumario is not None:
            # os itens do sumário ficam juntos, sem linha vazia entre eles
            while saida and saida[-1] == "" and saida[-2].lstrip().startswith("- ["):
                saida.pop()
            saida.append(sumario)
            continue
        saida.extend(contas_para_o_github(linha))

    texto = re.sub(r"\n{3,}", "\n\n", "\n".join(saida)).strip() + "\n"
    Path(sys.argv[2]).write_text(texto, encoding="utf-8")
    print(f"{figura} figuras; {len(texto):,} caracteres")


if __name__ == "__main__":
    main()
