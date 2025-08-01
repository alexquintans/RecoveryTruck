#!/usr/bin/env python3
"""
Script para gerar hash correto da senha usando bcrypt
"""

import bcrypt
import sys

def generate_password_hash(password: str) -> str:
    """Gera hash bcrypt da senha."""
    # Converter senha para bytes
    password_bytes = password.encode('utf-8')
    
    # Gerar salt e hash
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    
    # Retornar como string
    return password_hash.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha está correta."""
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)

if __name__ == "__main__":
    # Senha que queremos usar
    password = "123456"
    
    # Gerar hash
    password_hash = generate_password_hash(password)
    
    print(f"Senha: {password}")
    print(f"Hash: {password_hash}")
    print()
    
    # Testar verificação
    is_valid = verify_password(password, password_hash)
    print(f"Verificação: {'✅ Válida' if is_valid else '❌ Inválida'}")
    print()
    
    # Gerar SQL atualizado
    sql_template = f"""
-- Script para recriar dados básicos
-- Execute no pgAdmin ou via comando

-- Inserir tenant de exemplo
INSERT INTO tenants (id, name, cnpj, is_active, created_at, updated_at) 
VALUES (
    gen_random_uuid(),
    'Empresa Exemplo',
    '12345678000199',
    true,
    NOW(),
    NOW()
) ON CONFLICT DO NOTHING;

-- Inserir operador de exemplo (password = "123456")
-- Hash da senha "123456": {password_hash}
WITH tenant_data AS (
    SELECT id as tenant_id FROM tenants WHERE name = 'Empresa Exemplo' LIMIT 1
)
INSERT INTO operators (id, tenant_id, name, email, password_hash, is_active, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    tenant_data.tenant_id,
    'Operador Admin',
    'admin@exemplo.com',
    '{password_hash}',
    true,
    NOW(),
    NOW()
FROM tenant_data
ON CONFLICT DO NOTHING;

-- Verificar dados inseridos
SELECT 'Tenants:' as info;
SELECT id, name, cnpj FROM tenants;

SELECT 'Operadores:' as info;
SELECT id, name, email, tenant_id FROM operators;
"""
    
    print("=== SQL ATUALIZADO ===")
    print(sql_template)
    
    # Salvar no arquivo
    with open('seed_data_updated.sql', 'w', encoding='utf-8') as f:
        f.write(sql_template)
    
    print("✅ SQL salvo em 'seed_data_updated.sql'") 