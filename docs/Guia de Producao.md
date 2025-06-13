### Guia Rápido — Do Zero ao Totem em Produção

*(Qualidade • Sustentabilidade • Escalabilidade – versão 1.0)*

---

#### 1. Preparação (Dia 0)

| Ação                                            | Ferramenta   | Resultado                                             |
| ----------------------------------------------- | ------------ | ----------------------------------------------------- |
| Crie repositório **mono-repo** (`totem/`)       | GitHub       | Base única → fácil refatorar em micro-serviços depois |
| Defina **Roadmap** (épicos + sprints)           | Linear/Jira  | Visibilidade e capacidade de medição                  |
| Abra **doc de arquitetura viva** (`/docs/adr/`) | ADR markdown | Cada decisão registrada → evita “por que fizemos?”    |

---

#### 2. Ambiente Dev (Dia 1–2)

1. `git clone` + `make up` → **Docker Compose** com:

   * `api` (FastAPI)
   * `frontend-totem` (React PWA)
   * `frontend-operator`
   * `db` (PostgreSQL)
2. **Seeder**: `scripts/dev_seed.py` cria 3 tickets demo.
3. **Pre-commit hook**: Ruff (Python), ESLint + Prettier (JS).

---

#### 3. Convenções de Código

| Tema          | Regra                                  | Checagem      |
| ------------- | -------------------------------------- | ------------- |
| Commits       | Conventional Commits (`feat:`, `fix:`) | Husky         |
| Estilo Python | Ruff + Black                           | CI            |
| Estilo TS/JS  | ESLint + Prettier                      | CI            |
| Arquitetura   | Clean-ish: `domain/`, `infra/`, `api/` | Código-review |

---

#### 4. Testes Mínimos

| Camada               | Ferramenta                      | Cobertura alvo              |
| -------------------- | ------------------------------- | --------------------------- |
| Unitário             | PyTest / Vitest                 | ≥ 70 %                      |
| Contrato (Pagamento) | **Pact**                        | 100 % de endpoints externos |
| E2E crítico          | **Playwright** (seleção→ticket) | Smoke suite                 |

---

#### 5. CI/CD Pipeline

1. **GitHub Actions**:

   ```yaml
   lint → test → build → docker push :staging → e2e smoke
   ```
2. `main` tag = produção; gate manual de 1 clique.
3. **Docker multi-arch** (arm64 & amd64) → roda em Raspberry ou VPS x86.

---

#### 6. Observabilidade & Qualidade em Execução

| Item             | Stack                               | Sustentável porque…          |
| ---------------- | ----------------------------------- | ---------------------------- |
| Logs             | Otel → Grafana Cloud free           | Centralizado, retém 30 d     |
| Métricas         | `/metrics` Prometheus               | Orquestra autoscaling futuro |
| Tracing          | FastAPI middleware Otel             | Identifica gargalos cedo     |
| Carbon footprint | cloudcarbonfootprint.org CLI weekly | Relatório CO₂ ação simples   |

---

#### 7. Segurança & LGPD

1. **Dados sensíveis** (CPF) → coluna PG `ENC BY DEFAULT`.
2. **Segredos** → Railway/Vercel built-in secrets, nunca no Git.
3. **OWASP ZAP baseline** roda em CI.
4. Webhook Sicredi assinados HMAC + idempotência (`uniq(transaction_id)`).

---

#### 8. Performance & Escala

| Limite inicial  | Plano quando exceder                               |
| --------------- | -------------------------------------------------- |
| 200 WS conexões | Migrar WS para NATS JetStream                      |
| 10 k tickets/d  | Mover Postgres para RDS + partição por `tenant_id` |
| 150 ms p99 API  | Add CDN edge cache para assets PWA                 |

---

#### 9. Deploy Produção (Dia 15–20)

1. **Railway** for backend + Supabase (pg + storage).
2. **Vercel** para front (auto-static opt).
3. **Blue-Green**:

   * `prod-v1` live → deploy `prod-v2` → health-check → switch CNAME.
