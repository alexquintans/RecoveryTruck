Para transformar esse “wizard” de configuração do operador em algo realmente funcional, precisamos atuar em DUAS frentes:

──────────────────────────────────────────
1. Back-end – API
──────────────────────────────────────────
Criar/expôr endpoints REST que gravem (e leiam) as escolhas feitas pelo operador antes de iniciar a operação.

a) Equipamentos  
```
GET  /equipments?tenant=...
POST /equipments/assign        { operator_id, equipment_id }
POST /equipments/release       { operator_id }
```

b) Serviços disponíveis no painel  
```
GET  /services?tenant=...           → lista completa
PUT  /services/{id}/enable          { duration_minutes }
PUT  /services/{id}/disable
```

c) Itens extras  
```
GET  /extras?tenant=...
PUT  /extras/{id}/enable            { stock }
PUT  /extras/{id}/disable
```

d) Persistir a “sessão de operação”  
Criar tabela `operator_sessions`
```
id · operator_id · tenant_id · started_at · finished_at (nullable)
```
Endpoints:
```
POST /operator_sessions/start       { operator_id, equipment_id?, config_json }
POST /operator_sessions/finish      { session_id }
```

──────────────────────────────────────────
2. Front-end – apps/panel-client
──────────────────────────────────────────
A página `OperatorPage.tsx` já contém a maior parte da UI, mas hoje tudo fica apenas em estado local. Precisamos:

a) Substituir o estado local por hooks que chamam a API  
• Criar `src/services/operatorConfigService.ts`  
  – `fetchServices()`, `enableService()`, `disableService()`, etc.  
• Ajustar `useOperatorActions` ou novo hook `useOperatorConfig`.

b) Fluxo em etapas (Stepper)  
1)  Identificação do Operador  
2)  Seleção de Equipamento  
3)  Serviços Disponíveis  
4)  Itens Extras  
5)  Revisão → “Iniciar Operação”

Usar um estado `currentStep` e salvar cada etapa no back-end conforme o usuário clica “Próximo”.

c) Sincronização em tempo real  
Quando outro operador habilitar/desabilitar um serviço, usar websocket (`/ws/{tenant_id}/panel`) para receber `SERVICE_UPDATED`, `EXTRA_UPDATED`, etc. (já existe `websocket.py`, basta publicar eventos no back-end).

d) Persistência local para fallback  
Se o operador atualiza a página, pedir ao back-end a sessão em andamento e restaurar as seleções.

──────────────────────────────────────────
3. Passo-a-passo de implementação
──────────────────────────────────────────
1. Back-end  
   • Adicionar models + schemas (`EquipmentConfig`, `ServiceToggle`, `ExtraToggle`, `OperatorSession`).  
   • Adicionar rotas nos diretórios `routers/operator_config.py` e `routers/operator_sessions.py`.  
   • Emitir eventos WebSocket na mudança de estado (já há `websocket.py`).  

2. Front-end  
   • Criar services TS para cada endpoint.  
   • Refatorar `OperatorPage` em sub-componentes (`StepServices`, `StepExtras`, etc.).  
   • Usar `react-hook-form` para os formulários e manter estado global em `zustand` ou `context` para evitar prop-drilling.  

3. Desenvolvimento Hot-reload  
   • Rodar `npm run dev` no painel.  
   • Rodar API com `uvicorn --reload` montando volume (compose.dev).

4. Testes  
   • Criar testes e2e Cypress: login → wizard → iniciar sessão → chamadas de ticket funcionando.  
   • Backend: Pytest para cada endpoint.  


Passo 1 – service layer
=======================

Criarei um arquivo `src/services/operatorConfigService.ts` no panel-client com funções:

```
GET   /operator/services?tenant_id=
PUT   /operator/services/{id}

GET   /operator/extras?tenant_id=
PUT   /operator/extras/{id}

GET   /operator/equipments?tenant_id=
POST  /operator/equipments/assign
POST  /operator/equipments/release
```

