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
-- Hash da senha "123456": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhgJgxQxG3KqP9ZzQl1Qzu
WITH tenant_data AS (
    SELECT id as tenant_id FROM tenants WHERE name = 'Empresa Exemplo' LIMIT 1
)
INSERT INTO operators (id, tenant_id, name, email, password_hash, is_active, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    tenant_data.tenant_id,
    'Operador Admin',
    'admin@exemplo.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhgJgxQxG3KqP9ZzQl1Qzu',
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