from validators.cpf import validar_cpf, formato_cpf
from validators.cnpj import validar_cnpj, formato_cnpj


def apenas_numeros(valor: str) -> str:
    return ''.join(filter(str.isdigit, valor))


def validar_documento(documento: str) -> dict:
    numero = apenas_numeros(documento)

    if len(numero) == 11:
        valido = validar_cpf(numero)
        return {
            "type": "CPF",
            "input": documento,
            "formatted": formato_cpf(numero),
            "valid": valido,
            "message": "CPF válido" if valido else "CPF inválido",
        }

    if len(numero) == 14:
        valido = validar_cnpj(numero)
        return {
            "type": "CNPJ",
            "input": documento,
            "formatted": formato_cnpj(numero),
            "valid": valido,
            "message": "CNPJ válido" if valido else "CNPJ inválido",
        }

    return {
        "type": "UNKNOWN",
        "input": documento,
        "formatted": documento,
        "valid": False,
        "message": "Documento deve ter 11 (CPF) ou 14 (CNPJ) dígitos",
    }
