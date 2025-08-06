#!/usr/bin/env python3
"""
Teste para verificar se o CPF 43421731829 é válido
"""

import re

def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF seguindo algoritmo oficial brasileiro
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Calcula segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica se os dígitos calculados são iguais aos do CPF
    result = cpf[-2:] == f"{digito1}{digito2}"
    
    print(f"CPF: {cpf}")
    print(f"Digito1: {digito1}")
    print(f"Digito2: {digito2}")
    print(f"CPF[-2:]: {cpf[-2:]}")
    print(f"Expected: {digito1}{digito2}")
    print(f"Result: {result}")
    
    return result

def normalize_cpf(cpf: str) -> str:
    """
    Normaliza CPF removendo formatação
    """
    return re.sub(r'[^0-9]', '', cpf)

if __name__ == "__main__":
    # Testar CPF original
    original_cpf = "434.217.318-29"
    print(f"CPF original: {original_cpf}")
    
    # Normalizar
    normalized_cpf = normalize_cpf(original_cpf)
    print(f"CPF normalizado: {normalized_cpf}")
    
    # Validar
    is_valid = validate_cpf(normalized_cpf)
    print(f"CPF válido: {is_valid}")
    
    # Testar outros CPFs conhecidos
    test_cpfs = [
        "123.456.789-09",  # CPF válido conhecido
        "111.111.111-11",  # CPF inválido (todos iguais)
        "123.456.789-00",  # CPF inválido
    ]
    
    print("\nTestando outros CPFs:")
    for cpf in test_cpfs:
        normalized = normalize_cpf(cpf)
        valid = validate_cpf(normalized)
        print(f"{cpf} -> {normalized} -> {valid}") 