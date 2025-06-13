Abaixo está um roteiro objetivo para transformar a proposta em execução concreta — do alinhamento com o cliente na reunião de segunda-feira até a entrega em produção. Mantive a linguagem mais direta possível e sempre que houve trade-offs incluí observações rápidas de custo/complexidade.

---

## 1. Checagem Rápida para a Reunião de Segunda

Leve estas perguntas (se algo já estiver decidido, risque):

| Tema                    | Perguntas-chave                                                                                                                    | Por quê                                                       |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Hardware do totem**   | - Qual modelo/dispositivo será usado (Raspberry Pi, Intel NUC, Android “box”)?<br>- Dimensão/touch? Navegador em modo kiosk?       | Define SO, drivers, resolução e performance da UI.            |
| **Operadora de cartão** | - Qual adquirente/POS? (Stone, Cielo, SumUp etc.)<br>- A maquininha já possui API cloud ou será pareada por Bluetooth?             | API e SDK variam; impacta prazo de homologação.               |
| **Valor dos serviços**  | - Preço fixo por serviço ou variável?<br>- Tributação (criar recibo ou NFC-e)?                                                     | Precisamos enviar valor exato para POS.                       |
| **Política de fila**    | - Ticket numérico simples (001, 002…) ou segmentado por serviço (A001, B001)?<br>- É necessário reimprimir/comandar cancelamentos? | Modela as tabelas de fila e UX do painel.                     |
| **Múltiplos totens**    | - Haverá mais de um totem falando com a mesma fila?<br>- Local único ou várias unidades?                                           | Decide se usamos Supabase em nuvem ou DB local/off-line sync. |
| **Painel de chamada**   | - Será exibido em TV existente (navegador) ou monitor adicional?<br>- Som / beep ao chamar? Branding (logo)?                       | Ajustes de front-end e acessibilidade.                        |
| **Suporte pós-go-live** | - SLA e canal (WhatsApp, e-mail)?<br>- Quem reinicia aplicação/hardware no local?                                                  | Define extensão de suporte além dos 15 dias.                  |

---

## 2. Arquitetura de Alto Nível

```
[Totem Touch React] ─┐
                     ├──► [API Gateway (FastAPI)] ──► [PostgreSQL/Supabase]
[Admin Painel Web] ──┘                               ▲
                                                     │
                       [WebSocket] ◄─────────────────┘
                          │
                    [Painel TV/Monitor]
                          │
                    [REST ↔ POS Cloud API]
```

* **Totem**: navegador em modo kiosk; app React + Service Worker para eventual off-line e recuperação de sessão.
* **Backend**: FastAPI containerizado (Docker) → fácil deploy em VPS ou Railway.
* **Fila**: tabela `tickets` (id, service\_type, status, created\_at, paid\_at).
* **WebSocket**: FastAPI + `uvicorn` broadcasting; TV recebe “próximo número” em tempo real.
* **Pagamento**: se o adquirente tiver API cloud (Stone Connect, Cielo LIO, SumUp Kiosko) enviamos `amount` e recebemos webhook de confirmação; se for POS Bluetooth, tratamos via SDK local.
* **CI/CD**: GitHub → Docker build → Railway/Vercel autodeploy + .env secrets.

---

## 3. Plano de Desenvolvimento (20 dias úteis)

| Dia útil  | Entregável                          | Principais tarefas                                                                                                                                     | Responsável  |
| --------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ |
| **0-1**   | Kick-off + Especificação detalhada  | • Validar respostas das perguntas acima.<br>• Desenhos rápidos de fluxo (Figma, FigJam).                                                               | PM + UX      |
| **2-3**   | Ambiente base                       | • Repos (frontend, backend).<br>• Docker compose dev.<br>• Supabase/schema inicial.                                                                    | DevOps       |
| **4-7**   | **Sprint 1 – UI & Core Fila**       | • Tela de seleção de serviço.<br>• Geração de ticket e impressão (PDF ou ESC/POS).<br>• Endpoint `/tickets` (POST/GET).                                | Front + Back |
| **8-11**  | **Sprint 2 – Painel & WebSocket**   | • Painel em Next.js simples em tela cheia.<br>• Canal WS “call\_next”.<br>• Endpoint `/call/{ticket}` que emite WS.<br>• Teste simultâneo multi-totem. | Full-stack   |
| **12-16** | **Sprint 3 – Integração Pagamento** | • Mock API → troca com POS real.<br>• Tratamento de sucesso/falha/cancelamento.<br>• Webhook → update `paid_at`.<br>• Retentativa em rede instável.    | Back         |
| **17-18** | QA & Hardening                      | • Teste de estresse fila (Locust).<br>• Teste de desconexão de WS.<br>• Ajustes de UX (botões grandes, fonte, contraste).                              | QA/UX        |
| **19**    | Deploy piloto                       | • Subir instância em VPS.<br>• Instalar app no totem (kiosk script).<br>• Checklist de hardware.                                                       | DevOps       |
| **20**    | Treinamento & Handover              | • Manual de uso (PDF + Loom vídeo).<br>• Pack de logotipos/painel customizado.<br>• Reunião de entrega.                                                | PM           |

