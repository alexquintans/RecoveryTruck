# 🚀 Guia de Deploy Gratuito - Totem App

## Opções Recomendadas (Ordem de Prioridade)

### 1. **Railway** ⭐ (Mais Rápido)
**Custo**: $5/mês de crédito (gratuito para projetos pequenos)

#### Passos:
1. **Criar conta**: [railway.app](https://railway.app)
2. **Conectar GitHub**: Selecione este repositório
3. **Adicionar PostgreSQL**: 
   - Vá em "New Service" → "Database" → "PostgreSQL"
4. **Deploy da API**:
   - "New Service" → "GitHub Repo"
   - Selecione este repo
   - Railway detectará automaticamente o `railway.json`
5. **Configurar variáveis de ambiente**:
   ```
   DATABASE_URL=postgresql://[railway-db-url]
   JWT_SECRET=sua_chave_secreta_aqui
   ENVIRONMENT=production
   CORS_ORIGINS=https://seu-frontend.vercel.app
   ```

#### Vantagens:
- ✅ Deploy automático
- ✅ PostgreSQL incluído
- ✅ SSL automático
- ✅ Domínio gratuito
- ✅ Build automático

---

### 2. **Render** (Alternativa Excelente)
**Custo**: 1 serviço web + PostgreSQL gratuitos

#### Passos:
1. **Criar conta**: [render.com](https://render.com)
2. **Deploy da API**:
   - "New Web Service" → GitHub
   - Build Command: `pip install -r apps/api/requirements.txt`
   - Start Command: `uvicorn apps.api.full_api:app --host 0.0.0.0 --port $PORT`
3. **Adicionar PostgreSQL**:
   - "New PostgreSQL"
   - Conectar à API

---

### 3. **Vercel + PlanetScale** (Frontend + Banco)
**Custo**: Totalmente gratuito

#### Frontend (Vercel):
1. **Deploy**: [vercel.com](https://vercel.com)
2. **Conectar GitHub**
3. **Configurar build**:
   - Framework: Vite
   - Build Command: `cd apps/totem-client && npm run build`
   - Output Directory: `apps/totem-client/dist`

#### Banco (PlanetScale):
1. **Criar conta**: [planetscale.com](https://planetscale.com)
2. **Criar database**
3. **Migrar schema** (converter PostgreSQL → MySQL)

---

## 🛠️ Preparação do Projeto

### 1. Variáveis de Ambiente
Crie `.env` na raiz:
```env
# API
DATABASE_URL=postgresql://user:pass@host:port/db
JWT_SECRET=sua_chave_super_secreta
ENVIRONMENT=production
CORS_ORIGINS=https://seu-frontend.vercel.app

# Mercado Pago (se usar)
MERCADOPAGO_ACCESS_TOKEN=seu_token
MERCADOPAGO_PUBLIC_KEY=sua_public_key
```

### 2. Frontend Environment
Crie `apps/totem-client/.env.production`:
```env
VITE_API_URL=https://sua-api.railway.app
VITE_TENANT_ID=seu_tenant_id
```

### 3. Build do Frontend
```bash
cd apps/totem-client
npm install
npm run build
```

---

## 🚀 Deploy Rápido (Railway)

### Passo a Passo:

1. **Fork/Clone** este repositório
2. **Acesse** [railway.app](https://railway.app)
3. **Login** com GitHub
4. **New Project** → "Deploy from GitHub repo"
5. **Selecione** este repositório
6. **Adicione PostgreSQL**:
   - "New Service" → "Database" → "PostgreSQL"
7. **Configure variáveis**:
   - Vá em "Variables"
   - Adicione as variáveis do `.env`
8. **Deploy automático** acontecerá!

### URLs finais:
- **API**: `https://seu-projeto.railway.app`
- **Frontend**: Deploy no Vercel
- **Database**: Gerenciado pelo Railway

---

## 🔧 Troubleshooting

### Problemas comuns:

1. **Build falha**:
   - Verifique se `railway.json` está na raiz
   - Confirme se `Dockerfile` está correto

2. **Database não conecta**:
   - Verifique `DATABASE_URL` nas variáveis
   - Confirme se PostgreSQL está ativo

3. **CORS errors**:
   - Adicione URL do frontend em `CORS_ORIGINS`

4. **Porta não encontrada**:
   - Railway usa `$PORT`, não porta fixa

---

## 💰 Custos Estimados

| Plataforma | Custo Mensal | Limitações |
|------------|--------------|------------|
| **Railway** | $5 crédito | 500 horas/mês |
| **Render** | Gratuito | 1 serviço web |
| **Vercel** | Gratuito | 100GB bandwidth |
| **PlanetScale** | Gratuito | 1GB storage |

---

## 🎯 Recomendação Final

**Para deploy mais rápido e gratuito:**
1. **Railway** para API + PostgreSQL
2. **Vercel** para frontend
3. **Total**: $5/mês (Railway) + $0 (Vercel)

**Tempo estimado**: 30 minutos para deploy completo! 