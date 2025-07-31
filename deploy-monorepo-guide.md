# 🚀 Deploy Monorepo - PNPM + Docker

## 🏗️ Estrutura do Projeto

```
totem-app/
├── apps/
│   ├── api/           # FastAPI Backend
│   ├── totem-client/  # React Frontend
│   └── panel-client/  # React Admin Panel
├── packages/
│   ├── utils/         # Utilitários compartilhados
│   └── hooks/         # Hooks React compartilhados
├── pnpm-workspace.yaml
├── package.json
└── docker-compose.yml
```

## 🔧 Configurações Específicas

### **1. Railway (API) - Monorepo**

#### Dockerfile Otimizado:
```dockerfile
# Copia workspace pnpm
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./

# Copia packages compartilhados
COPY packages/ ./packages/

# Copia apps
COPY apps/ ./apps/
```

#### Variáveis de Ambiente:
```env
PYTHONPATH=/app
ENVIRONMENT=production
DATABASE_URL=postgresql://...
JWT_SECRET=...
```

### **2. Vercel (Frontend) - Monorepo**

#### vercel.json:
```json
{
  "buildCommand": "pnpm install && pnpm --filter totem-client build",
  "installCommand": "pnpm install",
  "outputDirectory": "apps/totem-client/dist"
}
```

#### package.json do totem-client:
```json
{
  "name": "totem-client",
  "dependencies": {
    "@totem/utils": "workspace:*",
    "@totem/hooks": "workspace:*"
  }
}
```

## 🚀 Deploy Step-by-Step

### **Fase 1: Railway (API)**

1. **Conectar GitHub** no Railway
2. **Selecionar repositório**
3. **Railway detectará**:
   - `railway.json` na raiz
   - `apps/api/Dockerfile`
4. **Adicionar PostgreSQL**:
   - "New Service" → "Database" → "PostgreSQL"
5. **Configurar variáveis**:
   ```env
   DATABASE_URL=postgresql://[railway-db-url]
   JWT_SECRET=sua_chave_secreta
   ENVIRONMENT=production
   CORS_ORIGINS=https://seu-frontend.vercel.app
   ```

### **Fase 2: Vercel (Frontend)**

1. **Conectar GitHub** no Vercel
2. **Selecionar repositório**
3. **Vercel detectará**:
   - `apps/totem-client/vercel.json`
   - `apps/totem-client/package.json`
4. **Build automático** com pnpm workspace
5. **Deploy automático**

## 🔍 Troubleshooting Monorepo

### **Problemas Comuns:**

1. **Dependências não encontradas**:
   ```bash
   # Verificar se packages estão sendo copiados
   ls -la packages/
   ```

2. **Build falha no Vercel**:
   ```json
   // vercel.json
   {
     "buildCommand": "pnpm install && pnpm --filter totem-client build"
   }
   ```

3. **Imports não funcionam**:
   ```python
   # apps/api/app.py
   import sys
   sys.path.append('/app')
   ```

4. **PNPM cache issues**:
   ```bash
   # Limpar cache
   pnpm store prune
   ```

## 📦 Otimizações para Monorepo

### **1. Docker Multi-stage (Opcional)**
```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./
COPY packages/ ./packages/
COPY apps/totem-client/ ./apps/totem-client/
RUN pnpm install --frozen-lockfile
RUN pnpm --filter totem-client build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/apps/totem-client/dist /usr/share/nginx/html
```

### **2. Cache Otimizado**
```yaml
# .github/workflows/deploy.yml
- uses: actions/setup-node@v3
  with:
    node-version: '18'
    cache: 'pnpm'

- name: Install pnpm
  uses: pnpm/action-setup@v2
  with:
    version: 8
```

### **3. Build Paralelo**
```json
// package.json
{
  "scripts": {
    "build:all": "pnpm --parallel --filter \"./apps/**\" build",
    "dev:all": "pnpm --parallel --filter \"./apps/**\" dev"
  }
}
```

## 🎯 Vantagens da Estrutura Monorepo

- ✅ **Dependências compartilhadas** (utils, hooks)
- ✅ **Build otimizado** com pnpm
- ✅ **Deploy independente** por app
- ✅ **Cache eficiente** entre builds
- ✅ **Manutenção centralizada**

## 💰 Custos Finais (Monorepo)

| Serviço | Custo | O que inclui |
|---------|-------|--------------|
| **Railway** | $5/mês | API + PostgreSQL |
| **Vercel** | $0/mês | Frontend + CDN |
| **Total** | $5/mês | Sistema completo |

**Tempo estimado**: 45 minutos (monorepo requer mais configuração) 