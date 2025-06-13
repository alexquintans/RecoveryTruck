### Plano de Desenvolvimento Profissional & Escalável

**Sistema de Autoatendimento - Totem com Pagamento Integrado**
(Versão 0.1 – pronto para ser transformado em *roadmap* no Jira/Linear)

---

## 0. Premissas confirmadas

* **MVP** = Banheira de Gelo (3) + Bota de Compressão (3), sessão fixa 10 min&#x20;
* **Pagamento Fase 1** = Link/QR Sicredi + Webhook HTTPS; prioridade para depois suportar POS/API se disponível&#x20;
* **Hardware** = Tablet Android + Impressora ESC/POS; rede 4G com futura Starlink&#x20;
* **Escalabilidade** = 2 CNPJs hoje, horizonte de franquia (*food-truck*) e múltiplos totens por local&#x20;

---

## 1. Metodologia & Governança

| Item                   | Decisão                                                                        | Rationale                                           |
| ---------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------- |
| **Processo**           | Scrum enxuto, sprints de **1 semana**                                          | MVP curto; feedback rápido do cliente.              |
| **Boards**             | Linear ou Jira; épicos: *Core-MVP*, *POS-API R\&D*, *Operador-UX*, *Analytics* | Facilita visibilidade futura quando escalar.        |
| **Definition of Done** | *Merge = ✅ code review + ≥85 % tests unit + lint pass + preview deploy OK*     | Mantém qualidade contínua, não “inspeciona” no fim. |
| **Branching**          | *trunk-based* (`main`, `release/*`, feature branches <4 dias)                  | Minimiza drift e conflitos.                         |
| **Commits**            | Conventional Commits (`feat:`, `fix:`, `chore:`)                               | Automatiza `CHANGELOG` e semver tags.               |

---

## 2. Arquitetura evolutiva

| Camada            | MVP (monorepo Docker)                                                    | Estratégia de escala (Fase →)                                             |
| ----------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| **Frontend**      | React 18 + Vite PWA • `apps/totem` (kiosk) • `apps/operator` (tablet/TV) | Separar em workspaces, habilitar Module Federation p/ plug-ins.           |
| **Backend**       | FastAPI monolítico   • `tickets`, `payments`, `operators`, `auth`        | Extrair **payments** como microserviço quando integrarem 2+ adquirentes.  |
| **DB**            | PostgreSQL (Supabase free tier)                                          | Migrar para RDS/Aurora; particionar por `tenant_id`.                      |
| **Messaging**     | WebSocket (FastAPI)                                                      | Substituir por **NATS** ou **Redis PubSub** se >200 conexões simultâneas. |
| **Observability** | OpenTelemetry → Grafana Cloud (free)                                     | Retenção 90 d; ativar SLOs ao franquear.                                  |

* **Multi-tenant desde o dia 1** — todas as tabelas com `tenant_id`, extraído do JWT gerado quando o tablet faz bootstrap.

---

## 3. Qualidade de Software

| Pilar                   | Práticas adotadas                                                                                                                                                                       |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Código**              | PEP-8 via *ruff*, ESLint + Prettier, Husky pre-commit.                                                                                                                                  |
| **Testes**              | - *Pyramid*: 70 % **unit** (PyTest, Vitest), 20 % **contract** (Pact), 10 % **e2e** (Playwright).<br>- Test data builders para tickets/pagamentos.                                      |
| **CI/CD**               | GitHub Actions → Matrix (Python / Node). Steps: install → lint → test → build Docker → push to **Railway staging** on PR.<br>Tag `main` ➜ **Railway production** + Supabase migrations. |
| **Static Analysis**     | Bandit (security), DependaBot, CodeQL.                                                                                                                                                  |
| **Secrets**             | `.env` no Vault Railway; acesso por OIDC.                                                                                                                                               |
| **Performance Budgets** | Totem bundle ≤ 150 KB gzip; API p99 ≤ 150 ms (in-VPC).                                                                                                                                  |
| **Sustentabilidade**    | 1) Lazy-load módulos; 2) Database idle‐timeout 5 min; 3) Use *Autosleep* Railway; 4) Bulk writes; 5) Measure CO₂ via Cloud Carbon Footprint weekly.                                     |

---

## 4. Backlog high-level (12 épicos → decompostos em histórias)

| Épico                 | Critérios de aceite                                                                   | Size |
| --------------------- | ------------------------------------------------------------------------------------- | ---- |
| **Core-Ticket**       | POST/GET `/tickets` + impressão ESC/POS; status machine (`pending`, `paid`, `called`) | 3 SP |
| **Pagamento-Link**    | Cria link Sicredi, exibe QR, recebe webhook; idempotência proven                      | 5 SP |
| **Painel-WS**         | Operator tablet recebe push; beep/cores configuráveis por `service_type`              | 3 SP |
| **LGPD-Consent**      | Captura Nome + CPF + Tel + `terms_version`; AES-256 at rest                           | 2 SP |
| **Operator-Session**  | Login JWT, define `equipment_count`, inicia/encerra operação, exporta CSV diário      | 4 SP |
| **KPI-Dashboard**     | Endpoint `/metrics.csv`; Metabase container w/ 3 charts; cron daily job               | 3 SP |
| **Multi-Tenant-Base** | Middleware `x-tenant-id`; migrations; row-level policies Supabase                     | 4 SP |
| **Offline-Retry**     | Queue local (IndexedDB) + background sync se 4G cair, reenvia tickets/pagamentos      | 5 SP |
| **POS-API-P\&D**      | Spike integrar POS-API (Stone Connect) + PoC em sandbox                               | 2 SP |
| **Starlink-Latency**  | Load-test 700 ms RTT: ensure polling fallback, adjust timeouts                        | 2 SP |
| **Accessibility**     | Fonte ≥16 px, contraste AA, teclado virtual grande, som opcional                      | 2 SP |
| **Observability-v1**  | Tracing OpenTelemetry, Grafana dashboards, alert Slack when p95 >500 ms               | 3 SP |

