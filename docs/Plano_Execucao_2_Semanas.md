# Plano de Execução: 2 Semanas para MVP em Produção

## 1. Prioridades Absolutas do MVP
Com base no Roadmap, foque nos épicos essenciais para o MVP funcionar em produção:

1. **Core-Ticket**  
   - CRUD de tickets  
   - Impressão ESC/POS  
   - Status machine (`pending`, `paid`, `called`)

2. **Pagamento-Link**  
   - Integração Sicredi (link/QR)  
   - Webhook de confirmação  
   - Idempotência

3. **Painel-WS**  
   - Push para operador/tablet  
   - Alertas visuais/sonoros

4. **LGPD-Consent**  
   - Captura de Nome, CPF, Tel  
   - Consentimento e criptografia

5. **Operator-Session**  
   - Login JWT  
   - Controle de equipamentos  
   - Exportação CSV diário

6. **Offline-Retry**  
   - Fila local e sync offline (mínimo viável)

7. **KPI-Dashboard**  
   - Endpoint `/metrics.csv`  
   - Exportação básica

---

## 2. Organização das Sprints

### Semana 1:
- **Dia 1-2:**  
  - Estrutura do monorepo (backend FastAPI, frontend React/Vite, Docker Compose)
  - Autenticação básica (JWT, multi-tenant)
  - CRUD tickets + impressão ESC/POS (Nada de dados mockados, é podução e escalabilidade)
- **Dia 3-4:**  
  - Integração Sicredi (link/QR, webhook)
  - Painel operador (push, alertas)
- **Dia 5:**  
  - LGPD: captura e consentimento
  - Testes unitários e integração mínima
  - Deploy em staging

### Semana 2:
- **Dia 6-7:**  
  - Operator session (login, controle, exportação)
  - Offline-retry (mínimo viável)
- **Dia 8-9:**  
  - KPI endpoint e exportação
  - Ajustes de UX, acessibilidade mínima
- **Dia 10:**  
  - Testes E2E, hardening, documentação rápida
  - Deploy produção

---

## 3. Dicas para Ganhar Velocidade
- **Reaproveite tudo da POC**: código, fluxos, integrações.
- **Automatize deploys**: use Railway, Supabase, Vercel.
- **Teste só o essencial**: priorize unitários e integração dos fluxos críticos.
- **Documente o mínimo viável**: README, endpoints, instruções de uso.
- **Use mocks/stubs** para integrações externas se necessário.
- **Comunique bloqueios rápido**: mantenha o cliente informado.

---

## 4. Checklist Diário
- [ ] O que está impedindo o deploy em produção?
- [ ] O que falta para o usuário final conseguir usar o MVP?
- [ ] O que pode ser mockado ou simplificado para ganhar tempo?
- [ ] O que pode ser automatizado (deploy, seed, reset)?

---

## 5. Próximos Passos Imediatos
1. **Confirme o que da POC pode ser aproveitado** (código, integrações, telas).
2. **Monte o esqueleto do monorepo** (se ainda não estiver pronto).
3. **Implemente o fluxo de ticket + pagamento + painel** (end-to-end, mesmo que simplificado).
4. **Garanta deploy automático em staging e produção**.
5. **Valide com o cliente o fluxo principal o quanto antes**.

---

Se quiser, posso ajudar a:
- Montar o esqueleto do monorepo (backend, frontend, Docker Compose)
- Gerar templates de PR, issues, runbooks
- Escrever código para os módulos principais (FastAPI, React, integração Sicredi)
- Criar scripts de deploy e automação 