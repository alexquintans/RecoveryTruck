Ran tool
Estudo de integração com “maquininha” Sicredi  
================================================

1. Visão geral da oferta Sicredi  
   • O Sicredi não expõe SDK específico para a maquininha; o fluxo oficial para **recebimento via equipamento** é a própria API Pix Sicredi.  
   • A maquininha gera o QR Code Dinâmico (usando endpoint `/cob`) ou lê NFC e confirma pagamento via Webhook ou pooling.  
   • Documentação pública: “Guia Técnico Integrações API Pix” (v19.1, mai 2025).  
     – PDF: https://www.sicredi.com.br/media/produtos/filer_public/2025/05/21/guia_tecnico_integracoes_api_pix_sicredi_v19_1.pdf  
   • Portal do Desenvolvedor: https://developer.sicredi.com.br (cadastro necessário).

2. Jornada de adesão (PJ)  
   a) Associado solicita adesão na cooperativa → recebe “ID de adesão”.  
   b) Técnico cria conta no Portal Dev, abre chamado “Acesso à API Pix” (informa CNPJ & ID).  
   c) Geração de CSR + chave privada (openssl) → upload (“Registrar Novo CSR”).  
   d) Sicredi valida e devolve certificado .CER, cadeia CA, opcional webhook-sicredi.CER.  
   e) Geração das **credenciais OAuth** (Client ID / Client Secret) ligadas a esse certificado.  
   f) Para homologação, pedir credenciais por e-mail (integracoes_pix@sicredi.com.br).  
   g) Após testes → produção.

3. Segurança/Infraestrutura  
   • Todas as chamadas TLS 1.2 com **mutual TLS** (mTLS): chave privada (.key) + certificado validado.  
   • Autenticação: OAuth 2.0 Client Credentials Flow  
     – `POST /oauth/token` (scope ex.: `cob.write cob.read webhook.write webhook.read`).  
   • Token (JWT) ~1 h de validade.  
   • Endpoints:  
     – Prod: https://api-pix.sicredi.com.br/oauth/token | /api/v2  
     – Homol: https://api-pix-h.sicredi.com.br/oauth/token | /api/v2

4. Endpoints principais (recebimento)  
   1. `POST /api/v2/cob` – Criar Cobrança imediata (QR Dinâmico).  
      Campos mínimos: `calendario.expiracao`, `devedor` (opcional), `valor.original`, `chave`.  
      Resposta traz `loc.id`, `location`, `txid`, `pixCopiaECola`.  
   2. `GET /api/v2/loc/{id}/qrcode` – Gera payload BRCode (se quiser imagem).  
   3. `GET /api/v2/pix?inicio=…&fim=…` – Listar Pix recebidos.  
   4. `GET /api/v2/pix/{e2eid}` – Pix específico.  
   5. Webhook (`PUT /api/v2/webhook/{chave}`) – cadastra URL HTTPS para notificação automática de pagamento (payload conforme Bacen).  

5. Webhook de confirmação  
   • Sicredi envia POST JSON quando recebe Pix para aquela chave.  
   • Requisito: seu servidor HTTPS com certificado público confiável.  
   • Opcional: validar certificado `webhook-sicredi.CER` (auth mútua).  

6. Erros & troubleshooting (resumo do guia)  
   – 400 Bad Request escopo ou chave inválida.  
   – 401 token inválido.  
   – 403 mTLS falhou (KEY/CER não correspondem).  
   – 500 erros internos – contatar suporte.  
   • Use Postman collection do Sicredi para testar (inclui mTLS).  

