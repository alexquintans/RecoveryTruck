# 📝 Como Inserir Dados na Tabela Tenant

Este guia explica como adicionar dados de teste na tabela `tenant` do sistema Totem.

## 🏗️ Estrutura da Tabela Tenant

A tabela `tenant` possui os seguintes campos:

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    cnpj VARCHAR(14) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🚀 Métodos para Inserir Dados

### 1. **Script SQL Direto** (Recomendado)

Use o arquivo `insert_tenant_data.sql`:

```bash
# Conecte ao PostgreSQL
psql -h localhost -p 5432 -U postgres -d totem

# Execute o script
\i insert_tenant_data.sql
```

**Ou via linha de comando:**
```bash
psql -h localhost -p 5432 -U postgres -d totem -f insert_tenant_data.sql
```

### 2. **Script Python** (Alternativo)

Use o arquivo `insert_tenant_script.py`:

```bash
# Certifique-se de estar no diretório raiz do projeto
cd /caminho/para/ProjetoTotem

# Execute o script Python
python insert_tenant_script.py
```

### 3. **Via Docker Compose** (Se estiver usando Docker)

```bash
# Inicie os containers
docker-compose up -d

# Execute o script SQL no container do banco
docker-compose exec db psql -U postgres -d totem -f /app/insert_tenant_data.sql
```

## 📋 Dados que Serão Inseridos

O script irá inserir 3 tenants de exemplo:

| Nome | CNPJ | Status |
|------|------|--------|
| RecoveryTruck Premium | 12345678000199 | Ativo |
| RecoveryTruck Basic | 98765432000188 | Ativo |
| RecoveryTruck Dev | 11111111000111 | Ativo |

## ⚙️ Configuração do Ambiente

### Variáveis de Ambiente Necessárias

Crie um arquivo `.env` na raiz do projeto:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/totem
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=totem
```

### Verificar Conexão

Antes de executar os scripts, verifique se o banco está acessível:

```bash
# Teste de conexão
psql -h localhost -p 5432 -U postgres -d totem -c "SELECT version();"
```

## 🔧 Pré-requisitos

1. **PostgreSQL rodando** na porta 5432 (ou configurada)
2. **Banco de dados `totem` criado**
3. **Tabelas criadas** (execute as migrações primeiro)
4. **Usuário `postgres`** com permissões adequadas

### Executar Migrações (se necessário)

```bash
# Navegue para o diretório da API
cd apps/api

# Execute as migrações
alembic upgrade head
```

## ✅ Verificação dos Dados

Após executar o script, verifique se os dados foram inseridos:

```sql
-- Ver todos os tenants
SELECT id, name, cnpj, is_active, created_at 
FROM tenants 
ORDER BY created_at;

-- Contar total
SELECT COUNT(*) as total_tenants FROM tenants;
```

## 🐛 Solução de Problemas

### Erro: "connection refused"
- Verifique se o PostgreSQL está rodando
- Confirme a porta e host nas configurações

### Erro: "database does not exist"
- Crie o banco: `CREATE DATABASE totem;`

### Erro: "table does not exist"
- Execute as migrações: `alembic upgrade head`

### Erro: "permission denied"
- Verifique as credenciais do usuário PostgreSQL
- Confirme se o usuário tem permissões no banco

## 📚 Próximos Passos

Após inserir os tenants, você pode:

1. **Criar operadores** para cada tenant
2. **Configurar serviços** por tenant
3. **Adicionar equipamentos** (totens, painéis)
4. **Testar a aplicação** com os dados inseridos

### Exemplo: Criar Operador

```sql
-- Inserir operador para o tenant Premium
INSERT INTO operators (id, tenant_id, name, email, password_hash, is_active)
SELECT 
    gen_random_uuid(),
    t.id,
    'Operador Admin',
    'admin@recoverytruck.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhgJgxQxG3KqP9ZzQl1Qzu', -- senha: 123456
    true
FROM tenants t 
WHERE t.name = 'RecoveryTruck Premium';
```

## 🔗 Links Úteis

- [Documentação do PostgreSQL](https://www.postgresql.org/docs/)
- [Guia de Migrações Alembic](https://alembic.sqlalchemy.org/)
- [Configuração do Docker Compose](./docker-compose.yml) 