*Buffer*: +3 dias corridos para homologação da API de pagamentos, caso a adquirente exija chave de produção só após análise.

---

## 4. Recursos e Custos Internos (Referência)

| Item                          | Custo estimado             | Observações                           |
| ----------------------------- | -------------------------- | ------------------------------------- |
| VPS (Railway 1 GB)            | \~US\$ 5/mês               | Escala até 10 k tickets/dia.          |
| Supabase (free tier)          | R\$ 0                      | Up to 500 MB; pagar ao escalar.       |
| Licença POS Cloud             | varia (Stone \~R\$ 60/mês) | Confirmar com cliente.                |
| Impressora térmica (opcional) | R\$ 350                    | Caso ticket impresso seja necessário. |
| Horas/homem (já no fee)       | —                          | 80 h dev, 16 h QA, 8 h PM.            |

---

## 5. Riscos e Mitigações

| Risco                        | Impacto            | Mitigação                                                                                         |
| ---------------------------- | ------------------ | ------------------------------------------------------------------------------------------------- |
| *API POS demora liberação*   | Atraso no Sprint 3 | Trabalhar com mock → alternar para adquirente que libera chave sandbox imediatamente.             |
| *Totem sem CPU suficiente*   | UI lenta           | Testar build React em hardware final até o Dia 7; opção Lite (PWA) se necessário.                 |
| *Falhas de internet*         | Pagamento/off-line | Implementar fila local com retry; exibir QR-code PIX como fallback.                               |
| *Tickets impressos atolando* | Atendimento parado | Se optar por impressão, usar impressora de kiosk testada (>180 mm/s) e incluir rotina de limpeza. |

---

## 6. Próximas Ações (antes de segunda)

1. **Revise a lista de perguntas** e já colete o máximo de detalhes com o cliente por WhatsApp para ganhar tempo.
2. Prepare um **Miro/FigJam** com o wireframe do totem (tela de seleção + ticket) e do painel TV → leve como “visual sneak peek”.
3. Abra os repositórios e configure o **Docker boilerplate** para mostrar profissionalismo no call (“infra já pronta, só falta validar critérios”).
4. Traga **duas opções de adquirentes** (ex.: Stone Connect vs. SumUp Kiosko) com prós/contras (custo, homologação, disponibilidade de API).
5. Tenha pronto um **roadmap visual de 3 sprints** para usar no compartilhamento de tela; reforça transparência de prazos.

Com esse plano você entra na reunião mostrando clareza de execução, reduz incertezas do cliente e cria um cronograma que bate com a proposta de 15-20 dias úteis e valor de R\$ 3.500,00. Qualquer ajuste fica fácil de evidenciar onde mexe no escopo, prazo ou custo.


Ele **parece** simples quando olhamos só para a tela de “Escolher serviço → Pagar → Mostrar senha”, mas há três pontos que costumam transformar um “sisteminha” em algo que consome mais tempo do que o esperado:

| Área                            | Por que complica                                                                                                                                                                                        | Como simplificar sem perder qualidade                                                                                                                                                                                 |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Integração com POS**          | • Cada adquirente expõe uma API ou SDK diferente; algumas exigem homologação, certificação PCI e contrato. <br>• O POS precisa receber o valor, aguardar a transação e devolver o status (sincronismo). | • Escolher uma maquininha **que já ofereça API REST pública** (ex.: Stone Connect, SumUp Kiosko) — nada de Bluetooth ou SDK fechado. <br>• Limitar métodos de pagamento: cartão chip + aproximação, sem parcelamento. |
| **Sincronização fila ↔ painel** | • Vários totens/filas geram concorrência (ticket duplicado, ordem trocada). <br>• É comum surgirem bugs de “pular” ou repetir senha se a lógica não for atomizada.                                      | • Usar **auto-incremento do banco** como número da senha (garante unicidade). <br>• WebSocket simples: se cair a conexão, o painel faz polling a cada 3 s.                                                            |
| **Robustez off-line**           | • Se a rede cair entre “pagar” e “salvar OK”, você pode cobrar o cliente e perder o ticket. <br>• POS pode estar on-line, mas seu backend não.                                                          | • Gravar o ticket **antes** de chamar o POS e marcar o status como `pending_payment`. <br>• Se o POS confirma, atualizar; se falhar, mostrar mensagem “procure o atendente”.                                          |

