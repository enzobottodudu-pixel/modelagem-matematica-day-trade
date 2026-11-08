# ---------------------------------------- os dados e os indicadores
def volume_do_yahoo(ativo):
    """SPY e NQ: o HistData não tem volume; usa o volume do Yahoo
    (15 min), que existe só no mês de teste."""
    y = pd.read_csv(
        TCC / "Dados do Yahoo Finance" / ativo / f"{ativo}_15min.csv"
    )
    y["Data"] = pd.to_datetime(y["Data"], utc=True).dt.tz_convert(FUSO[ativo])
    return y.set_index("Data")["Volume"]


def candles_do_teste(ativo, estrategia):
    """Abre os candles, calcula o indicador da estratégia com todo o
    histórico e devolve só o mês de teste."""
    c = carregar(ativo, TIMEFRAME[estrategia]).copy()
    if estrategia == "VWAP":
        if ativo == "EURUSD":
            # câmbio não tem volume centralizado: não há VWAP
            return None
        if ativo in ("SPY", "NQ"):
            c["Volume"] = volume_do_yahoo(ativo).reindex(c.index).fillna(0)
        # preço típico, como na Figura 34
        tipico = (c["High"] + c["Low"] + c["Close"]) / 3
        soma_pv = (tipico * c["Volume"]).groupby(c["dia"]).cumsum()
        soma_v = c["Volume"].groupby(c["dia"]).cumsum()
        # recomeça todo dia
        c["vwap"] = (soma_pv / soma_v).where(soma_v > 0)
    if estrategia == "IFR":
        variacao = c["Close"].diff()
        altas = variacao.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
        quedas = (
            (-variacao.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        )
        c["ifr"] = 100 - 100 / (1 + altas / quedas)
    if estrategia == "Médias":
        c["acima"] = (
            c["Close"].ewm(span=9, adjust=False).mean()
            > c["Close"].ewm(span=21, adjust=False).mean()
        )
    _, teste = treino_e_teste(c)
    return teste


# ---------------------------------------- peças iguais para as 4 estratégias
def bateu(lado, k, stop, alvo):
    """Stop e alvo dentro do candle, pela máxima e pela mínima.
    Os dois no mesmo candle: conta o stop.
    Se o candle já abre depois do nível (gap), sai na abertura."""
    if lado == "compra":
        if stop is not None and k.Low <= stop:
            return min(k.Open, stop), "stop"
        if alvo is not None and k.High >= alvo:
            return max(k.Open, alvo), "alvo"
    else:
        if stop is not None and k.High >= stop:
            return max(k.Open, stop), "stop"
        if alvo is not None and k.Low <= alvo:
            return min(k.Open, alvo), "alvo"
    return None


def abrir(lado, preco, k, i, stop, alvo=None):
    return {"lado": lado, "entrada": preco, "hora_entrada": k.Index,
            "i": i, "stop": stop, "alvo": alvo}


def fechar(op, preco, motivo, k, ativo, timeframe):
    """Fecha a operação: resultado = retorno − custo, em %."""
    custo = custo_percentual(ativo, op["entrada"], timeframe)
    if op["lado"] == "compra":
        retorno = (preco - op["entrada"]) / op["entrada"] * 100
    else:
        retorno = (op["entrada"] - preco) / op["entrada"] * 100
    return {"lado": op["lado"], "hora_entrada": op["hora_entrada"],
            "entrada": op["entrada"], "hora_saida": k.Index,
            "saida": preco, "motivo": motivo, "custo": custo,
            "sem_custo": retorno, "resultado": retorno - custo}


# ---------------------------------------- as 4 estratégias, um dia por vez
def orb(dia, ativo, tf):
    ops, aberta, operou = [], None, False
    # a faixa de abertura: o 1º candle do dia
    maxima, minima = dia[0].High, dia[0].Low
    faixa = maxima - minima
    if faixa <= 0:
        return ops
    for i, k in enumerate(dia[1:], start=1):
        if aberta is None and not operou and i < len(dia) - 1:
            sobe, desce = k.High > maxima, k.Low < minima
            if sobe or desce:
                # rompeu os dois lados no mesmo candle:
                # vale o lado mais perto da abertura
                if sobe and desce:
                    sobe = abs(k.Open - maxima) <= abs(k.Open - minima)
                lado = "compra" if sobe else "venda"
                preco = max(k.Open, maxima) if sobe else min(k.Open, minima)
                alvo = preco + 3 * faixa if sobe else preco - 3 * faixa
                stop = minima if sobe else maxima
                aberta, operou = abrir(lado, preco, k, i, stop, alvo), True
                # no candle da entrada, só o stop (o caso pior)
                saida = bateu(lado, k, aberta["stop"], None)
                if saida:
                    ops.append(fechar(aberta, *saida, k, ativo, tf))
                    aberta = None
                continue
        if aberta is not None:
            saida = bateu(aberta["lado"], k, aberta["stop"], aberta["alvo"])
            if saida:
                ops.append(fechar(aberta, *saida, k, ativo, tf))
                aberta = None
    if aberta is not None:
        ops.append(fechar(aberta, dia[-1].Close, "fim do dia", dia[-1],
                          ativo, tf))
    return ops


def vwap(dia, ativo, tf):
    ops, aberta = [], None
    for i, k in enumerate(dia):
        saiu = False
        if aberta is not None and i > aberta["i"]:
            # a VWAP que já era conhecida quando o candle começou
            alvo = dia[i - 1].vwap
            saida = bateu(aberta["lado"], k, aberta["stop"], alvo)
            if saida:
                ops.append(fechar(aberta, *saida, k, ativo, tf))
                aberta, saiu = None, True
        if (aberta is None and not saiu and i < len(dia) - 1
                and not np.isnan(k.vwap)):
            distancia = k.Close / k.vwap - 1
            if distancia >= 0.006:
                aberta = abrir("venda", k.Close, k, i, k.Close * 1.006)
            elif distancia <= -0.006:
                aberta = abrir("compra", k.Close, k, i, k.Close * 0.994)
    if aberta is not None:
        ops.append(fechar(aberta, dia[-1].Close, "fim do dia", dia[-1],
                          ativo, tf))
    return ops


def ifr(dia, ativo, tf):
    ops, aberta = [], None
    for i, k in enumerate(dia):
        saiu = False
        if aberta is not None and i > aberta["i"]:
            saida = bateu(aberta["lado"], k, aberta["stop"], None)
            if saida is None and (
                    (aberta["lado"] == "compra" and k.ifr >= 50)
                    or (aberta["lado"] == "venda" and k.ifr <= 50)):
                saida = (k.Close, "alvo (IFR voltou a 50)")
            if saida:
                ops.append(fechar(aberta, *saida, k, ativo, tf))
                aberta, saiu = None, True
        if aberta is None and not saiu and i < len(dia) - 1:
            if k.ifr <= 30:
                aberta = abrir("compra", k.Close, k, i, k.Close * 0.99)
            elif k.ifr >= 70:
                aberta = abrir("venda", k.Close, k, i, k.Close * 1.01)
    if aberta is not None:
        ops.append(fechar(aberta, dia[-1].Close, "fim do dia", dia[-1],
                          ativo, tf))
    return ops


def medias(dia, ativo, tf):
    ops, aberta = [], None
    for i, k in enumerate(dia):
        if aberta is not None and i > aberta["i"]:
            saida = bateu(aberta["lado"], k, aberta["stop"], None)
            if saida:
                ops.append(fechar(aberta, *saida, k, ativo, tf))
                aberta = None
        # as médias cruzaram neste candle
        if i > 0 and k.acima != dia[i - 1].acima and i < len(dia) - 1:
            lado = "compra" if k.acima else "venda"
            # cruzamento contrário: vira a mão
            if aberta is not None and aberta["lado"] != lado:
                ops.append(fechar(aberta, k.Close, "cruzamento contrário",
                                  k, ativo, tf))
                aberta = None
            if aberta is None:
                stop = k.Close * (0.985 if lado == "compra" else 1.015)
                aberta = abrir(lado, k.Close, k, i, stop)
    if aberta is not None:
        ops.append(fechar(aberta, dia[-1].Close, "fim do dia", dia[-1],
                          ativo, tf))
    return ops


REGRA = {"ORB": orb, "VWAP": vwap, "IFR": ifr, "Médias": medias}
