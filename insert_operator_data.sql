-- Script para inserir operador de teste
-- Operador associado ao tenant: RecoveryTruck Dev (ID: 7f02a566-2406-436d-b10d-90ecddd3fe2d)

-- 1. Verificar se o tenant existe
SELECT 'Verificando tenant RecoveryTruck Dev:' as info;
SELECT id, name, cnpj, is_active 
FROM tenants 
WHERE id = '7f02a566-2406-436d-b10d-90ecddd3fe2d';

-- 2. Inserir operador para o tenant RecoveryTruck Dev
-- Senha: "123456" (hash bcrypt)
INSERT INTO operators (id, tenant_id, name, email, password_hash, is_active, created_at, updated_at) 
VALUES (
    gen_random_uuid(),
    '7f02a566-2406-436d-b10d-90ecddd3fe2d', -- ID correto do tenant
    'Operador Teste',
    'operador@recoverytruck.dev',
    '$2b$12$CO4AsLnoRO.F624pMIMz6OjdwH99BBEhCDjYR8/ryM/NsRDw0KqBO', -- Hash correto
    true,
    NOW(),
    NOW()
) ON CONFLICT (email) DO UPDATE 
SET 
    password_hash = '$2b$12$CO4AsLnoRO.F624pMIMz6OjdwH99BBEhCDjYR8/ryM/NsRDw0KqBO', -- Hash correto
    updated_at = NOW();

-- 3. Verificar se o operador foi inserido corretamente
SELECT 'Verificando operador inserido:' as info;
SELECT id, name, email, tenant_id, is_active
FROM operators
WHERE email = 'operador@recoverytruck.dev';

-- 4. Listar todos os operadores para o tenant de desenvolvimento
SELECT 'Listando todos os operadores do tenant:' as info;
SELECT o.id, o.name, o.email, o.is_active, t.name as tenant_name
FROM operators o
JOIN tenants t ON o.tenant_id = t.id
WHERE o.tenant_id = '7f02a566-2406-436d-b10d-90ecddd3fe2d'
ORDER BY o.created_at;

-- 5. Contar total de operadores
SELECT 
    'Total de operadores:' as info,
    count(*) as total
FROM operators; 