### O que realmente é “complexo”?

* **Controle transacional** entre pagamento e liberação de senha (evitar ticket sem pagamento ou pagamento sem ticket).
* **Exibições em tempo real** (WebSocket) — não é difícil, mas precisa pensar em reconexão.
* **Segurança & LGPD** se for gravar dados pessoais (e-mail, CPF para NF).
* **Escalabilidade** caso amanhã queiram 10 totens em rede.

### Caminho mínimo viável (MVP) — 5 passos

1. **Totem PWA** em React, rodando em modo kiosk.
2. **Backend FastAPI** com apenas três endpoints:

   * `POST /tickets` (gera ticket `pending_payment`)
   * `POST /payment-callback` (webhook do POS)
   * `GET /next` (painel puxa o próximo chamado)
3. **Fila simples** no Postgres: `id SERIAL, service ENUM, status ENUM, created_at, paid_at`.
4. **Painel TV** = página HTML que faz polling; WebSocket pode vir depois.
5. Escolher **uma** adquirente com sandbox aberto, subir em staging e testar fluxo ponta-a-ponta.

Se ficar só nisso, é um CRUD + webhook — nada fora do comum para equipe que já domina React/Node/Python. O ponto é alinhar com o cliente que:

* **Funcionalidades “extra”** (parcelamento, cancelamento, impressão, multi-unidade) **aumentam complexidade** e devem entrar como fases futuras.
* O valor de R\$ 3.500,00 cobre esse MVP básico; qualquer integração extra ou SLA estendido reprecifica.

**Resumo:** o núcleo do sistema não é grande, mas integração de pagamento em ambiente de produção sempre merece atenção. Mantendo escopo enxuto e escolhendo uma adquirente amigável, dá para entregar em \~2 semanas, como previsto.


### Cenário-modelo: onde moram os abacaxis

> **Fluxo resumido**
>
> 1. Usuário toca no serviço → 2. Sistema cria *ticket pending-payment* → 3. POS cobra → 4. POS devolve **OK** (webhook) → 5. Ticket vira *paid* e entra na fila → 6. Painel chama ticket.

Aparentemente linear, esse fluxo atravessa **quatro domínios críticos** (UI -> backend -> adquirente -> fila em tempo real). É neles que você deve concentrar cuidados de engenharia.

---

## 1. Escopo & Expectativas

| Pergunta                         | Impacto                                         | Ação prática                            |
| -------------------------------- | ----------------------------------------------- | --------------------------------------- |
| Há limite de totens simultâneos? | Concorrência (tickets duplicados)               | Auto-incremento no DB + transação.      |
| Precisa emitir NF-e / NFC-e?     | Integração fiscal + impressão                   | Planejar fase 2 ou usar gateway fiscal. |
| Multi-serviço futuro?            | Campos extras na tabela (`service_id`, `price`) | Deixar modelagem “service-agnostic”.    |

---

## 2. UX e Interface Física

* **Área de toque grande** com *hit target* ≥ 48 px (evita toques duplos na pressa).
* **Modo kiosk** bloqueado: browser sem barra de endereço, desativa ALT-TAB.
* **Estados visíveis**: *Selecionando* → *Aguardando Pagamento* (loading) → *Pagamento Aprovado / Falhou*.
* **Fallback**: se POS não responde em 15 s mostre QR-Code PIX e permita re-tentativa.

---

## 3. Integração com POS (maquininha)

| Cuidados                     | Como mitigar                                                |
| ---------------------------- | ----------------------------------------------------------- |
| **Idempotência do webhook**  | guarde `transaction_id` → ignore duplicatas.                |
| **Time-out / perda de rede** | ticket segue `pending_payment`; CRON reconsulta status.     |
| **Versão da API**            | **pin** versão no header; monitore changelog da adquirente. |
| **PCI DSS / LGPD**           | nunca armazene PAN; log só masked (`**** **** **** 1234`).  |

