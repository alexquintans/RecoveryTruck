-- Script para inserir dados de teste na tabela tenant
-- Execute este script no seu banco de dados PostgreSQL

-- 1. Inserir tenant principal para testes
INSERT INTO tenants (id, name, cnpj, is_active, created_at, updated_at) 
VALUES (
    gen_random_uuid(),
    'RecoveryTruck Premium',
    '12345678000199',
    true,
    NOW(),
    NOW()
) ON CONFLICT (cnpj) DO NOTHING;

-- 2. Inserir tenant secundário para testes
INSERT INTO tenants (id, name, cnpj, is_active, created_at, updated_at) 
VALUES (
    gen_random_uuid(),
    'RecoveryTruck Basic',
    '98765432000188',
    true,
    NOW(),
    NOW()
) ON CONFLICT (cnpj) DO NOTHING;

-- 3. Inserir tenant de desenvolvimento
INSERT INTO tenants (id, name, cnpj, is_active, created_at, updated_at) 
VALUES (
    gen_random_uuid(),
    'RecoveryTruck Dev',
    '11111111000111',
    true,
    NOW(),
    NOW()
) ON CONFLICT (cnpj) DO NOTHING;

-- 4. Verificar os dados inseridos
SELECT 'Tenants inseridos:' as info;
SELECT 
    id, 
    name, 
    cnpj, 
    is_active, 
    created_at 
FROM tenants 
ORDER BY created_at;

-- 5. Contar total de tenants
SELECT 
    'Total de tenants:' as info,
    COUNT(*) as total
FROM tenants; 