O service aproveitará o helper `API_URL` e o token salvo em `@totem/utils`.

Passo 2 – hook
==============

`useOperatorConfig`:

```
const { user } = useAuth();          // já temos tenant_id no JWT
const {
   services, extras, equipments,
   toggleService, toggleExtra, assignEquipment …
}
```

• Internamente chama o service.  
• Atualiza estado local (zustand ou React context) para refletir instantaneamente.  
• Conecta via websocket (`/ws/{tenant_id}/panel`) e, ao receber `service_update` ou `extra_update`, faz merge de estado → UI re-renderiza.

Passo 3 – atualizar UI
======================

1. Em `OperatorPage.tsx`
   • Substituir o array `services`/`extras` locais pelo hook.
   • No toggle (switch) chamar `toggleService(id, enable, duration)`, etc.
   • Na lista de extras atualizar estoque com setinha → chama `toggleExtra`.

2. Stepper
   • Já existe o slider de etapas; apenas trocar `currentStep` e avançar
     quando “Continuar” chamar `/operator/sessions/start`.

Passo 4 – persistência
======================

• Quando a página monta, chamar `GET /operator/sessions/start?active=true`
  (a implementar depois) ou simplesmente consultar o hook; se houver sessão,
  restaurar seleções.

Vou começar pelo service e hook; em seguida mostro como plugar no `OperatorPage`.


Read file: apps/panel-client/src/components/OperatorConfigStep.tsx
Read file: apps/panel-client/src/hooks/useOperatorConfig.ts
O componente `OperatorConfigStep` e o hook `useOperatorConfig` já estão integrados e funcionais para o fluxo de configuração de serviços e extras do operador, conforme as imagens e o passo-a-passo do `docs/attOperator.md`.

**Próximos passos para finalizar a atualização do UI e persistência:**

---

### 1. Persistência e restauração de sessão do operador

- **Objetivo:** Ao montar a página, consultar se já existe uma sessão ativa para o operador e restaurar as seleções (serviços/extras/equipamento).
- **Como fazer:**  
  - Adicionar chamada ao endpoint `GET /operator/sessions/start?active=true` (ou equivalente) ao montar a página.
  - Se houver sessão, restaurar as seleções no estado do hook (serviços, extras, equipamento).
  - Se não houver, seguir o fluxo normal do wizard.

---

### 2. Integração do início de sessão

- **Ao clicar em “Continuar” no wizard:**
  - Chamar o endpoint `POST /operator/sessions/start` passando o operador, equipamento selecionado e o snapshot da configuração (serviços/extras).
  - Salvar o ID da sessão no localStorage ou estado global.
  - Avançar para o painel principal.

---

### 3. Atualização do UI do painel

- **Exibir informações da sessão ativa:**  
  - Mostrar o equipamento atribuído, nome do operador e configurações ativas.
  - Permitir encerrar a sessão (`/operator/sessions/finish`), limpando o estado e retornando ao wizard.

---

### 4. Sincronização em tempo real

- O hook já escuta o websocket para atualizações de serviços/extras/equipamentos, garantindo que o painel reaja a mudanças feitas por outros operadores.

---

### 5. Melhorias de UX

- Desabilitar botão “Continuar” enquanto não houver pelo menos um serviço ativo e um equipamento selecionado.
- Exibir feedback de loading/sucesso/erro nas ações de toggle e persistência.

---

**Resumo do que já está pronto:**
- Wizard de configuração usando o hook centralizado.
- Atualização instantânea dos estados de serviço/extra.
- UI reativa e pronta para integração com persistência de sessão.

**O que falta implementar:**
- Chamada e restauração de sessão do operador (backend + integração no hook/página).
- Integração do equipamento selecionado no início da sessão.
- Feedback visual e bloqueio de ações conforme estado.

Se quiser, posso implementar agora a lógica de persistência/restauração de sessão e integração do equipamento selecionado no wizard. Deseja prosseguir com isso?