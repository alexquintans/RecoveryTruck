Read file: apps/api/security.py

Read file: apps/api/auth.py

Ran tool

Read file: apps/totem-client/src/utils/api.ts

Read file: packages/utils/src/helpers/api.ts

Read file: packages/utils/src/helpers/auth.ts

Read file: apps/api/routers/services.py

Ran tool

Ran tool

Ran tool

Ran tool

Read file: apps/api/auth.py

Ran tool

Para que a “Camada de acesso à API” realmente feche o ciclo entre React (front-end) e FastAPI (back-end) precisamos ir um pouco além do simples `axios.create`.  
Abaixo está o checklist completo ― boa parte já existe no monorepo mas vale confirmar/ajustar.

────────────────────────────────────────────────────────
1. Arquivos .env (✓ já criados)  
• `VITE_API_URL`, `VITE_WS_URL`, `VITE_TENANT_ID` nos dois clients.  
• Backend com `CORS_ORIGINS` apontando para as portas do Vite.

2. Cliente HTTP (axios ou fetch)
a) Criar/ajustar `src/services/api.ts` em cada client (ou usar o já existente em `packages/utils/helpers/api.ts`).  
   – `baseURL` = `VITE_API_URL`.  
   – Request-interceptor: adiciona  
       • `Authorization: Bearer <token>` (lido de `localStorage` / helper `getAuthToken`).  
       • `X-Tenant-Id` (ou outro header) se quiser forçar tenant num cenário multi-tenant.  
   – Response-interceptor:  
       • Se `status === 401`, limpar token (`logout()`) e redirecionar para `/login`.  
       • Opcional: mostrar toast de erro genérico.

b) Exportar um thin-wrapper:

```ts
export const api = {
  get:  <T>(url: string, config?: AxiosRequestConfig) => instance.get<T>(url, config),
  post: <T>(url: string, data?: any, config?: AxiosRequestConfig) => instance.post<T>(url, data, config),
  // … put, patch, delete
};
```

3. Serviços de domínio
Para cada recurso do back-end crie um service dedicado que use o wrapper acima.  
Exemplos (no painel):

```
/src/services/authService.ts
  login (POST /auth/token)
  logout (limpa storage)

 /src/services/ticketService.ts
  listTickets
  queue
  call/start/complete/cancel
  dashboardStats

 /src/services/serviceService.ts
  getServices etc.
```

Isso facilita trocar fetch↔axios e centraliza tratamento de erro.

4. Gestão de autenticação
• Helpers já existem em `packages/utils/helpers/auth.ts` (set/get token, isAuthenticated).  
• Criar um hook React `useAuth` no painel que exponha:
  `login(email, pwd)`, `logout()`, `operator`, `isAuthenticated`, `loading`.  
  Ele consome `authService` e grava token/usuario no Zustand ou Context API.

5. Proteção de rotas
No painel: `PrivateRoute` (React-Router) ou `useAuth` dentro das páginas.  
No totem não é necessário token; mas se em algum momento o back-end exigir tenant header ou token “guest”, o mesmo wrapper já cuida.

6. Tipos TypeScript
Gere tipos a partir do esquema OpenAPI para evitar `any`. Ferramentas:  
`npx openapi-typescript http://localhost:8000/openapi.json --output src/types/api.d.ts`  
Isso produz interfaces idênticas aos `schemas.py`.

7. Tratamento global de erros
Crie um interceptor ou HOC para:
• Notificar com `toast.error(message)`  
• Case 422/400: exibir detalhes no formulário  
• Case 500+: mensagem genérica

8. WebSocket
Quando o socket exigir autenticação (header ou query ?token=) use o mesmo token obtido pelo authService.  
O hook `useWebSocket.ts` que já existe pode receber o token:

```ts
const ws = new WebSocket(`${VITE_WS_URL}?token=${token}&tenant=${tenantId}&type=operator`);
```

9. Multi-tenant
Se operar com mais de um tenant:
• Ao logar, backend devolve `tenant_id` no payload JWT.  
• Salve isso em `localStorage` e envie via `X-Tenant-Id` header quando necessário.

10. Smoke-tests de integração
Use o Jest/RTL já configurado para testar que:
• `authService.login` grava token.  
• `ticketService.listTickets` dispara chamada `GET /tickets/queue` com header Authorization.

────────────────────────────────────────────────────────
Resumo prático do que falta escrever:

1. `panel-client/src/services/api.ts` (ou apontar para `packages/utils/helpers/api.ts`).  
2. `panel-client/src/services/authService.ts`, `ticketService.ts`, `serviceService.ts`  
3. `panel-client/src/hooks/useAuth.ts` e `PrivateRoute`/`RequireAuth`  
4. Mesmo pattern (sem auth) em `totem-client/src/services/api.ts` (pode reutilizar fetch existente, mas trocar para wrapper garante padronização).  
5. Adicionar interceptores axios ou, se for manter `fetchApi`, mover a lógica de 401/logout para ele.

Com esse checklist concluído a camada de acesso ficará pronta, permitindo que as páginas façam chamadas reais e que os sockets recebam atualizações on-line da fila/tíquetes.