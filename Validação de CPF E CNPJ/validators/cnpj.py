# leitura de cnpj

def apenas_numeros(valor: str) -> str:
    return ''.join(filter(str.isdigit, valor))


def validar_cnpj(cnpj: str) -> bool:
    cnpj = apenas_numeros(cnpj)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * len(cnpj):
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1

    def calcular_digito(base: str, pesos: list[int]) -> int:
        soma = sum(int(d) * p for d, p in zip(base, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    d1 = calcular_digito(cnpj[:12], pesos1)
    d2 = calcular_digito(cnpj[:12] + str(d1), pesos2)

    return (d1 == int(cnpj[12])) and (d2 == int(cnpj[13]))


def formato_cnpj(cnpj: str) -> str:
    cnpj = apenas_numeros(cnpj)
    if len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
