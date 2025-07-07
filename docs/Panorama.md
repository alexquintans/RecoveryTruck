## 🏗️ Panorama Geral do Projeto Totem

### **O que é o Sistema**
Este é um **sistema de autoatendimento** (totem) para filas e pagamentos. É um projeto bem robusto com:
- Sistema de filas com tickets
- Integração com múltiplos terminais de pagamento (Sicredi, Stone, PagBank, etc.)
- Painel para operadores
- Interface para clientes no totem
- Monitoramento completo

### **🏢 Arquitetura do Sistema**

**1. Backend (Python/FastAPI)** - `apps/api/`
- API REST completa
- Integração com bancos (PostgreSQL)
- Sistema de pagamentos
- Impressão de tickets
- WebSockets para comunicação em tempo real

**2. Frontend - 2 aplicações React:**
- **Totem Client** (`apps/totem-client/`) - Interface para clientes
- **Panel Client** (`apps/panel-client/`) - Painel para operadores

**3. Monitoramento completo:**
- Prometheus (métricas)
- Grafana (dashboards)
- Jaeger (tracing)
- AlertManager (alertas)

### **🐳 Docker e Docker Compose**

O `docker-compose.yml` configura toda a infraestrutura:

```bash
# Para subir todo o sistema:
docker-compose up --build

# Para parar:
docker-compose down
```

**Serviços que sobem:**
- `api`: Backend FastAPI (porta 8000)
- `panel`: Painel do operador (porta 5173)
- `totem`: Interface do totem (porta 5174)
- `db`: PostgreSQL (porta 5433)
- `prometheus`: Métricas (porta 9090)
- `grafana`: Dashboards (porta 3000)
- `jaeger`: Tracing (porta 16686)

### **📦 PNPM e Workspace**

O projeto usa **monorepo** com pnpm workspace:

```yaml
# pnpm-workspace.yaml
packages:
  - 'apps/*'      # totem-client, panel-client
  - 'packages/*'  # ui, hooks, utils (compartilhados)
```

**Comandos úteis:**
```bash
# Instalar todas as dependências
pnpm install

# Rodar aplicação específica
pnpm --filter panel-client dev
pnpm --filter totem-client dev

# Rodar o backend (se tiver script configurado)
pnpm --filter api dev
```

### **🚀 Como Rodar o Projeto**

**Opção 1: Docker (Mais fácil)**
```bash
# Na raiz do projeto
docker-compose up --build
```

**Opção 2: Desenvolvimento local**
```bash
# Backend
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend - Painel
cd apps/panel-client
pnpm install
pnpm dev --host --port 5173

# Frontend - Totem
cd apps/totem-client
pnpm install
pnpm dev --host --port 5174
```

### **📁 Estrutura dos Packages**

```
packages/
├── ui/         # Componentes React compartilhados
├── hooks/      # React hooks compartilhados
└── utils/      # Utilitários compartilhados
```

Estes packages são reutilizados entre totem-client e panel-client.

### **🔧 Configurações Importantes**

**Variáveis de ambiente:**
- `apps/api/backend.env` - Configuração do backend
- `apps/*/frontend.env` - Configuração dos frontends

**Configurações de exemplo em `config/`:**
- Terminais de pagamento
- Impressoras
- Notificações
- Multi-tenant

### **📊 Monitoramento**

Depois de rodar, você pode acessar:
- **API**: http://localhost:8000
- **Painel**: http://localhost:5173
- **Totem**: http://localhost:5174
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686

### **💡 Dicas para Começar**

1. **Use Docker primeiro** - É mais fácil para entender o sistema completo
2. **Verifique o health check**: http://localhost:8000/health
3. **Explore a documentação** em `docs/` - tem muita coisa útil
4. **Use o Makefile** para comandos rápidos:
   ```bash
   make up    # docker-compose up --build
   make down  # docker-compose down
   ```

O projeto está muito bem estruturado e documentado! É um sistema comercial completo com boas práticas. Quer que eu explique alguma parte específica em mais detalhes?