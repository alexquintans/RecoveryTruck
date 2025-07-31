Perfeito! Vou criar um guia **super detalhado** passo a passo para você que nunca fez deploy com Docker e monorepo. Vou dividir em etapas bem claras:

## �� Guia Completo - Deploy Monorepo (Primeira Vez)

### **�� Pré-requisitos**
- Conta no GitHub
- Conta no Railway (gratuita)
- Conta no Vercel (gratuita)
- Projeto já no GitHub

---

## **FASE 1: Preparação do Projeto** ⚙️

### **Passo 1.1: Verificar Estrutura**

```bash
ls -la
```
```bash
dir
```
✅ **Estrutura OK!** Vejo que você tem:
- `apps/` (monorepo)
- `packages/` (dependências compartilhadas)
- `railway.json` (já criado)
- `docker-compose.yml` (já existe)

### **Passo 1.2: Verificar se está no GitHub**

```bash
git remote -v
```
✅ **GitHub OK!** Repositório: `https://github.com/gfugulin/ProjetoTotem.git`

### **Passo 1.3: Verificar se tudo está commitado**

```bash
git status
```
⚠️ **ATENÇÃO!** Você tem muitas mudanças não commitadas. Vamos commitar tudo antes do deploy:

```bash
git add .
```
```bash
git commit -m "Preparação para deploy: configurações Railway e Vercel para monorepo"
```
```bash
git push origin main
```
✅ **Perfeito!** Tudo commitado e enviado para o GitHub.

---

## **FASE 2: Deploy da API no Railway** 🚂

### **Passo 2.1: Criar conta no Railway**

1. **Acesse**: [railway.app](https://railway.app)
2. **Clique em**: "Start a New Project"
3. **Escolha**: "Deploy from GitHub repo"
4. **Conecte sua conta GitHub** (se ainda não conectou)
5. **Selecione o repositório**: `gfugulin/ProjetoTotem`

### **Passo 2.2: Configurar o Projeto**

Após conectar o GitHub:

1. **Railway detectará automaticamente**:
   - ✅ `railway.json` na raiz
   - ✅ `apps/api/Dockerfile`
   - ✅ Estrutura monorepo

2. **Clique em**: "Deploy Now"

3. **Aguarde o build** (pode demorar 5-10 minutos na primeira vez)

### **Passo 2.3: Adicionar PostgreSQL**

**IMPORTANTE**: Faça isso **APÓS** o deploy da API estar funcionando.

1. **No Railway Dashboard**:
   - Clique em "New Service"
   - Selecione "Database"
   - Escolha "PostgreSQL"

2. **Conectar à API**:
   - Vá na aba "Variables" da API
   - Copie a variável `DATABASE_URL` do PostgreSQL
   - Cole na API

### **Passo 2.4: Configurar Variáveis de Ambiente**

Na API, vá em "Variables" e adicione:

```env
DATABASE_URL=postgresql://[railway-db-url] (copiado do PostgreSQL)
JWT_SECRET=sua_chave_super_secreta_aqui_123456789
ENVIRONMENT=production
CORS_ORIGINS=https://seu-frontend.vercel.app (vamos configurar depois)
LOG_LEVEL=INFO
APP_ENV=production
```

### **Passo 2.5: Verificar se API está funcionando**

1. **Vá na aba "Deployments"**
2. **Clique no último deployment**
3. **Copie a URL** (exemplo: `https://seu-projeto.railway.app`)
4. **Teste**: `https://sua-url.railway.app/health`

---

## **FASE 3: Deploy do Frontend no Vercel** ⚡

### **Passo 3.1: Criar conta no Vercel**

1. **Acesse**: [vercel.com](https://vercel.com)
2. **Clique em**: "Continue with GitHub"
3. **Autorize** o Vercel a acessar seus repositórios

### **Passo 3.2: Importar Projeto**

1. **Clique em**: "New Project"
2. **Selecione**: `gfugulin/ProjetoTotem`
3. **Vercel detectará**:
   - ✅ `apps/totem-client/vercel.json`
   - ✅ `apps/totem-client/package.json`

### **Passo 3.3: Configurar Build**

O Vercel deve detectar automaticamente:

- **Framework**: Vite
- **Build Command**: `pnpm install && pnpm --filter totem-client build`
- **Output Directory**: `apps/totem-client/dist`
- **Install Command**: `pnpm install`

### **Passo 3.4: Configurar Variáveis de Ambiente**

No Vercel, vá em "Settings" → "Environment Variables":

```env
VITE_API_URL=https://sua-api.railway.app (URL da API do Railway)
VITE_TENANT_ID=seu_tenant_id (se você tiver)
```

### **Passo 3.5: Deploy**

1. **Clique em**: "Deploy"
2. **Aguarde o build** (3-5 minutos)
3. **Copie a URL** do frontend

---

## **FASE 4: Conectar Frontend e Backend** 🔗

### **Passo 4.1: Atualizar CORS na API**

No Railway, vá nas variáveis da API e atualize:

```env
CORS_ORIGINS=https://recovery-truck-totem-client-7ynj.vercel.app,https://recovery-truck-panel-client.vercel.app
```

### **Passo 4.2: Testar Conexão**

1. **Acesse o frontend**
2. **Teste se consegue fazer login**
3. **Verifique se as requisições para a API funcionam**

---

## **FASE 5: Configurações Finais** ⚙️

### **Passo 5.1: Domínios Personalizados (Opcional)**

**Railway**:
- Vá em "Settings" → "Domains"
- Adicione seu domínio

**Vercel**:
- Vá em "Settings" → "Domains"
- Adicione seu domínio

### **Passo 5.2: Monitoramento**

**Railway**:
- Vá em "Metrics" para ver logs
- Configure alertas se necessário

**Vercel**:
- Vá em "Analytics" para ver métricas
- Configure webhooks se necessário

---

## **🔧 Troubleshooting Comum**

### **Problema 1: Build falha no Railway**
```bash
# Verificar logs no Railway
# Verificar se Dockerfile está correto
# Verificar se requirements.txt existe
```

### **Problema 2: Build falha no Vercel**
```bash
# Verificar se pnpm está instalado
# Verificar se workspace está configurado
# Verificar se vercel.json está correto
```

### **Problema 3: CORS errors**
```bash
# Verificar CORS_ORIGINS na API
# Verificar se URLs estão corretas
```

### **Problema 4: Database não conecta**
```bash
# Verificar DATABASE_URL
# Verificar se PostgreSQL está ativo
# Verificar migrations
```

---

## **📊 URLs Finais**

Após o deploy, você terá:

- **API**: `https://seu-projeto.railway.app`
- **Frontend**: `https://seu-projeto.vercel.app`
- **Database**: Gerenciado pelo Railway

---

## **⏱️ Tempo Estimado**

- **Fase 1**: 5 minutos (preparação)
- **Fase 2**: 15 minutos (Railway)
- **Fase 3**: 10 minutos (Vercel)
- **Fase 4**: 5 minutos (conexão)
- **Fase 5**: 10 minutos (configurações)

**Total**: ~45 minutos

---

## **�� Custos Finais**

- **Railway**: $5/mês (API + PostgreSQL)
- **Vercel**: $0/mês (Frontend)
- **Total**: $5/mês

---

**�� Próximos passos**: Comece pela **Fase 2** (Railway) e me avise quando estiver na etapa de configurar as variáveis de ambiente!