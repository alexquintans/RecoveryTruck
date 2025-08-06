# Solução para Problemas de CORS no Totem-Client

## Problemas Identificados

### 1. Erro de CORS Original
```
Access to XMLHttpRequest at 'https://recoverytruck-production.up.railway.app/tickets' 
from origin 'https://recovery-truck-totem-client-7ynj.vercel.app' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### 2. Erro de Header Origin (RESOLVIDO)
```
Refused to set unsafe header "Origin"
```
**Causa**: Tentativa de definir manualmente o header `Origin`, que é controlado pelo navegador.
**Solução**: Removida a linha que tentava definir `Origin` manualmente.

### 3. Erro de Backend - service_id null (RESOLVIDO)
```
null value in column "service_id" of relation "payment_sessions" violates not-null constraint
```
**Causa**: O backend estava criando uma `PaymentSession` temporária com `service_id=None` quando havia assinatura.
**Solução**: 
- Corrigido o backend para usar o `service_id` do primeiro serviço do ticket
- Tornado o campo `payment_session_id` nullable na tabela `tickets`
- Criada migração `019_make_payment_session_id_nullable.py`

## Soluções Implementadas

### 1. Configuração de API Específica (`api-config.ts`)

Criamos uma configuração específica para o totem-client que:
- Usa axios com timeout de 30 segundos
- Adiciona headers necessários automaticamente
- **REMOVIDO**: Tentativa de definir header `Origin` manualmente
- Trata erros de CORS e servidor especificamente
- Inclui funções de debug e verificação de saúde da API

### 2. Proxy de Desenvolvimento (Vite)

Configuramos um proxy no Vite para desenvolvimento local:
```typescript
proxy: {
  '/api': {
    target: 'https://recoverytruck-production.up.railway.app',
    changeOrigin: true,
    secure: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

### 3. Componente de Tratamento de Erros (`ErrorHandler.tsx`)

Criamos um componente que:
- Verifica a saúde da API ao carregar
- Captura eventos de erro de CORS
- Exibe interface amigável para erros de conexão
- Fornece informações de debug

### 4. Interceptors de Erro

Implementamos interceptors que:
- Detectam erros de CORS automaticamente
- Emitem eventos customizados para tratamento
- Fornecem informações detalhadas de debug

### 5. Correções no Backend (NOVO)

#### 5.1. Correção do service_id null
**Arquivo**: `apps/api/routers/tickets.py` (linha ~1205)
```python
# ANTES (problemático):
temp_payment_session = PaymentSession(
    service_id=None,  # ❌ Causava erro
    # ...
)

# DEPOIS (corrigido):
service_id = ticket_in.services[0].service_id if ticket_in.services else None
if not service_id:
    raise HTTPException(status_code=400, detail="Ticket deve ter pelo menos um serviço")

temp_payment_session = PaymentSession(
    service_id=service_id,  # ✅ Usa o service_id do primeiro serviço
    # ...
)
```

#### 5.2. Correção do payment_session_id nullable
**Arquivo**: `apps/api/models.py` (linha 170)
```python
# ANTES:
payment_session_id = Column(UUID(as_uuid=True), ForeignKey("payment_sessions.id"), nullable=False)

# DEPOIS:
payment_session_id = Column(UUID(as_uuid=True), ForeignKey("payment_sessions.id"), nullable=True)
```

#### 5.3. Migração do Banco de Dados
**Arquivo**: `apps/api/migrations/versions/019_make_payment_session_id_nullable.py`
```python
def upgrade():
    op.alter_column('tickets', 'payment_session_id',
               existing_type=postgresql.UUID(as_uuid=True),
               nullable=True)
```

### 6. Logs de Debug (NOVO)

Adicionamos logs detalhados em todas as funções de API:
- `createTicket`: Log do payload e resposta
- `createPaymentSession`: Log do payload e resposta  
- `createPaymentForTicket`: Log dos parâmetros e resposta
- Backend: Logs detalhados na criação de tickets

## Como Usar

### Para Desenvolvimento Local

1. O proxy do Vite será usado automaticamente
2. As requisições serão feitas para `/api` que será redirecionado para o servidor
3. Logs de debug estarão disponíveis no console

### Para Produção

1. O totem-client usa a URL completa da API
2. O ErrorHandler captura e trata erros de CORS
3. Informações de debug estão disponíveis

### Debug de Problemas

Para debugar problemas:

1. **Abra o console do navegador**
2. **Procure por logs com prefixo `🔍 DEBUG`**:
   - `Criando ticket com payload:`
   - `Resposta do ticket:`
   - `Criando payment para ticket:`
   - `Resposta do payment:`
   - `Criando payment session com payload:`
   - `Resposta do payment session:`
3. **Procure por eventos `cors:error` ou `server:error`**
4. **Use o botão "Informações de Debug" no ErrorHandler**
5. **Verifique as informações de CORS no console**

## Configurações de Ambiente

### frontend.env
```
VITE_API_URL=https://recoverytruck-production.up.railway.app
VITE_WS_URL=wss://recoverytruck-production.up.railway.app/ws
VITE_TENANT_ID=7f02a566-2406-436d-b10d-90ecddd3fe2d
VITE_DISABLE_KIOSK_MODE=false
```

## Status das Correções

### ✅ RESOLVIDO
- **Erro de Header Origin**: Removida tentativa de definir Origin manualmente
- **Erro de service_id null**: Corrigido backend para usar service_id do primeiro serviço
- **Erro de payment_session_id**: Tornado nullable no modelo e banco de dados

### 🔍 EM MONITORAMENTO
- Logs de debug adicionados para monitorar futuros problemas
- ErrorHandler implementado para capturar erros de CORS
- Proxy configurado para desenvolvimento local

## Próximos Passos

Se o problema persistir:

1. **Verificar logs de debug**: Analise todos os logs `🔍 DEBUG` no console
2. **Verificar configuração do servidor**: O servidor precisa permitir requisições do domínio do totem-client
3. **Configurar CORS no backend**: Adicionar headers de CORS apropriados
4. **Usar CDN ou proxy**: Considerar usar um proxy reverso para evitar problemas de CORS
5. **Verificar payload**: Confirmar que o payload está sendo enviado corretamente

## Monitoramento

O sistema agora:
- Monitora automaticamente a saúde da API
- Captura e reporta erros de CORS
- Fornece informações de debug detalhadas
- Permite retry automático em caso de falha
- **NOVO**: Logs detalhados de todas as operações de API
- **NOVO**: Correções no backend para evitar erros de constraint
- **NOVO**: Migração do banco de dados para suportar tickets sem payment_session 