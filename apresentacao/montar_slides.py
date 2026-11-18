"""Monta a apresentação da banca no Google Slides, no visual do modelo da escola.

O modelo ("Modelo de Apresentação de TCC para Banca") tem: capa azul-escura com
linha laranja, slides brancos com um rótulo pequeno verde-azulado em cima, título
em Lora e texto em DM Sans, cartões cinza-claro, e o slide final escuro com as
referências. Este programa gera os pedidos (requests) da API do Slides em 4 lotes.

Uso: py -3.14 apresentacao/montar_slides.py
Saída: apresentacao/lote1.json a lote4.json (sem o writeControl).
"""

import json
from pathlib import Path

PASTA = Path(__file__).parent
EMU = 914400

# cores e fontes do modelo
AZUL = "#0F172A"
AZUL2 = "#1E293B"
LARANJA = "#DD6B20"
VERDE = "#0F766E"
TINTA = "#0F172A"
CORPO = "#334155"
CINZA = "#64748B"
CARTAO = "#F1F5F9"
FUNDO2 = "#F8FAFC"
BRANCO = "#FFFFFF"
CLARO = "#E2E8F0"
CLARO2 = "#CBD5E1"
TITULO = "Lora"
TEXTO = "DM Sans"

GIF = "https://raw.githubusercontent.com/enzobottodudu-pixel/modelagem-matematica-day-trade/main/figuras/Figura_39.gif"
REPO = "https://github.com/enzobottodudu-pixel/modelagem-matematica-day-trade"


def rgb(cor):
    cor = cor.lstrip("#")
    return {k: round(int(cor[i : i + 2], 16) / 255, 4) for k, i in zip(("red", "green", "blue"), (0, 2, 4))}


def caixa(pagina, x, y, w, h):
    return {
        "pageObjectId": pagina,
        "size": {
            "width": {"magnitude": round(w * EMU), "unit": "EMU"},
            "height": {"magnitude": round(h * EMU), "unit": "EMU"},
        },
        "transform": {
            "scaleX": 1,
            "scaleY": 1,
            "translateX": round(x * EMU),
            "translateY": round(y * EMU),
            "unit": "EMU",
        },
    }


