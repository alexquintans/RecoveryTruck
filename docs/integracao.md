Resumo do estado atual da integração Front-end ⇆ Back-end (14/06/2025)

────────────────────────────────────────
✔️ Funcionalidades já totalmente conectadas ao Back-end

1. Autenticação (panel-client)  
   • Tela de Login usa POST `/auth/token` e grava JWT.  
   • Contexto `useAuth` protege rotas com `<RequireAuth>`.

2. Camada de acesso HTTP  
   • Wrapper `fetchApi` (packages/utils) injeta `Authorization` + `X-Tenant-Id`, faz logout automático em 401.  
   • `ticketService` e `serviceService` realizam chamadas REST reais.  
   • Alias `@totem/utils` / `@totem/hooks` configurados nos dois apps.

3. WebSocket & Fila de tickets  
   • Hook `useTicketQueue`  
     – Faz GET `/tickets/queue` (React-Query).  
     – Abre WS em `ws://API/ws?tenant_id=...&client_type=operator&token=<jwt>`.  
     – Atualiza cache em `queue_update`/`ticket_update`.  
   • Hook `useOperatorActions` (panel) chama endpoints reais `call/start/complete/cancel` e atualiza o cache.

4. Estrutura de build/monorepo  
   • Pacotes internos referenciados via workspaces; tipos compilam sem erros críticos.

5. DashboardPage  
   • Já usa `useTicketQueue` (dados reais de tickets).  
   • Equipamentos, operação e estatísticas avançadas ainda vazios (back-end ainda não expõe).  
   • Precisa remover código duplicado gerado na última edição (iremos refatorar).

6. OperatorPage  
   • Importou `useTicketQueue` + `useOperatorActions`, porém ainda mantém partes do antigo `mockPanelStore`.  
   • Falta:  
     – Desestruturar dados do hook (tickets / operationConfig).  
     – Ajustar handlers de equipamentos (ainda locais).  
     – Retirar chamadas `resetMockData`, `startOperation`, `endOperation` ou ligá-las a endpoints reais quando existirem.

────────────────────────────────────────
🔧 Em transição (parte real, parte mock)

C. DisplayPage  
   • Continua 100 % mock; aguardando migração para `useTicketQueue`.

────────────────────────────────────────
❌ Ainda 100 % mock / fora do escopo real

1. Totem-client  
   • Continua usando `src/utils/api.ts` com fetch + dados simulados (serviços, pagamento, tickets).  
   • WS ainda não conectado.

2. Equipamentos & Operação  
   • Toda lógica de quantidade de banheiras/botas e “startOperation/endOperation” é mock local; back-end ainda não possui endpoints nem broadcast.

3. Estatísticas agregadas (tempo médio, receita, etc.)  
   • Cálculo é feito no front-end sobre os tickets; se o back-end precisar fornecer métricas oficiais, faltam endpoints.

────────────────────────────────────────
Próximos passos (para eliminar dados mock)

1. Concluir OperatorPage  
   • Limpar duplicatas no arquivo.  
   • Substituir todas as referências a `mockPanelStore`.  
   • Usar `useTicketQueue()` para leitura e `useOperatorActions()` para mutações.

2. Refatorar DisplayPage  
   • Ler apenas `useTicketQueue()` (modo leitura).  
   • Tocar sons com `useSoundNotifications` quando receber `ticket_update` status `called`.

3. Totem-client  
   • Substituir utilitário fetch pelo pacote `@totem/utils`.  
   • Criar `paymentSessionService` para `/payment_sessions`.  
   • Conectar WS `client_type=totem` para receber `payment_update` & `ticket_update`.

4. Back-end (se necessário)  
   • Se quisermos remover mocks de equipamentos, criar endpoints `/equipment` e `queue/operation` + eventos WS.

Posso continuar imediatamente pelo item 1 (OperatorPage) e depois item 2. Avise se gostaria que eu execute essas refatorações agora ou se prioriza outra parte.