7. Passos para integrar no Totem  
   1. Formalizar adesão na cooperativa.  
   2. Obter certificado + credenciais; armazenar no back-end (FastAPI) com segurança.  
   3. Implementar serviço `SicrediPixAdapter` (já há `services/payment/adapters/sicredi.py` stub).  
      – Métodos: `create_payment(amount, description)` → retorna `{qr_code, txid}`.  
      – Pool or Webhook handler para `payment_update`.  
   4. Back-end gera QR (ou repassa `pixCopiaECola` para front).  
   5. Front Totem exibe QR; após webhook do Sicredi → marca PaymentSession `paid` → WS → Totem → imprime ticket.  
   6. Para fallback, front faz polling em `/payment-sessions/{id}` (já implementado).  

8. Dados e parâmetros necessários  
   • Chave Pix (EVP, CNPJ ou telefone) cadastrada na conta PJ.  
   • Certificado .CER + chave .KEY (sem senha) ⇔ correspondentes.  
   • Cadeia CA do Sicredi instalada no back-end (requests mTLS).  
   • Client ID & Client Secret (produção e homol).  
   • URL de Webhook pública HTTPS válida (ex.: https://api.minhaempresa.com/pix/webhook).  

9. Dependências de backend Python  
   • `httpx` ou `requests` suportando mTLS (`cert=(cert.pem, key.pem)`).  
   • Renova token OAuth automaticamente; cache em memória/Redis.  
   • Validação de assinatura / idempotência no Webhook (e2eid único).  

10. Cronograma enxuto  
   • Semana 1: Concluir adesão, gerar artefatos, mTLS teste via Postman.  
   • Semana 2: Implementar `SicrediPixAdapter` + endpoints webhook/homologação.  
   • Semana 3: Conectar com PaymentSession flow; testes ponta-a-ponta Totem → Pix pago → Ticket impresso.  
   • Semana 4: Monitoramento, métricas, handling de devolução (opcional).

Referências  
• Guia Técnico Sicredi v19.1 (PDF)  
• Portal do Desenvolvedor Sicredi: https://developer.sicredi.com.br  
• Especificação Bacen Pix API: https://bacen.github.io/pix-api  

Isso cobre as informações necessárias para iniciar a integração com a maquininha/QR Pix Sicredi.


------------------------
Integração cartão (crédito/débito) com “totem” + impressora + maquininha Sicredi  
==========================================================================

Premissas  
• Totem = tablet Android (nosso app React Native/Expo ou web em modo kiosk)  
• Impressora térmica USB/Serial já integrada (FastAPI gera ESC/POS).  
• Maquininha Sicredi será acoplada fisicamente no quiosque (energia + rede) para que o cliente passe o cartão ali mesmo, tal qual totens do McDonald’s/BK.

1. Qual modelo de maquininha?  
-------------------------------------------------
Sicredi opera dois cenários:

A) Smart POS (Android) – ex. PAX A920/A50 ou Gertec T640  
   • Único hardware: tela + leitor + impressora.  
   • Possui SDK AIDL/Intent (“Sicredi Pay SDK”) para iniciar transações a partir de outro app ou via URL Scheme.  
   • Kiosk clássico: rodamos **o nosso app dentro da maquininha**; impressora interna imprime tanto comprovante quanto ticket (ou enviamos ESC/POS para térmica externa).

B) POS tradicional + Pin-Pad (“Dupla tela”) – ex. Ingenico Move/5000 + Pinpad  
   • Comunicação via **TEF (Transferência Eletrônica de Fundos)** padrão PayGo/SiTef/NTK.  
   • Tablet dispara comando de venda em rede local (`localhost:60906/paygo`) ou socket serial.  
   • POS imprime comprovante; Totem imprime ticket na sua impressora.

→ Confirme com a cooperativa qual kit será fornecido. A Sicredi geralmente oferta **Smart POS** para novos projetos, pois simplifica a homologação PCI.

2. Fluxo de integração (Smart POS recomendado)  
-------------------------------------------------
```
Totem React/Web (tablet) ──► SDK Sicredi Pay (na mesma máquina) ─► REDE Sicredi
       │                                                               │
       └── WebSocket backend (PaymentSession) ◄── status/receipt ◄─────┘
```

