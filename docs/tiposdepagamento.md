Claro! Vamos fazer um “estudo de viabilidade” completo – técnico e de produto – para que você saiba exatamente:

1. Quais pontos do sistema precisam ser alterados (banco, API, painel do operador, totem-client e panel-client).  
2. Como cada modo de funcionamento (Nenhum pagamento, Mercado Pago – Checkout Pro, Maquininha Sicredi) se encaixa na arquitetura existente.  
3. Como manter o código sustentável (feature-flags, extensibilidade, testes etc.).

=====================================================================
1. Visão geral dos três cenários
=====================================================================

A) “Somente gerenciamento de tickets”  
• Não existe cobrança eletrônica; o PaymentPage do Totem deve ser pulado.  
• O operador continua podendo marcar tickets como pagos manualmente se desejar (ex.: botão “Concluir sem pagamento”).  

B) Mercado Pago – Checkout Pro  
• Processo 100 % online via redirecionamento/iframe do Mercado Pago.  
• Fluxo já está parcialmente pronto (PaymentPage -> `MercadoPagoPayment`). Precisamos só garantir:  
  – Gerar `preference_id` na API.  
  – Manter WebSocket/Pooling para receber `payment_update`.  

C) Maquininha física Sicredi  
• O backend já contém esboço de integração em `apps/api/services/payment/terminal` e exemplos em `examples/sicredi_integration_example.py`.  
• Totem exibe tela “Aproxime ou insira o cartão na maquininha”; backend comanda o terminal e devolve status via WebSocket.  

=====================================================================
2. Alterações de domínio / banco
=====================================================================

Tabela `operation_config` (ou equivalente)  
Adicionar campo novo:

```
payment_modes   TEXT[]        -- ex.: ['none'] | ['mercadopago'] | ['sicredi'] | ['mercadopago','sicredi']
```

• Usar enum no Alembic: `payment_modes_enum` com valores `none`, `mercadopago`, `sicredi`.  
• Permitir array (PostgreSQL `TEXT[]`) para habilitar múltiplos métodos futuros.

=====================================================================
3. Backend/API
=====================================================================

1. Schemas (`schemas.py`)  
   – Atualizar `OperationConfig` / `OperationConfigUpdateSchema` para incluir `payment_modes: list[PaymentMode]`.

2. Endpoints  
   – `GET /operation-config` → devolver `payment_modes`.  
   – `POST/PUT /operation-config` → aceitar o array.

3. Lógica de pagamento  
   a. Rota `POST /tickets/{id}/payment`  
      – Se `'none' in payment_modes`, retornar erro 400 ou simplesmente não criar sessão e sinalizar “SEM_PAGAMENTO”.  
   b. Mercado Pago  
      – Já existe `createPaymentForTicket` que devolve `preference_id`. Garantir estojo Checkout Pro (link/iframe).  
   c. Sicredi  
      – Criar/terminar transação via SDK na camada `services/payment/terminal/sicredi_terminal.py`.  
      – Manter padrão `PaymentSession` (`id`, `status`, `ticket_id`, `provider_reference`, etc.).

4. WebSocket  
   – Mensagem `payment_update` permanece igual; apenas o produtor muda conforme o provider (MercadoPago ou Sicredi).

=====================================================================
4. Painel do Operador (panel-client)
=====================================================================

Etapa “config” (já existe em `OperatorPage`):

1. Adicionar novo bloco “Métodos de Pagamento” com 3 checkboxes ou radio:  
   - Nenhum (gerenciamento de tickets)  
   - Mercado Pago  
   - Sicredi

2. No payload enviado a `saveOperationConfig`, incluir `payment_modes`.  
   Exemplo do trecho já existente:

```ts
const configPayload = {
  tenant_id,
  operator_id,
  services: [...],
  equipments: [...],
  extras: [...],
  payment_modes // ← novo campo
}
```

3. UI/UX  
   – Se “Nenhum” for marcado, desabilitar os demais.  
   – Help-text explicando o impacto (pular pagamento no Totem).

=====================================================================
5. Totem-client
=====================================================================

1. `useTotemStore`  
   – Guardar `operationConfig.payment_modes`.

2. Roteamento  
   – Ao passar pelo fluxo de termos → se `payment_modes` contém `'none'`, pular a rota `/payment` e gerar ticket diretamente (`api.createTicket(..., skipPayment=true)`).

3. PaymentPage  
   – Filtrar métodos disponíveis:  
     • Mercado Pago → já exibido.  
     • Sicredi → exibir CardPaymentInterface “Insira o cartão na maquininha”.  
   – Se nenhum método disponível, mostrar aviso e botão “Continuar”.

=====================================================================
6. API → Frontend contrato
=====================================================================

Novo endpoint opcional: `POST /tickets` com body extra `skip_payment: bool`.  
• Se `true`, ticket status vem como `pending_payment=false` e não cria PaymentSession.

=====================================================================
7. Mecanismo de Feature-flag / Sustentabilidade
=====================================================================

• Os métodos de pagamento serão tratados como “plugins” (Strategy Pattern) já usado em `services/payment/adapters`.  
• Novo Enum `PaymentMode` compartilhado entre backend e front (via `types/index.ts`).  
• Testes unitários:  
  – Backend: criar ticket nos 3 cenários e validar respostas.  
  – Frontend: Cypress / React Testing Library para verificar fluxo com/sem pagamento.  
• Documentação: atualizar `/docs/Pagamento/` com diagramas de sequência.

=====================================================================
8. Roadmap de implementação sugerido
=====================================================================

1. Banco & models (migration Alembic).  
2. Ajustar schemas / endpoints.  
3. Refatorar service `createPaymentForTicket` para suportar `'none'`.  
4. Painel do Operador – UI dos métodos + envio ao backend.  
5. Totem-client – pular PaymentPage quando adequado; adaptar UI.  
6. Implementar Checkout Pro:  
   – No backend gerar `init_point` ou `preference_id`.  
   – No front usar iframe oficial.  
7. Finalizar integração Sicredi (já há código-base).  
8. Testes end-to-end (dummy WebSocket + mock providers).  

=====================================================================
9. Próximos passos
=====================================================================

Se o plano estiver claro para você, podemos começar pela parte que tem menor acoplamento (painel do operador + novo campo `payment_modes`). Quando estiver ok seguimos para backend e, por fim, Totem-client.

Fico à disposição para avançar na implementação!