class Slide:
    """Junta os pedidos de um slide."""

    def __init__(self, sid, fundo):
        self.sid = sid
        self.req = [
            {"createSlide": {"objectId": sid, "slideLayoutReference": {"predefinedLayout": "BLANK"}}},
            {
                "updatePageProperties": {
                    "objectId": sid,
                    "pageProperties": {"pageBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(fundo)}}}},
                    "fields": "pageBackgroundFill.solidFill.color",
                }
            },
        ]
        self.n = 0

    def _id(self, nome):
        self.n += 1
        return f"{self.sid}_{nome}"

    def forma(self, nome, tipo, x, y, w, h, cor):
        oid = self._id(nome)
        self.req += [
            {"createShape": {"objectId": oid, "shapeType": tipo, "elementProperties": caixa(self.sid, x, y, w, h)}},
            {
                "updateShapeProperties": {
                    "objectId": oid,
                    "shapeProperties": {
                        "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(cor)}}},
                        "outline": {"propertyState": "NOT_RENDERED"},
                    },
                    "fields": "shapeBackgroundFill.solidFill.color,outline.propertyState",
                }
            },
        ]
        return oid

    def texto(
        self,
        nome,
        x,
        y,
        w,
        h,
        partes,
        tam=14,
        cor=CORPO,
        fonte=TEXTO,
        negrito=False,
        alinhar="START",
        meio=False,
        bolinhas=False,
        depois=0,
        linha=None,
        sobre=None,
    ):
        """Caixa de texto. 'partes' é um texto ou uma lista de (texto, estilo)."""
        if isinstance(partes, str):
            partes = [(partes, {})]
        oid = self._id(nome)
        if sobre:  # o texto vai dentro de uma forma já criada
            oid = sobre
        else:
            self.req.append(
                {
                    "createShape": {
                        "objectId": oid,
                        "shapeType": "TEXT_BOX",
                        "elementProperties": caixa(self.sid, x, y, w, h),
                    }
                }
            )
        tudo = "".join(t for t, _ in partes)
        self.req.append({"insertText": {"objectId": oid, "text": tudo}})
        base = {
            "fontFamily": fonte,
            "fontSize": {"magnitude": tam, "unit": "PT"},
            "bold": negrito,
            "foregroundColor": {"opaqueColor": {"rgbColor": rgb(cor)}},
        }
        self.req.append(
            {
                "updateTextStyle": {
                    "objectId": oid,
                    "textRange": {"type": "ALL"},
                    "style": base,
                    "fields": "fontFamily,fontSize,bold,foregroundColor",
                }
            }
        )
        inicio = 0
        for t, estilo in partes:
            fim = inicio + len(t)
            if estilo and fim > inicio:
                st, campos = {}, []
                if "negrito" in estilo:
                    st["bold"] = estilo["negrito"]
                    campos.append("bold")
                if "italico" in estilo:
                    st["italic"] = estilo["italico"]
                    campos.append("italic")
                if "cor" in estilo:
                    st["foregroundColor"] = {"opaqueColor": {"rgbColor": rgb(estilo["cor"])}}
                    campos.append("foregroundColor")
                if "tam" in estilo:
                    st["fontSize"] = {"magnitude": estilo["tam"], "unit": "PT"}
                    campos.append("fontSize")
                if "fonte" in estilo:
                    st["fontFamily"] = estilo["fonte"]
                    campos.append("fontFamily")
                if "link" in estilo:
                    st["link"] = {"url": estilo["link"]}
                    campos.append("link")
                self.req.append(
                    {
                        "updateTextStyle": {
                            "objectId": oid,
                            "textRange": {"type": "FIXED_RANGE", "startIndex": inicio, "endIndex": fim},
                            "style": st,
                            "fields": ",".join(campos),
                        }
                    }
                )
            inicio = fim
        par = {"alignment": alinhar}
        campos = ["alignment"]
        if depois:
            par["spaceBelow"] = {"magnitude": depois, "unit": "PT"}
            campos.append("spaceBelow")
        if linha:
            par["lineSpacing"] = linha
            campos.append("lineSpacing")
        self.req.append(
            {
                "updateParagraphStyle": {
                    "objectId": oid,
                    "textRange": {"type": "ALL"},
                    "style": par,
                    "fields": ",".join(campos),
                }
            }
        )
        if bolinhas:
            self.req.append(
                {
                    "createParagraphBullets": {
                        "objectId": oid,
                        "textRange": {"type": "ALL"},
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE",
                    }
                }
            )
        if meio:
            self.req.append(
                {
                    "updateShapeProperties": {
                        "objectId": oid,
                        "shapeProperties": {"contentAlignment": "MIDDLE"},
                        "fields": "contentAlignment",
                    }
                }
            )
        return oid

    def cabecalho(self, rotulo, titulo):
        self.texto("rotulo", 0.75, 0.42, 8.5, 0.32, rotulo, tam=11, cor=VERDE, negrito=True)
        self.texto("titulo", 0.75, 0.72, 8.5, 0.72, titulo, tam=28, cor=TINTA, fonte=TITULO, negrito=True)

    def cartao(
        self, nome, x, y, w, h, titulo, corpo, cor_titulo=TINTA, fundo=CARTAO, bolinhas=False, tam=14, h_titulo=0.4
    ):
        self.forma(nome, "ROUND_RECTANGLE", x, y, w, h, fundo)
        self.texto(
            nome + "_t",
            x + 0.2,
            y + 0.15,
            w - 0.4,
            h_titulo,
            titulo,
            tam=16,
            cor=cor_titulo,
            fonte=TITULO,
            negrito=True,
        )
        self.texto(
            nome + "_c",
            x + 0.2,
            y + 0.15 + h_titulo,
            w - 0.4,
            h - 0.3 - h_titulo,
            corpo,
            tam=tam,
            cor=CORPO,
            bolinhas=bolinhas,
            depois=6,
            linha=110,
        )


def it(t):
    return (t, {"italico": True})


def montar():
    slides = []

    # 1 — capa
    s = Slide("slide01", AZUL)
    s.texto("escola", 1.0, 0.75, 8, 0.32, "LUMIAR VILA OLÍMPIA  ·  9º ANO  ·  2026", tam=11, cor=LARANJA, negrito=True)
    s.texto(
        "titulo",
        1.0,
        1.8,
        8.2,
        1.45,
        [("Modelagem Matemática de Estratégias de ", {}), it("Day Trade")],
        tam=34,
        cor=BRANCO,
        fonte=TITULO,
        negrito=True,
        linha=95,
    )
    s.texto("sub", 1.0, 3.25, 8.2, 0.42, "Risco, gestão de capital e a influência da economia", tam=16, cor=CLARO2)
    s.forma("linha", "RECTANGLE", 1.0, 3.85, 0.7, 0.05, LARANJA)
    s.texto(
        "nomes",
        1.0,
        4.1,
        8.2,
        0.8,
        [
            ("Autor: ", {"negrito": True, "cor": CLARO}),
            ("Enzo Botto de Barros Marzionna Dudu\n", {}),
            ("Orientador: ", {"negrito": True, "cor": CLARO}),
            ("Prof. Mestre Antônio Francisco da Silva Junior", {}),
        ],
        tam=14,
        cor=CLARO2,
        depois=4,
    )
    slides.append(s)

    # 2 — introdução
    s = Slide("slide02", BRANCO)
    s.cabecalho("ABERTURA", "Introdução e Contextualização")
    s.cartao(
        "cen",
        0.75,
        1.65,
        5.3,
        1.6,
        "Cenário geral do tema",
        [
            it("Day trade"),
            (" é comprar e vender o mesmo ativo no mesmo dia, para aproveitar as variações de preço.", {}),
        ],
    )
    s.cartao(
        "del",
        0.75,
        3.45,
        5.3,
        1.75,
        "Delimitação do assunto",
        "4 estratégias de análise técnica e uma regressão linear, testadas em 9 ativos com 90 dias de dados reais"
        " (12/07 a 09/10/2026).",
    )
    s.texto("num", 6.35, 1.75, 2.9, 1.1, "97%", tam=60, cor=LARANJA, fonte=TITULO, negrito=True, alinhar="CENTER")
    s.texto(
        "num_t",
        6.35,
        2.9,
        2.9,
        1.3,
        [("das pessoas que fizeram ", {}), it("day trade"), (" por mais de 300 dias perderam dinheiro", {})],
        tam=15,
        alinhar="CENTER",
    )
    s.texto("num_f", 6.35, 4.3, 2.9, 0.5, "(CHAGUE; DE-LOSSO; GIOVANNETTI, 2019)", tam=11, cor=CINZA, alinhar="CENTER")
    slides.append(s)

    # 3 — problema e justificativa
    s = Slide("slide03", FUNDO2)
    s.cabecalho("PROBLEMA DE PESQUISA", "Problema de Pesquisa e Justificativa")
    s.forma("barra1", "RECTANGLE", 0.75, 1.7, 0.06, 1.35, LARANJA)
    s.texto("p_t", 1.0, 1.62, 8, 0.4, "PERGUNTA NORTEADORA", tam=16, cor=LARANJA, fonte=TITULO, negrito=True)
    s.texto(
        "p_c",
        1.0,
        2.0,
        8.25,
        1.05,
        [
            ("É possível obter uma margem de lucro constante e segura no ", {}),
            it("day trade"),
            (" usando ferramentas matemáticas?", {}),
        ],
        tam=21,
        cor=TINTA,
        fonte=TITULO,
    )
    s.forma("barra2", "RECTANGLE", 0.75, 3.35, 0.06, 1.3, LARANJA)
    s.texto("j_t", 1.0, 3.27, 8, 0.4, "JUSTIFICATIVA", tam=16, cor=LARANJA, fonte=TITULO, negrito=True)
    s.texto(
        "j_c",
        1.0,
        3.65,
        8.25,
        1.5,
        [
            ("Muita gente compara o ", {}),
            it("day trade"),
            (" a um cassino, mas ele pode ser testado com modelos matemáticos e algoritmos.\n", {}),
            ("Testar uma regra antes de usar dinheiro de verdade protege quem investe (ODS 4 e ODS 8 da ONU).", {}),
        ],
        tam=15,
        bolinhas=True,
        depois=8,
    )
    slides.append(s)

    # 4 — objetivos
    s = Slide("slide04", BRANCO)
    s.cabecalho("ONDE A PESQUISA QUIS CHEGAR", "Objetivos Geral e Específicos")
    s.forma("geral", "ROUND_RECTANGLE", 0.75, 1.65, 8.5, 1.4, VERDE)
    s.texto("geral_t", 0.95, 1.75, 8.1, 0.32, "OBJETIVO GERAL", tam=12, cor="#CCFBF1", negrito=True)
    s.texto(
        "geral_c",
        0.95,
        2.05,
        8.1,
        0.9,
        [
            ("Compreender, com modelagem matemática, como as estratégias de ", {}),
            it("day trade"),
            (" baseadas em análise técnica se relacionam com probabilidade e esperança matemática.", {}),
        ],
        tam=16,
        cor=BRANCO,
        negrito=True,
    )
    s.texto("esp_t", 0.75, 3.25, 8, 0.32, "OBJETIVOS ESPECÍFICOS", tam=12, cor=VERDE, negrito=True)
    s.texto(
        "esp_c",
        0.75,
        3.57,
        8.5,
        1.65,
        [
            ("Transformar as estratégias em regras exatas que um computador consegue seguir (algoritmos);\n", {}),
            ("Testar as regras com dados reais e calcular taxa de acerto, ", {}),
            it("payoff"),
            (", esperança matemática e ", {}),
            it("drawdown"),
            (";\n", {}),
            ("Observar se as estratégias funcionam melhor em momentos calmos ou agitados da economia.", {}),
        ],
        tam=15,
        bolinhas=True,
        depois=6,
    )
    slides.append(s)

    # 5 — referencial teórico
    s = Slide("slide05", FUNDO2)
    s.cabecalho("BASE CONCEITUAL", "Referencial Teórico")
    autores = [
        (
            "Chague, De-Losso e Giovannetti (2019)",
            [it("Day trade"), (" no mini-índice: 97% de quem insistiu por mais de 300 dias perdeu dinheiro.", {})],
        ),
        (
            "Murphy (1999)",
            (
                "Análise técnica: indicadores calculados sobre o preço, como médias móveis e IFR, base das"
                " estratégias testadas."
            ),
        ),
        (
            "Fama (1970)",
            "Mercados eficientes: o preço já reflete as informações, e estudar preços passados não daria vantagem.",
        ),
    ]
    for i, (quem, ideia) in enumerate(autores):
        x = 0.75 + i * 2.9
        s.cartao(f"aut{i + 1}", x, 1.7, 2.7, 3.45, quem, ideia, cor_titulo=VERDE, fundo=BRANCO, h_titulo=0.95)
    slides.append(s)

    # 6 — percurso metodológico
    s = Slide("slide06", BRANCO)
    s.cabecalho("COMO A PESQUISA FOI FEITA (1 DE 2)", "Percurso Metodológico")
    passos = [
        (
            VERDE,
            "Tipo de pesquisa",
            [("Quantitativa e bibliográfica, com simulação em dados do passado (", {}), it("backtest"), (").", {})],
        ),
        (
            VERDE,
            "Coleta de dados",
            "Candles de 9 ativos em 90 dias: Yahoo Finance, Binance, HistData, Bybit e Profit Pro.",
        ),
        (
            LARANJA,
            "Análise dos dados",
            "Regras programadas em Python e testadas no mês de teste (10/09 a 09/10/2026), com e sem custos.",
        ),
    ]
    for i, (cor, nome, corpo) in enumerate(passos):
        x = 0.75 + i * 2.9
        s.forma(f"p{i + 1}", "ROUND_RECTANGLE", x, 1.7, 2.7, 3.45, CARTAO)
        bola = s.forma(f"p{i + 1}_n", "ELLIPSE", x + 0.2, 1.9, 0.5, 0.5, cor)
        s.texto("", 0, 0, 0, 0, str(i + 1), tam=16, cor=BRANCO, negrito=True, alinhar="CENTER", meio=True, sobre=bola)
        s.texto(f"p{i + 1}_t", x + 0.2, 2.55, 2.3, 0.4, nome, tam=16, cor=TINTA, fonte=TITULO, negrito=True)
        s.texto(f"p{i + 1}_c", x + 0.2, 2.95, 2.3, 2.05, corpo, tam=14, linha=110)
    slides.append(s)

    # 7 — as regras testadas
    s = Slide("slide07", FUNDO2)
    s.cabecalho("COMO A PESQUISA FOI FEITA (2 DE 2)", "As 4 Estratégias e a Regressão Linear")
    linhas = [
        ["Abordagem", "Timeframe", "Entrada", "Saída"],
        [
            "ORB",
            "30 min",
            "O preço passa da máxima ou da mínima do 1º candle do dia",
            "Alvo de 3 faixas ou stop no outro lado",
        ],
        ["VWAP", "15 min", "O preço fecha 0,6% longe da VWAP", "Volta à VWAP ou stop de 0,6%"],
        ["IFR", "30 min", "IFR de 14 em 30 ou menos: compra; em 70 ou mais: vende", "IFR volta a 50 ou stop de 1%"],
        ["Médias móveis", "5 min", "A MME de 9 cruza a de 21", "Vira a mão no cruzamento contrário; stop de 1,5%"],
        ["Regressão linear", "1 h", "Prevê alta: compra; prevê queda: vende", "Vira a mão quando a previsão muda"],
    ]
    larg = [1.6, 1.25, 2.95, 2.7]
    tab = "slide07_tabela"
    s.req.append(
        {
            "createTable": {
                "objectId": tab,
                "elementProperties": caixa(s.sid, 0.75, 1.6, sum(larg), 3.1),
                "rows": len(linhas),
                "columns": 4,
            }
        }
    )
    for c, w in enumerate(larg):
        s.req.append(
            {
                "updateTableColumnProperties": {
                    "objectId": tab,
                    "columnIndices": [c],
                    "tableColumnProperties": {"columnWidth": {"magnitude": round(w * EMU), "unit": "EMU"}},
                    "fields": "columnWidth",
                }
            }
        )
    s.req.append(
        {
            "updateTableRowProperties": {
                "objectId": tab,
                "rowIndices": list(range(len(linhas))),
                "tableRowProperties": {"minRowHeight": {"magnitude": round(0.38 * EMU), "unit": "EMU"}},
                "fields": "minRowHeight",
            }
        }
    )
    for r, linha in enumerate(linhas):
        for c, val in enumerate(linha):
            loc = {"rowIndex": r, "columnIndex": c}
            s.req.append({"insertText": {"objectId": tab, "cellLocation": loc, "text": val}})
            s.req.append(
                {
                    "updateTextStyle": {
                        "objectId": tab,
                        "cellLocation": loc,
                        "textRange": {"type": "ALL"},
                        "style": {
                            "fontFamily": TEXTO,
                            "fontSize": {"magnitude": 12, "unit": "PT"},
                            "bold": r == 0 or c == 0,
                            "foregroundColor": {
                                "opaqueColor": {"rgbColor": rgb(VERDE if r == 0 else TINTA if c == 0 else CORPO)}
                            },
                        },
                        "fields": "fontFamily,fontSize,bold,foregroundColor",
                    }
                }
            )
    # itálico nas palavras em inglês da tabela
    for r, c, palavra in [
        (0, 1, "Timeframe"),
        (1, 2, "candle"),
        (1, 3, "stop"),
        (2, 3, "stop"),
        (3, 3, "stop"),
        (4, 3, "stop"),
    ]:
        i0 = linhas[r][c].index(palavra)
        s.req.append(
            {
                "updateTextStyle": {
                    "objectId": tab,
                    "cellLocation": {"rowIndex": r, "columnIndex": c},
                    "textRange": {"type": "FIXED_RANGE", "startIndex": i0, "endIndex": i0 + len(palavra)},
                    "style": {"italic": True},
                    "fields": "italic",
                }
            }
        )
    s.req.append(
        {
            "updateTableCellProperties": {
                "objectId": tab,
                "tableRange": {"location": {"rowIndex": 0, "columnIndex": 0}, "rowSpan": len(linhas), "columnSpan": 4},
                "tableCellProperties": {
                    "tableCellBackgroundFill": {"solidFill": {"color": {"rgbColor": rgb(BRANCO)}}},
                    "contentAlignment": "MIDDLE",
                },
                "fields": "tableCellBackgroundFill.solidFill.color,contentAlignment",
            }
        }
    )
    s.texto(
        "nota",
        0.75,
        5.05,
        8.5,
        0.35,
        "Todas fecham no fim do dia. US$1.000 em cada ativo, com o custo de cada operação descontado.",
        tam=11,
        cor=CINZA,
    )
    slides.append(s)

    # 8 — resultados
    s = Slide("slide08", BRANCO)
    s.cabecalho("O QUE O TESTE MOSTROU", "Com custos, todas perderam dinheiro")
    s.req.append(
        {
            "createImage": {
                "objectId": "slide08_corrida",
                "url": GIF,
                "elementProperties": caixa(s.sid, 0.75, 1.62, 5.6, 2.894),
            }
        }
    )
    numeros = [
        ("−0,7% a −9,2%", LARANJA, "as 5 abordagens, com custos"),
        ("+0,9% a +2,6%", VERDE, "as mesmas, sem custos"),
        ("+20,6%", TINTA, [it("buy and hold"), (" no mesmo mês", {})]),
    ]
    for i, (num, cor, legenda) in enumerate(numeros):
        y = 1.55 + i * 1.1
        s.texto(f"n{i + 1}", 6.6, y, 2.65, 0.5, num, tam=22, cor=cor, fonte=TITULO, negrito=True)
        s.texto(f"n{i + 1}_t", 6.6, y + 0.45, 2.65, 0.6, legenda, tam=14)
    s.texto(
        "fonte",
        0.75,
        4.88,
        8.5,
        0.5,
        "Fonte: gerado pelo Claude (ANTHROPIC, 2026), com dados do Profit Pro, Yahoo Finance, Binance, Bybit e"
        " HistData. Capital somado dos ativos, dia a dia, de 10/09 a 09/10/2026.",
        tam=10,
        cor=CINZA,
    )
    slides.append(s)

    # 9 — considerações finais
    s = Slide("slide09", BRANCO)
    s.cabecalho("CONCLUSÃO", "Considerações Finais")
    s.cartao(
        "resp",
        0.75,
        1.6,
        8.5,
        1.5,
        "Resposta ao problema",
        "Neste teste, não. Sem custos, as abordagens ficaram perto de zero (+0,9% a +2,6%); com custos, todas"
        " perderam (−0,7% a −9,2%), e nenhuma mostrou vantagem estatística real.",
        cor_titulo=VERDE,
        tam=15,
    )
    s.cartao(
        "alc",
        0.75,
        3.3,
        8.5,
        1.9,
        "Alcance dos objetivos",
        [
            ("As 4 estratégias viraram algoritmos em Python e foram testadas em 9 ativos;\n", {}),
            ("Taxa de acerto, ", {}),
            it("payoff"),
            (", esperança, margem de erro e ", {}),
            it("drawdown"),
            (" foram calculados;\n", {}),
            ("Momentos calmos e agitados: só em parte, porque o teste teve um mês, de alta na B3.", {}),
        ],
        cor_titulo=VERDE,
        bolinhas=True,
    )
    slides.append(s)

    # 10 — agradecimento e referências
    s = Slide("slide10", AZUL)
    s.texto(
        "obg",
        0.75,
        0.7,
        8.5,
        0.8,
        "Obrigado pela atenção!",
        tam=38,
        cor=BRANCO,
        fonte=TITULO,
        negrito=True,
        alinhar="CENTER",
    )
    s.texto(
        "disp",
        0.75,
        1.5,
        8.5,
        0.42,
        "Fico à disposição para as considerações e arguições da banca examinadora.",
        tam=15,
        cor=CLARO2,
        alinhar="CENTER",
    )
    s.texto(
        "repo",
        0.75,
        1.95,
        8.5,
        0.38,
        [
            ("Trabalho, código e figuras: ", {}),
            ("github.com/enzobottodudu-pixel/modelagem-matematica-day-trade", {"link": REPO, "cor": LARANJA}),
        ],
        tam=12,
        cor=CLARO2,
        alinhar="CENTER",
    )
    s.forma("refs", "ROUND_RECTANGLE", 1.0, 2.6, 8.0, 2.55, AZUL2)
    s.texto(
        "refs_t",
        1.25,
        2.75,
        7.5,
        0.32,
        "REFERÊNCIAS PRINCIPAIS CITADAS NOS SLIDES (NORMA ABNT)",
        tam=10,
        cor=LARANJA,
        negrito=True,
    )
    n = {"negrito": True, "cor": BRANCO}
    s.texto(
        "refs_c",
        1.25,
        3.07,
        7.5,
        2.0,
        [
            ("CHAGUE, Fernando; DE-LOSSO, Rodrigo; GIOVANNETTI, Bruno. ", {}),
            ("Day trading for a living?", n),
            (" São Paulo: FEA-USP, 2019. (Working Paper Series, n. 2019-47).\n", {}),
            ("FAMA, Eugene F. Efficient capital markets: a review of theory and empirical work. ", {}),
            ("The Journal of Finance", n),
            (", v. 25, n. 2, p. 383-417, 1970.\n", {}),
            ("MURPHY, John J. ", {}),
            ("Technical analysis of the financial markets", n),
            (
                (
                    ": a comprehensive guide to trading methods and applications. New York: New York Institute"
                    " of Finance, 1999."
                ),
                {},
            ),
        ],
        tam=10,
        cor=CLARO,
        depois=8,
    )
    slides.append(s)
    return slides


def main():
    slides = montar()
    lotes = [slides[0:3], slides[3:5], slides[5:7], slides[7:10]]
    for i, lote in enumerate(lotes, start=1):
        reqs = [r for s in lote for r in s.req]
        (PASTA / f"lote{i}.json").write_text(
            json.dumps({"requests": reqs}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
        print(f"lote{i}.json: {len(lote)} slides, {len(reqs)} pedidos")


if __name__ == "__main__":
    main()
