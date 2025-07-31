# 💰 Mercado Pago Checkout Pro - Guia de Integração

## 📋 Visão Geral

Esta integração utiliza o **SDK JavaScript do Mercado Pago** para implementar o **Checkout Pro** no sistema de totem. O fluxo é 100% online e oferece uma experiência de pagamento completa e segura.

## ✅ Funcionalidades Implementadas

### **Frontend (Totem)**
- ✅ SDK JavaScript carregado automaticamente
- ✅ Interface de pagamento responsiva
- ✅ Callbacks de sucesso, erro e cancelamento
- ✅ Estados de loading e tratamento de erros
- ✅ Notificações sonoras integradas

### **Backend (API)**
- ✅ Adaptador MercadoPago completo
- ✅ Criação de preferências de pagamento
- ✅ Webhook robusto com validação
- ✅ Integração automática com tickets
- ✅ Impressão automática de comprovantes

## 🚀 Configuração Rápida

### **1. Configurar Mercado Pago Developers**

1. Acesse [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
2. Crie uma nova aplicação
3. Configure:
   - **Tipo de solução**: Pagamentos on-line
   - **Plataforma e-commerce**: Não
   - **Produto**: Checkout Pro
   - **Modelo de integração**: SDK JavaScript

### **2. Obter Credenciais**

No painel do Mercado Pago, você receberá:
```bash
# Sandbox (testes)
MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Produção
MERCADOPAGO_ACCESS_TOKEN=APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MERCADOPAGO_PUBLIC_KEY=APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### **3. Configurar Variáveis de Ambiente**

```bash
# .env
MERCADOPAGO_API_URL=https://api.mercadopago.com/v1
MERCADOPAGO_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
MERCADOPAGO_PUBLIC_KEY=YOUR_PUBLIC_KEY
```

### **4. Configurar Webhook**

No painel do Mercado Pago, configure:
```
URL: https://seu-dominio.com/webhooks/mercadopago
Eventos: payment.created, payment.updated, payment.approved
```

## 🔄 Fluxo Completo

### **1. Cliente Escolhe Serviço**
```typescript
// Totem exibe serviços disponíveis
const services = await api.getServices(tenantId);
```

### **2. Sistema Cria Preferência**
```python
# Backend cria preferência no Mercado Pago
preference_data = {
    "items": [{"title": "Serviço", "quantity": 1, "unit_price": 50.00}],
    "payer": {"email": "cliente@email.com", "name": "João Silva"},
    "back_urls": {
        "success": "https://seu-dominio.com/payment/success",
        "failure": "https://seu-dominio.com/payment/failure",
        "pending": "https://seu-dominio.com/payment/pending"
    },
    "auto_return": "approved",
    "notification_url": "https://seu-dominio.com/webhooks/mercadopago"
}
```

### **3. Frontend Renderiza Checkout**
```typescript
// SDK JavaScript renderiza o botão
const mp = new MercadoPago(publicKey, { locale: 'pt-BR' });
mp.checkout({
    preference: { id: preferenceId },
    render: { container: '.cho-container' },
    callbacks: {
        onSuccess: () => console.log('✅ Pagamento aprovado'),
        onError: (error) => console.error('❌ Erro:', error),
        onCancel: () => console.log('🚫 Cancelado')
    }
});
```

### **4. Webhook Processa Confirmação**
```python
# Webhook recebe notificação
@router.post("/mercadopago")
async def mercadopago_webhook(request: Request):
    webhook_data = await request.json()
    
    if webhook_data["action"] == "payment.updated":
        # Processa pagamento e cria ticket automaticamente
        ticket = await create_ticket_from_payment(payment_data)
```

## 🛠️ Implementação Técnica

### **Componente MercadoPagoPayment**

```typescript
interface MercadoPagoPaymentProps {
  preferenceId: string;
  publicKey: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
}
```

**Funcionalidades:**
- ✅ Loading states
- ✅ Tratamento de erros
- ✅ Callbacks personalizados
- ✅ Interface responsiva
- ✅ Retry automático

### **Adaptador Backend**

```python
class MercadoPagoAdapter(PaymentAdapter):
    async def create_payment_preference(self, amount: float, description: str, metadata: Dict) -> Dict:
        # Cria preferência no Mercado Pago
        # Retorna preference_id e init_point
```

**Funcionalidades:**
- ✅ Criação de preferências
- ✅ Validação de dados
- ✅ Tratamento de erros
- ✅ Logs detalhados

### **Webhook Handler**

```python
@router.post("/mercadopago")
async def mercadopago_webhook(request: Request, background_tasks: BackgroundTasks):
    # Valida assinatura
    # Processa em background
    # Cria ticket automaticamente
```

## 🔧 Configuração Avançada

### **Métodos de Pagamento**

```json
{
  "payment_methods": {
    "credit_card": {
      "enabled": true,
      "installments": {"min": 1, "max": 12}
    },
    "debit_card": {"enabled": true},
    "pix": {
      "enabled": true,
      "expiration_minutes": 30
    }
  }
}
```

### **URLs de Retorno**

```json
{
  "back_urls": {
    "success": "https://seu-dominio.com/payment/success",
    "failure": "https://seu-dominio.com/payment/failure",
    "pending": "https://seu-dominio.com/payment/pending"
  }
}
```

### **Segurança**

```json
{
  "security": {
    "validate_signature": true,
    "allowed_ips": [],
    "max_timestamp_diff": 600
  }
}
```

## 🧪 Testes

### **Sandbox**
```bash
# Credenciais de teste
MERCADOPAGO_ACCESS_TOKEN=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### **Cartões de Teste**
- **Visa**: 4509 9535 6623 3704
- **Mastercard**: 5031 4332 1540 6351
- **PIX**: Automático no sandbox

## 🚨 Troubleshooting

### **Erro: SDK não carregado**
```javascript
// Verificar se o script está carregado
if (!window.MercadoPago) {
    console.error('SDK não carregado');
}
```

### **Erro: Public Key inválida**
```bash
# Verificar variável de ambiente
echo $MERCADOPAGO_PUBLIC_KEY
```

### **Erro: Webhook não recebido**
```bash
# Verificar logs
tail -f logs/api.log | grep mercadopago
```

## 📊 Monitoramento

### **Métricas Disponíveis**
- ✅ Transações por minuto
- ✅ Taxa de sucesso
- ✅ Tempo de resposta
- ✅ Erros por tipo

### **Logs Estruturados**
```json
{
  "level": "INFO",
  "message": "MercadoPago transaction created",
  "transaction_id": "123456789",
  "amount": 50.00,
  "status": "pending"
}
```

## 🎯 Próximos Passos

1. **Configurar credenciais** no ambiente
2. **Testar em sandbox** com cartões de teste
3. **Configurar webhook** no painel do Mercado Pago
4. **Testar fluxo completo** no totem
5. **Ativar em produção** após testes

## 📞 Suporte

- **Documentação**: [Mercado Pago Developers](https://www.mercadopago.com.br/developers)
- **SDK JavaScript**: [Documentação Oficial](https://www.mercadopago.com.br/developers/pt/docs/checkout-api/integrate-checkout)
- **Webhooks**: [Guia de Webhooks](https://www.mercadopago.com.br/developers/pt/docs/checkout-api/additional-content/notifications)

---

**✅ Integração Mercado Pago Checkout Pro - Implementação Completa!** 