---

## 4. Modelo de Dados Essencial

```sql
TABLE tickets (
  id            SERIAL PRIMARY KEY,
  service       VARCHAR(30) NOT NULL,
  price_cents   INT NOT NULL,
  status        ENUM('pending_payment','paid','called','done','cancelled') DEFAULT 'pending_payment',
  pos_tx_id     VARCHAR(50),
  created_at    TIMESTAMP DEFAULT now(),
  paid_at       TIMESTAMP,
  called_at     TIMESTAMP
);
```

*Transação*: `BEGIN; INSERT ticket … RETURNING id; COMMIT;` — só depois chama POS.

---

## 5. Confiabilidade & Desempenho

* **WebSocket com TTL**: se cair, frontend faz *poll* `/next` a cada 3 s.
* **Fila local em RAM** no painel para evitar “eco” na TV (chama duas vezes).
* **Healthcheck**: endpoint `/health` para Kubernetes / Railway (retorna DB & POS).
* **Watchdog** no totem: script systemd que reinicia browser se congelar.

---

## 6. Segurança operacional

| Vetor           | Proteção                                                   |
| --------------- | ---------------------------------------------------------- |
| Chaves da API   | `.env` criptografado + secret manager da cloud.            |
| Hardening do SO | Usuário sem sudo, portas fechadas, auto-update desativado. |
| Log & Auditoria | Loki / Papertrail; retenção mínima 90 dias.                |

---

## 7. Monitoramento & Métricas

* **KPIs úteis ao cliente**: tempo médio de fila, tickets por hora, abandonos.
* Exponha `/metrics` (Prometheus) → Grafana; ou use serviço gratuito (Railway metrics).

---

## 8. Testes recomendados

| Tipo             | Ferramenta                   | Objetivo                                        |
| ---------------- | ---------------------------- | ----------------------------------------------- |
| **Unitário**     | pytest / vitest              | Valida regras de fila e cálculo de preço.       |
| **Integração**   | docker-compose + POS sandbox | Garante handshake completo.                     |
| **Stress**       | Locust                       | 200 rps, 4 totens, 1 painel.                    |
| **Exploratório** | Cypress (UI)                 | Fluxos de erro: cancel, time-out, double-click. |

---

## 9. Deploy & Atualizações

* **Imutável**: cada release gera imagem Docker com tag semântica (`v1.3.0`).
* **Blue-green** em Railway ou Fly.io → zero downtime.
* **Totem autoupdate**: script `git pull && pm2 restart` agendado de madrugada.

---

## 10. Legislação brasileira

* LGPD: se coletar CPF/e-mail, exibir aviso de consentimento e política resumida.
* Se emitir nota: circular 09/2023 SEFAZ - NFC-e offline máximo 24 h; planeje sync.

---

### Checklist “antes de dar play”

1. 🔲 Definido **adquirente** e acesso à sandbox.
2. 🔲 Validadas **exigências fiscais** (nota ou recibo simples?).
3. 🔲 Confirmado **hardware** (CPU, impressora, som).
4. 🔲 Owners de **monitoramento / suporte** definidos (e-mail on-call).
5. 🔲 Termo de aceite descrevendo **limitações do MVP** (sem parcelamento, etc.).

---

**Heurística simples:**
*Se algo envolve dinheiro em tempo real (POS) ou “quem é o próximo da fila” (concorrência), trate como missão crítica.*
Todo o resto (cores, animação, beep de chamada) pode falhar graciosamente sem prejudicar o negócio.

Com esses cuidados de modelagem você reduz imprevistos caros, mantém o escopo do ticket enxuto e cria base sólida para evoluções futuras (multi-unidade, serviços extras, novos meios de pagamento).


# O projeto:
Sistema de autoatendimento para totens com pagamento integrado  

Descrição do Projeto:
Sistema para totens de autoatendimento.

Preciso de um sistema para totens portáteis com as seguintes funcionalidades:

• Seleção de serviços (banheira de gelo ou bota de compressão);
• Geração de ticket para atendimento;
• Painel de chamada exibindo o número do cliente;
• Integração com maquininha de cartão para pagamento imediato.

O foco é oferecer uma experiência rápida e fluida para o cliente, com interface simples e responsiva