4. **Backup**: WAL + snapshot diárias; cron “verify-restore” semanal.

---

#### 10. Operação Contínua

| Ritmo      | Ação                                 |
| ---------- | ------------------------------------ |
| Diário     | Check dashboard erros & p95          |
| Semanal    | Groom backlog + 15 % dívida técnica  |
| Mensal     | Re-estimativa de CO₂ & custo infra   |
| Trimestral | GameDay: simular 4 G off-line 30 min |

---

**Pronto.** Siga os passos na ordem, registre decisões em ADRs e mantenha o pipeline verde; você terá um MVP de qualidade, barato de rodar e preparado para franquear sem retrabalho pesado.


### Sequência “faça-isso-depois-isso” — 0 → Produção

*(20 dias úteis, passo a passo, direto ao ponto)*

| Dia útil  | Entregável                 | O que você faz, na ordem exata                                                                                        |
| --------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **0**     | Kick-off                   | • Reunião de 30 min para rever escopo.<br>• Cria repositório **mono-repo** (`totem/`).                                |
| **1**     | Ambiente dev               | • `docker-compose up` com FastAPI, React (Totem + Operador) e Postgres.<br>• Adiciona pre-commit (Ruff, ESLint).      |
| **2**     | CI/CD básico               | • GitHub Actions: lint → testes → build Docker → push **staging** (Railway).                                          |
| **3**     | Modelo de dados            | • Tabela `services`, `tickets`, `payments`, `operators` (inclui `tenant_id`).<br>• Migrações Alembic.                 |
| **4**     | API Tickets                | • `POST /tickets` + status machine (`pending`, `paid`).<br>• PyTest unit + contract tests.                            |
| **5**     | UI Totem – Seleção         | • Tela: escolher serviço → confirma → mostra QR (mock).<br>• Playwright e2e (seleção gera ticket).                    |
| **6**     | Integração Sicredi (link)  | • Endpoint `POST /payments/link` cria QR via sandbox.<br>• Recebe webhook; grava `transaction_id`; idempotência.      |
| **7**     | Impressão & Senha          | • Gera número autoincremento.<br>• ESC/POS impressão; fallback PDF se sem impressora.                                 |
| **8**     | WebSocket & Painel         | • WS FastAPI → Operador tablet recebe e mostra fila.<br>• Beep/cores por serviço configurados em `services` table.    |
| **9**     | Operador: iniciar/encerrar | • Login JWT.<br>• “Iniciar operação” define nº de aparelhos.<br>• Botão “Atender / Encerrar” altera `tickets.status`. |
| **10**    | Dados pessoais + LGPD      | • Form captura Nome, CPF, Cel.<br>• Criptografa CPF; salva `consent_version` + timestamp.                             |
| **11**    | Relatório diário           | • Cron job `00:05` gera CSV do dia D-1; armazena em Supabase storage; link para download no painel.                   |
| **12**    | Observabilidade            | • OpenTelemetry log + trace → Grafana Cloud free.<br>• Dashboard p95 latência + erros 4xx/5xx.                        |
| **13**    | Tests & hardening          | • Playwright full smoke (seleção→pago→chamado).<br>• ZAP baseline scan in CI.<br>• Final code-review (DoD).           |
| **14**    | Staging demo               | • Envia URL staging + usuário demo para cliente testar.<br>• Corrige feedback alto nível (UI, copy).                  |
| **15**    | Blue-Green prod            | • Railway `prod-v2` up → health-check → switch CNAME.<br>• Frontend Vercel tag `production`.                          |
| **16–17** | Checklists                 | • Backup script verificado.<br>• Retry offline (4 G drop) validado.<br>• Docs README + ADR completados.               |
| **18**    | Treinamento                | • Grava Loom 5 min Totem + 5 min Operador.<br>• Manual PDF (10 pág).                                                  |
| **19**    | Go-Live                    | • Cliente usa em operação real.<br>• Monitor p95 + webhook idempotência logs.                                         |
| **20**    | Retro & hand-off           | • Sprint retro.<br>• Abre board “Fase 2: POS-API” e “Sugestões operador”.<br>• Inicia suporte de 15 dias.             |

