Estudo Orientado de Modelagem de Banco de Dados  
Projeto Totem – Levantamento de Requisitos e Proposta de Modelo

────────────────────────────────────────────
1. Visão Geral do Sistema
────────────────────────────────────────────
O Totem é um ecossistema composto por:

• API back-end (FastAPI + SQLAlchemy)  
• Front-end “totem client” (terminal de autoatendimento)  
• Front-end “panel client” (painel/operador)  
• Serviços auxiliares: fila de tickets, pagamentos em múltiplos terminais, impressora, webhooks, métricas/alertas.

O banco de dados centraliza:
1. Gerenciamento multi-tenant (várias filiais/empresas).  
2. Catálogo de serviços e respectivos preços.  
3. Fluxo de tickets (fila, estado, prioridade).  
4. Pagamentos (sessões, métodos, status, recibos).  
5. Equipamentos (terminais físicos, impressoras, painéis).  
6. Usuários/operadores e autenticação (JWT).  
7. Logs relevantes (opcional agregar em tabelas).

────────────────────────────────────────────
2. Requisitos Funcionais
────────────────────────────────────────────
RF-01  Cadastrar e manter Tenants  
RF-02  Cadastrar Serviços (por Tenant) com preço e tempo estimado  
RF-03  Gerar Ticket no Totem (cliente) associando-se a Tenant e Serviço  
RF-04  Controlar estados do Ticket (created, waiting, in_service, finished, canceled, expired)  
RF-05  Exibir fila ordenada no Painel do Operador  
RF-06  Associar Ticket a Operador (quando atendido)  
RF-07  Persistir sessão de pagamento (iniciada no Totem) e atualizar status (pending, paid, failed, refunded)  
RF-08  Registrar transações por adaptador (pagseguro, stone, etc.) com ID externo  
RF-09  Emitir recibo (código + PDF/texto) e relacionar ao pagamento  
RF-10  Cadastrar Equipamentos (terminais, painéis) e seu Tenant  
RF-11  Gerenciar permissões de Operadores (por Tenant)  
RF-12  Gerar métricas (via Prometheus) – mas somente algumas são persistidas (ex: histórico diário)  
RF-13  Armazenar configurações de impressão, webhook, notificações por Tenant  
RF-14  Auditar ações críticas (login, cancelamento de pagamento, mudança manual de estado)

────────────────────────────────────────────
3. Requisitos Não Funcionais Relacionados ao BD
────────────────────────────────────────────
RNF-01  PostgreSQL ≥ 15 (já em uso)  
RNF-02  Isolamento por Tenant via colunas (schema único) com chave estrangeira `tenant_id`  
RNF-03  Integridade transacional (pagamento + mudança de estado)  
RNF-04  Índices em colunas de busca frequente (ticket.status, ticket.created_at, payment.external_id).  
RNF-05  Constraints de domínio para estados enumerados  
RNF-06  Migrável via Alembic; versionamento sem downtime  
RNF-07  Suporte a soft-delete (campo `deleted_at`) em entidades de configuração

────────────────────────────────────────────
4. Entidades Principais
────────────────────────────────────────────
(⚑ = chave primária)

1. tenant ⚑id, name, slug, logo_url, contact_email, created_at  
2. service ⚑id, tenant_id*, name, description, price_cents, duration_minutes, active, created_at  
3. ticket ⚑id, tenant_id*, service_id*, code, customer_name, state, priority, created_at, updated_at, operator_id?  
4. payment_session ⚑id, ticket_id*, method (pix, card, cash), adapter, external_id, amount_cents, status, created_at, updated_at  
5. receipt ⚑id, payment_session_id*, content (json/text), created_at  
6. user ⚑id, tenant_id*, username, full_name, hashed_password, role (admin, operator), created_at, last_login  
7. equipment ⚑id, tenant_id*, type (totem, panel, printer), identifier, location, status, created_at  
8. config_notification ⚑id, tenant_id*, slack_webhook, email_from, smtp_host, created_at  
9. config_webhook ⚑id, tenant_id*, target_url, secret, enabled, created_at  
10. audit_log ⚑id, tenant_id*, user_id?, action, entity, entity_id, data_json, created_at

(*) = foreign key

────────────────────────────────────────────
5. Relacionamentos
────────────────────────────────────────────
• tenant 1-N service / ticket / user / equipment / configs / audit_log  
• service 1-N ticket  
• ticket 1-1 payment_session (em geral) – mas deixar 1-N para reintentos  
• payment_session 1-1 receipt (nem toda sessão gera recibo)  
• user (operador) 1-N tickets atendidos  
• equipment (panel) lê tickets do seu tenant

────────────────────────────────────────────
6. Atributos Detalhados
────────────────────────────────────────────
ticket.state (enum):
- created  
- waiting  
- called  
- in_service  
- finished  
- canceled  
- expired

payment_session.status (enum):
- pending  
- paid  
- failed  
- canceled  
- refunded

equipment.status (enum):
- online  
- offline  
- maintenance

auditoria.action (exemplos):
- LOGIN  
- TICKET_CANCEL  
- PAYMENT_REFUND  
- CONFIG_UPDATE

────────────────────────────────────────────
7. Índices Sugeridos
────────────────────────────────────────────
• ticket(tenant_id, state, priority, created_at)  
• payment_session(external_id) UNIQUE  
• user(username) UNIQUE  
• equipment(tenant_id, type)  
• audit_log(tenant_id, created_at DESC)

────────────────────────────────────────────
8. Padrões de Migração e Seeds
────────────────────────────────────────────
• `alembic revision --autogenerate` monitorando models do SQLAlchemy  
• Seed inicial: tenant “default”, serviços de exemplo, usuário admin  
• Scripts de seed podem rodar após `alembic upgrade head` no mesmo entrypoint.

────────────────────────────────────────────
9. Estratégia de Backup e Retenção
────────────────────────────────────────────
• Dump lógico (`pg_dump`) diário; retenção 7 dias locais + 30 dias em S3  
• Tabela `audit_log` rodada para partições mensais e retenção 6 meses  
• Job de limpeza de tickets/receipts muito antigos (ex.: > 1 ano)

────────────────────────────────────────────
10. Próximos Passos
────────────────────────────────────────────
1. Aprovar entidades e campos com o time de produto.  
2. Implementar models SQLAlchemy e gerar migração inicial (já foi em parte).  
3. Ajustar serviços que ainda usam JSON plano ou armazenamento em arquivo para gravar no BD (ex.: recibos).  
4. Criar testes de integração:  
   • geração de ticket, chamada de fila, pagamento, recibo.  
5. Documentação ER-diagram (dbdiagram.io ou pgModeler) para compartilhar.

Com essa modelagem, o banco atende todos os fluxos atuais (fila, pagamentos, multi-tenant, operadores) e abre espaço para auditoria e escalabilidade futura.