1. Cliente escolhe serviço no totem → `POST /payment-sessions` (payment_method=credit|debit).  
2. Backend gera sessão “pending”, devolve `transaction_id` e `amount`.  
3. Front chama SDK local:

```ts
startCardPayment({
  amount: 5000,          // em centavos
  transactionId: “…”,    // para conciliar
  installments: 1,
});
```

4. SDK exibe tela nativa de pagamento; usuário insere cartão/PIN.  
5. SDK devolve callback:

```json
{ status: "approved", nsu: "312456", authorization: "A12345", cardBrand:"VISA" }
```

6. Front envia PATCH `/payment-sessions/{id}` status=paid + dados cartão.  
7. FastAPI lança ticket, imprime, emite `payment_update` via WebSocket → front exibe TicketPage.

3. Ponto-a-ponto de implementação  
-------------------------------------------------

Backend (`services/payment/adapters/sicredi_terminal.py`)  
• `start_payment(amount, transaction_id, card_type)`  
• `cancel_payment(transaction_id)`  
• Armazena NSU, authorization, brand, masked PAN.

Totem front  
• `useCardPayment()` hook que encapsula:
  – chamada AIDL/Intent: `intent.putExtra("amount", …)`  
  – promessa resolve/reject com resultado.  
• Tratamento de erros:
  – `USER_CANCELLED`, `DECLINED`, `TIMEOUT` → mostra modal e permite tentar novamente ou trocar para Pix.

Ticket/Impressão  
• Se Smart POS tiver impressora: enviar ESC/POS via API da impressora interna OU imprimir comprovante cartão nela e ticket na térmica externa.  
• Adicionar opção “re-imprimir comprovante”.

4. TEF (se usar POS + Pin-Pad)  
-------------------------------------------------
• Instalar middleware PayGo Windows/Linux dentro do quiosque.  
• FastAPI expõe `POST /tef/sale` → realiza socket para PayGo → retorna JSON.  
• Necessário homologação PayGo + Sicredi (código adquirente 136).  
• Monitor de TEF imprime comprovante; ticket sai na impressora do totem.

5. Checklist de requisitos Sicredi (crédito/débito)  
-------------------------------------------------

| Item | Observação |
|------|------------|
| Afiliado Sicredi Cartões PJ | CNPJ precisa estar ativo com bandeiras desejadas |
| Chave de automação (TEF) ou SDK SmartPOS | Fornecida pela cooperativa |
| Certificação PCI no dispositivo | Smart POS já certifica |
| Conexão HTTPS para conciliação | Nosso backend já usa SSL |
| Sincronismo de relógio no POS | Para antifraude |

6. Roadmap de desenvolvimento  
-------------------------------------------------
Semana | Entrega
---|---
1 | Confirmar modelo de maquininha, obter APK/SDK ou PayGo. \
   Estruturar `CardPaymentAdapter` (interfaces).
2 | Implementar prova-de-conceito no Totem (chamada SDK, tela de teste). \
   Logar callbacks de sucesso/erro.
3 | Conectar com `PaymentSession` (backend) e WebSocket. \
   Imprimir comprovante/ticket.
4 | Homologação Sicredi (testes de 10 transações / 3 cenários). \
   Ajustes de UX (mensagens, animações).
5 | Deploy piloto no quiosque do cliente; monitoramento e ajustes.

7. Próximos passos imediatos  
-------------------------------------------------
1. Perguntar ao gerente Sicredi:  
   • “Vocês fornecem Smart POS Android integrado ou TEF PayGo?”  
2. Solicitar kit de homologação + manual do SDK (ou PayGo).  
3. Iniciar stub do `CardPaymentAdapter` na pasta `services/payment/adapters/sicredi.py`.  
4. Criar hook `useCardPayment` no totem-client.

Com esses insumos definimos o caminho técnico completo para aceitar crédito/débito na maquininha acoplada ao totem, mantendo o fluxo unificado já existente de `PaymentSession` e WebSocket.