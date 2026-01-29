# leitura de cpf

def apenas_numeros(valor: str) -> str:
    return ''.join(filter(str.isdigit, valor))


def validar_cpf(cpf: str) -> bool:
    cpf = apenas_numeros(cpf)

    # precisa ter 11 dígitos
    if len(cpf) != 11:
        return False

    # evita cpf repetido tipo 11111111111 e também evita cpf vazio
    if cpf == cpf[0] * len(cpf):
        return False

    # calcula os 2 dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(0, i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False

    return True


def formato_cpf(cpf: str) -> str:
    cpf = apenas_numeros(cpf)
    if len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
