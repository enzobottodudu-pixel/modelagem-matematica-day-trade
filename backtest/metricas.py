"""
MÉTRICAS — o "boletim" de uma estratégia, calculado a partir do caderno de operações do motor.

São as mesmas fórmulas dos programas do Enzo no capítulo 4 do TCC:
  4.2 taxa de acerto e payoff      -> "fórmula taxa de acerto.py" e "Formula payoff.py"
  4.3 esperança matemática         -> "Esperança matemática.py"
  4.4 taxa de acerto mínima        -> "taxa de acerto minima.py"
  4.6 margem de erro da média      -> "margem de erro.py"
  4.7 drawdown                     -> "drawdown.py"

Aqui os números não são inventados: vêm do caderno (a lista de operações que o motor devolve).
Cada resultado está em %, já com o custo.
"""

import statistics


def boletim(operacoes, capital_inicial=100.0):
    """Calcula todas as métricas de uma lista de operações e devolve um dicionário."""
    resultados = [op["resultado"] for op in operacoes]  # o resultado (%) de cada operação
    n = len(resultados)
    if n == 0:
        return {"operacoes": 0}

    # 4.2 TAXA DE ACERTO: operações com lucro ÷ operações totais
    lucros = [r for r in resultados if r > 0]
    prejuizos = [-r for r in resultados if r <= 0]  # sem o sinal de menos, como no TCC
    taxa_de_acerto = len(lucros) / n
    taxa_de_erro = 1 - taxa_de_acerto

    # 4.2 PAYOFF: ganho médio ÷ perda média
    ganho_medio = sum(lucros) / len(lucros) if lucros else 0.0
    perda_media = sum(prejuizos) / len(prejuizos) if prejuizos else 0.0
    payoff = ganho_medio / perda_media if perda_media > 0 else float("inf")

    # 4.3 ESPERANÇA MATEMÁTICA: E = acerto × ganho médio − erro × perda média  (em % por operação)
    esperanca = taxa_de_acerto * ganho_medio - taxa_de_erro * perda_media

    # 4.4 TAXA DE ACERTO MÍNIMA: 1 ÷ (1 + payoff)
    acerto_minimo = 1 / (1 + payoff)

    # 4.6 MARGEM DE ERRO DA MÉDIA: 2 × desvio-padrão ÷ √n  (cerca de 95% de confiança)
    desvio_padrao = statistics.stdev(resultados) if n > 1 else 0.0
    margem_de_erro = 2 * desvio_padrao / n**0.5
    faixa = (esperanca - margem_de_erro, esperanca + margem_de_erro)

    # 4.7 DRAWDOWN: a conta começa com 100 e cada operação usa o capital todo
    #     (comprou com R$100 e ganhou 2% -> R$102; a próxima operação já começa com R$102)
    capital = [capital_inicial]
    for r in resultados:
        capital.append(capital[-1] * (1 + r / 100))
    topo, drawdown_maximo = capital[0], 0.0
    for valor in capital:
        topo = max(topo, valor)  # o maior valor até agora (o "topo acumulado" do drawdown.py)
        drawdown_maximo = min(drawdown_maximo, (valor - topo) / topo * 100)

    return {
        "operacoes": n,
        "taxa_de_acerto": taxa_de_acerto * 100,  # em %
        "ganho_medio": ganho_medio,
        "perda_media": perda_media,
        "payoff": payoff,
        "esperanca": esperanca,
        "acerto_minimo": acerto_minimo * 100,  # em %
        "desvio_padrao": desvio_padrao,
        "margem_de_erro": margem_de_erro,
        "faixa_da_esperanca": faixa,
        "tem_vantagem": faixa[0] > 0,  # a faixa inteira acima de zero (seção 4.6)
        "capital": capital,
        "retorno_total": (capital[-1] / capital_inicial - 1) * 100,
        "drawdown_maximo": drawdown_maximo,
    }


def mostrar_boletim(b, titulo):
    """Escreve o boletim na tela, em português."""
    print(titulo)
    if b["operacoes"] == 0:
        print("  nenhuma operação")
        return
    print(f"  operações ............ {b['operacoes']}")
    print(f"  taxa de acerto ....... {b['taxa_de_acerto']:.1f}%   (mínima para empatar: {b['acerto_minimo']:.1f}%)")
    print(f"  ganho médio .......... {b['ganho_medio']:+.3f}%   perda média: {b['perda_media']:.3f}%")
    print(f"  payoff ............... {b['payoff']:.2f}")
    print(f"  esperança (E) ........ {b['esperanca']:+.3f}% por operação")
    print(
        f"  margem de erro ....... ±{b['margem_de_erro']:.3f}%  -> E entre {b['faixa_da_esperanca'][0]:+.3f}% "
        f"e {b['faixa_da_esperanca'][1]:+.3f}%"
    )
    print(f"  tem vantagem? ........ {'SIM' if b['tem_vantagem'] else 'NÃO dá para afirmar (a faixa passa pelo zero)'}")
    print(f"  retorno total ........ {b['retorno_total']:+.2f}%")
    print(f"  drawdown máximo ...... {b['drawdown_maximo']:.2f}%")


if __name__ == "__main__":
    # 1) Teste com 10 operações inventadas, para conferir de cabeça
    inventadas = [{"resultado": r} for r in [2, -1, 2, -1, -1, 2, -1, 2, -1, -1]]
    mostrar_boletim(boletim(inventadas), "TESTE: 10 operações inventadas (4 ganham 2%, 6 perdem 1%)")

    # 2) O caderno de verdade do pedaço 8: PETR4, 5 min, treino inteiro, regra de teste
    from dados import carregar, treino_e_teste
    from motor import simular_periodo

    treino, _ = treino_e_teste(carregar("PETR4", "5min"))
    treino = treino.copy()
    treino["sinal"] = ["compra" if p else "nada" for p in ~treino["dia"].duplicated()]
    print()
    mostrar_boletim(
        boletim(simular_periodo("PETR4", "5min", treino)),
        "PETR4, 5 min, treino (regra de teste: compra no 1º candle de cada dia)",
    )