**Regras de ouro enquanto executa:**

1. **Merge only on green CI** – evita surpresas na build de produção.
2. **Cada dia útil = commit tag semver patch** – rollbacks simples.
3. **“Done” = rodou em staging + teste Playwright passou** – sem exceções.
4. **Documente decisão em `docs/adr/YYYY-MM-DD-slug.md`** – 5 linhas basta.
5. **Mantra de escala**: toda query filtra por `tenant_id`; toda feature nova mede p95 antes de lançar.

Siga a lista exatamente e você sai do zero para produção com qualidade, sustentabilidade e já preparado para crescer.


[X] Estrutura inicial dos diretórios e arquivos (FastAPI, React/Vite, Docker, Compose)
[X] docker-compose.yml para orquestrar tudo
[ ] Dockerfiles para cada serviço
[X] README.md com instruções mínimas
[ ] .env.example para variáveis de ambiente
[X] Endpoint de healthcheck no backend
[X] Frontend totem e operador com tela inicial (React/Vite)
[ ] Banco PostgreSQL rodando e acessível

--------------------------

1. Modelo de Dados e Banco
Criar tabelas essenciais:
services (Banheira de Gelo, Bota de Compressão)
tickets (com status machine: pending, paid, called)
payments (integração Sicredi)
operators (multi-tenant)
consents (LGPD)

---
Criar migrations Alembic
Implementar modelos SQLAlchemy
Adicionar validações Pydantic
Configurar criptografia de dados sensíveis
Implementar políticas de acesso
---

2. Backend (FastAPI)
Implementar endpoints:
POST /tickets (criar ticket)
GET /tickets (listar tickets)
POST /payments/link (gerar QR Sicredi)
POST /payments/webhook (receber confirmação)
GET /metrics.csv (KPIs)

3. Frontend Totem
Telas principais:
Seleção de serviço
Captura de dados (Nome, CPF, Tel)
Exibição do QR de pagamento
Tela de sucesso/aguardando

4. Frontend Operador
Telas principais:
Login
Painel de fila (WebSocket)
Controle de atendimento
Exportação CSV e .pdf

5. Integrações
Sicredi (pagamento), preparar para ser possivel integrar com outras operadoras de máquinas
Impressora ESC/POS
WebSocket para fila
6. Segurança & LGPD
Criptografia de dados sensíveis
Termo de consentimento
Autenticação JWT
7. Observabilidade
Logs
Métricas
Tracing


------
Integrações:
Implementar WebSocket
Configurar impressora
Frontend:
Criar telas do totem
Criar telas do operador
Implementar autenticação
------

Implementar Circuit Breaker e Retry
Adicionar resiliência nas chamadas à API
Configurar timeouts adequados
Implementar fallback para falhas
Monitorar métricas de disponibilidade
Implementar Logging e Monitoramento
Adicionar logs estruturados
Integrar com OpenTelemetry
Criar dashboards no Grafana
Configurar alertas para falhas
Implementar Impressão de Comprovante
Integrar com impressoras ESC/POS
Criar templates de comprovante
Implementar fila de impressão
Adicionar retry para falhas de impressão
Implementar Offline Mode
Criar fila local (IndexedDB)
Implementar sincronização em background
Adicionar indicador de status de conexão
Garantir idempotência nas transações
Melhorar Segurança
Implementar rotação de chaves
Adicionar rate limiting
Implementar validação de certificados
Adicionar auditoria de transações
Documentação Adicional
Criar documentação de API (OpenAPI/Swagger)
Adicionar exemplos de integração
Criar guia de troubleshooting
Documentar procedimentos de rollback
Implementar Analytics
Adicionar métricas de transações
Criar relatórios de performance
Implementar dashboards de negócio
Adicionar exportação de dados