*Total ≈ 38 SP; cabe em 6 sprints de 1 semana, mantendo buffer.*

---

## 5. Ambiente e automação

| Ambiente            | URL / infra                            | Regras                                            |
| ------------------- | -------------------------------------- | ------------------------------------------------- |
| **Local Dev**       | Docker Compose (db, api, front)        | `make up` abre tudo; hot-reload.                  |
| **Staging**         | Railway *starter plan*, supabase *dev* | Deploy each PR; seed with dummy data.             |
| **Prod**            | Railway *Hobby*, Supabase *pro* later  | Manual gate via GitHub Actions + tag.             |
| **Feature Preview** | Vercel branch deploy (frontend only)   | Link em PR p/ stakeholder revisar UI rapidamente. |

**IaC** → Terraform Cloud (free) controla Railway, Supabase, Grafana.

---

## 6. Segurança & Compliance

1. **LGPD**: base legal “execução de contrato”; banner consent; registros em tabela `consents`.
2. **PCI-DSS (nível 4)**: não manipulamos PAN; mascaramos `**** **** **** 1234`, armazenamos só `transaction_id`, `brand`.
3. **OWASP Top-10**: dependabot + zap baseline scan in CI.
4. **Backups**: Supabase WAL + Railway disk snapshot nightly; retenção 30 d.

---

## 7. Sustentabilidade & manutenção futura

* **Código modulável**: `domain/<bounded-context>` para poder extrair microserviços.
* **Plugin-ready Front**: `services.json` baixado em runtime permite adicionar novos tipos de serviço sem redeploy.
* **Schema versioning**: Alembic migrations semantic (`2025_06_12_add_tenant_id.py`).
* **Observabilidade**: error budget vs feature delivery; quartely *GameDay* (simulate 4G loss).
* **TechDebt register**: every retrospective includes `debt.md` grooming; max 15 % sprint capacity to debt-burn.

---

## 8. Kick-off checklist (D-0)

1. ✅ Criar repositório **evergreen/totem** com templates `.editorconfig`, `pre-commit`.
2. ✅ Provisionar Railway staging, Supabase dev, Grafana Cloud.
3. ✅ Registrar webhook endpoint `/payments/sicredi/callback` em sandbox.
4. ✅ Onboard time-tracker (Harvest) para estimativas reais de SP → h.
5. ✅ Agendar *Demo Friday* semanal com cliente (15 min).

---

### Próximo passo imediato

*Montar Sprint 0 (setup) no board hoje mesmo e marcar a demo do wireframe para daqui a **4 dias**.*

Precisa de *templates* (PR, issue, runbooks) ou de um **docker-compose.yml** startado? É só falar que entrego.


| **Tema** | **Perguntas-chave** | **Resposta do cliente** |
|---|---|---|
| **Serviços & Preços** | • Quais serviços estarão disponíveis?<br>• Valor de cada serviço? Preço fixo, por tempo ou pacote? | Dois serviços: Banheira de Gelo e Bota de Compressão, com **3 equipamentos de cada (total 6)**. Sessão fixa de **10 min**. |
| **Pagamento** | • Qual adquirente/maquininha?<br>• Contrato ativo / sandbox?<br>• Métodos aceitos?<br>• Precisa NF-e / NFC-e? | Usará **maquininha Sicredi** (quer flexibilidade para outras). Métodos: **débito, crédito, PIX, aproximação**. |
| **Hardware do Totem** | • Modelo do dispositivo?<br>• Tamanho/resolução da tela?<br>• Impressora térmica?<br>• Som/câmera? | **Tablet Android** como totem, com **impressora ESC/POS** para senhas. |
| **Ambiente de Rede** | • Wi-Fi, cabo ou 4 G?<br>• Restrições de porta/firewall?<br>• Comportamento em queda de internet? | Conexão via **chip 4 G**; futura opção **Starlink**. |
| **Fila & Painel** | • Nº de totens e painéis?<br>• Serviços misturados ou separados?<br>• Alerta sonoro/visual?<br>• Layout (cores, logo)? | Hoje **1 totem : 1 painel**. Prefixo, cor e som distintos por serviço serão usados. |
| **Escalabilidade** | • Mais unidades na mesma fila?<br>• Totens futuros sem reconfiguração? | Planeja **franquear (food-truck)**; MVP portátil, mas preparado para escala. **Dois CNPJs** já mapeados. |
| **Dados do Cliente Final** | • Solicitar CPF, e-mail ou telefone?<br>• Política LGPD disponível? | Coletará **Nome, CPF e Celular**; termo de consentimento será exibido. |
| **Design & Conteúdo** | • Manual de identidade visual?<br>• Textos de instrução, idiomas?<br>• Acessibilidade necessária? | Marca **RecoveryTruck** em rebranding; detalhes visuais virão depois. |
| **Legais & Contratuais** | • Termo/contrato de uso no totem?<br>• Requisitos PCI-DSS extras? | Possui **termo de responsabilidade**; aceite será salvo no banco. |
| **Relatórios & Métricas** | • Indicadores a acompanhar?<br>• Periodicidade e formato? | KPIs simples: **tickets/hora, tipo, faturamento diário/mensal**; exportável em CSV/PDF. |