# Minha proposta para o projeto:
Proposta Comercial – Sistema de Autoatendimento para Totens com Pagamento Integrado
Empresa Responsável: Evergreen ((http://www.evergreenmkt.com.br))

A Evergreen é especializada no desenvolvimento de sistemas sob medida com foco em experiência do usuário, automação e integração de pagamentos. Entregamos soluções funcionais e intuitivas que otimizam o atendimento presencial com tecnologia estável, rápida e fácil de operar.

O projeto descrito visa criar um sistema de autoatendimento para totens portáteis, com funcionalidades de seleção de serviços, geração de tickets, painel de chamada e pagamento por cartão — com foco total na agilidade e simplicidade da jornada do cliente.



Funcionalidades a Desenvolver:

1. Tela de Seleção de Serviço

* Interface amigável e responsiva
* Opções: *banheira de gelo* ou *bota de compressão*
* Confirmação rápida para evitar filas

2. Geração de Ticket e Fila de Atendimento

* Geração automática de senha/ticket com número sequencial
* Armazenamento local ou em nuvem (caso deseje integração entre unidades)

3. Painel de Chamada

* Painel web com design limpo para exibição em TV/monitor
* Atualização automática com número do próximo cliente

4. Integração com Maquininha de Cartão

* Integração com POS via API (ex: Stone, Cielo, SumUp, Gerencianet, etc.)
* Pagamento no final da escolha, com envio automático do valor
* Confirmação automática após pagamento para liberar ticket


Como será desenvolvido:

* Frontend (interface do totem): React.js
* Backend (controle de fila e pagamento): Node.js com Express ou Python (FastAPI)
* Banco de dados: Supabase ou PostgreSQL (leve e rápido)
* Painel de chamada: aplicação web acessada por navegador
* Integração com maquininha: via API REST da operadora escolhida (cliente define ou fornecemos opções)


Entregáveis

* Sistema completo para usar em totens
* Código-fonte documentado
* Manual de uso
* Suporte por 15 dias após entrega

Prazo de entrega:
15 a 20 dias úteis, dependendo da disponibilidade da API da maquininha e ajustes no fluxo.


Investimento:
R$ 3.500,00 (valor fixo)
Inclui:
* Design e desenvolvimento completo do sistema
* Integração com API de pagamento
* Testes e deploy

Diferenciais Evergreen:

* Especialistas em automação de atendimento e UX para soluções autônomas
* Experiência com integração de meios de pagamento e filas automatizadas
* Sistema leve, rápido e fácil de escalar para múltiplas unidades



### Análise das novas respostas (versão “melhorada”) e impactos no planejamento

*(todas as citações referem-se ao PDF do cliente)*

| Tema                       | Situação após as novas respostas                                                                                                                | Pontos ainda em aberto / próximos passos                                                                                                                 | Ações recomendadas                                                                                                                                  |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Serviços & Preços**      | - Dois serviços, **3 equipamentos de cada** (total 6).<br>- Sessão fixa de **10 min**.                                                          | 1. Valores de cada sessão.<br>2. Futuras variações (30 min? combos?).                                                                                    | Criar tabela **`services`** já com campo `price_cents` e `max_parallel_units`.                                                                      |
| **Pagamento**              | - **Sicredi** como adquirente principal; quer flexibilidade futura para outras máquinas.<br>- Métodos: débito, crédito, **PIX** e aproximação.  | 1. **Confirmação oficial** de que o modelo de POS Sicredi possui API/TEF para disparo remoto.<br>2. Caso **não** exista: cliente aceita link/QR Sicredi? | ▸ Continuar o *plano B* (link QR + webhook).<br>▸ Estruturar camada de *gateway* de pagamentos (abstração) para suportar outros adquirentes depois. |
| **Hardware**               | - Totem = **tablet Android** + **impressora** de senhas.                                                                                        | 1. Modelo Android (versão / CPU) e se permite **modo kiosk**.<br>2. Marca/driver da impressora térmica (ESC/POS?).                                       | ▸ Validar driver WebUSB/ESC-POS.<br>▸ Caso não plug-and-play: gerar PDF da senha e usar app nativo para impressão.                                  |
| **Rede**                   | - 4G agora, **Starlink** futuramente.                                                                                                           | Confirmar **franquia de dados** 4G para cálculo de custos; latência Starlink (\~700 ms) tolerável com polling de 2–3 s.                                  | ▸ Ajustar time-outs do WebSocket ↔ fallback polling.<br>▸ Implementar **retry** offline para Webhooks.                                              |
| **Fila & Painel**          | - **1:1** (tablet cliente vs tablet operador).<br>- Quer **prefixos/cores** distintos + **som**.                                                | Precisa **voz sintetizada** ou apenas beep?<br>Define paleta/códigos de cor (virão com o rebranding).                                                    | ▸ Incluir parâmetro `service.color` e `service.sound`.<br>▸ Planejar MP3 curto (licença free).                                                      |
| **Escalabilidade**         | - Objetivo futuro de **franquia** (food-truck), com **2 CNPJs** iniciais.<br>- MVP portátil, 1 equipamento por vez.                             | Concorda em começar **single-tenant** com campo `tenant_id` “hard-coded” e migrar para RBAC depois?                                                      | ▸ Modelar `tenant_id` desde já (mesmo se =1).<br>▸ Gerar QR de provisionamento que injeta `tenant_id` no tablet na primeira execução.               |
| **Dados do cliente final** | Nome, **CPF** e celular capturados.                                                                                                             | Fornecer **texto de consentimento LGPD**; onde exibir (tela ou termo impresso).                                                                          | ▸ Criptografar CPF no banco (AES-256).<br>▸ Logar data/hora do aceite com hash do termo.                                                            |
| **Design**                 | Marca **RecoveryTruck** em rebranding.                                                                                                          | Receber **manual visual** até o início da Sprint 1.                                                                                                      | ▸ Criar *theme variables* (`primary`, `accent`, `font`).                                                                                            |
| **Legais**                 | Há **termo de responsabilidade**; quer registro no banco.                                                                                       | Conteúdo final e se precisa **assinatura digital** ou só aceite via botão.                                                                               | ▸ Campo `terms_version` + `accepted_at` no banco.<br>▸ PDF do termo versionado salvo em S3.                                                         |
| **Relatórios & Métricas**  | KPIs: atendimentos/hora, tipo de serviço, faturamento diário/mensal.                                                                            | Preferência: **dashboard on-line** (Metabase) ou PDF por e-mail?                                                                                         | ▸ Começar com **endpoint CSV** + gráfico simples no painel operador (bar & line).                                                                   |

---

### Decisões críticas (“travar” antes do desenvolvimento)

1. **Integração Sicredi**

   * *Entrega rápida*: **link/QR** Sicredi → totem faz polling (confirmou? libera senha).
   * *Entrega ideal*: POS API **só** se Sicredi fornecer TEF/SDK compatível com Android; isso pode triplicar prazo.
     **Pergunta direta ao cliente**:

   > “Se o POS Sicredi não oferecer API de disparo remoto hoje, podemos começar com link de pagamento/QR-Code e migrar para integração direta numa fase 2?”

2. **Impressora**

   * Se a impressora for USB/ESC-POS: OK via JS.
   * Se for Bluetooth, será necessário app wrapper nativo.
     **Ação**: peça modelo (Ex: Elgin i9, Epson TM-T20 etc.).

3. **Som & Acessibilidade**

   * Definir se beep simples basta ou querem locução (“Senha A-003, dirija-se ao aparelho 1”).
   * Se locução: inserir `speechSynthesis` (browser) ou MP3 pré-gerado.

4. **LGPD & Termo**

   * Validar com jurídico se “nome + CPF + telefone” é mínimo necessário.
   * Entregar minipolítica (30–50 palavras) + link para política completa.

---

### Ajuste no cronograma (resumido)

| Fase                           | Dias úteis | Mudanças                                                 |
| ------------------------------ | ---------- | -------------------------------------------------------- |
| Kick-off & Especificação       | **0-2**    | Travar integrações (Sicredi, impressora).                |
| Sprint 1 – UI & Ticket         | **3-6**    | Já incluir captura Nome/CPF/celular + consentimento.     |
| Sprint 2 – Painel & Impressão  | **7-10**   | Beep/voz por serviço; driver impressora integrado.       |
| Sprint 3 – Pagamento (link QR) | **11-14**  | Webhook/Polling Sicredi. Se POS-API for viável, +3 dias. |
| QA & Deploy piloto             | **15-18**  | Testes 4G + impressora + latência.                       |
| Treinamento & Handover         | **19-20**  | Manual, vídeo, relatório KPI simples.                    |

*(mantém as 3 semanas úteis; só estende se POS-API exigir certificação)*

