# 🎯 API de Preferências Mercado Pago

## 📋 Visão Geral

A **API de Preferências** do Mercado Pago é a forma recomendada para criar links de pagamento para o **Checkout Pro**. Ela permite configurar todos os detalhes do pagamento antes de redirecionar o cliente.

## ✅ Por que usar a API de Preferências?

### **Vantagens**
- ✅ **Configuração completa** antes do pagamento
- ✅ **URLs de retorno** personalizadas
- ✅ **Webhooks** configurados automaticamente
- ✅ **Métodos de pagamento** filtrados
- ✅ **Dados do cliente** pré-preenchidos
- ✅ **Metadados** para rastreamento

### **Fluxo de Pagamento**
1. **Backend** cria preferência com todos os dados
2. **Frontend** recebe `init_point` da preferência
3. **Cliente** é redirecionado para o Checkout Pro
4. **Mercado Pago** processa o pagamento
5. **Webhook** notifica sobre mudanças de status

## 🔧 Implementação

### **Criar Preferência**

```python
import mercadopago
from mercadopago.config import RequestOptions

# Inicializar SDK
sdk = mercadopago.SDK("YOUR_ACCESS_TOKEN")

# Dados da preferência
preference_data = {
    "items": [
        {
            "title": "Serviço de Recuperação",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 50.00
        }
    ],
    "payer": {
        "email": "cliente@exemplo.com",
        "name": "João Silva"
    },
    "back_urls": {
        "success": "https://seu-dominio.com/payment/success",
        "failure": "https://seu-dominio.com/payment/failure",
        "pending": "https://seu-dominio.com/payment/pending"
    },
    "auto_return": "approved",
    "external_reference": "payment_session_123",
    "notification_url": "https://seu-dominio.com/webhooks/mercadopago",
    "metadata": {
        "source": "totem",
        "amount": 50.00
    }
}

# Criar preferência
result = sdk.preference().create(preference_data)

if result["status"] == 201:
    preference = result["response"]
    print(f"Preferência criada: {preference['id']}")
    print(f"Link de pagamento: {preference['init_point']}")
```

### **Estrutura Completa da Preferência (Documentação Oficial)**

```python
preference_data = {
    # Itens do pagamento
    "items": [
        {
            "id": "1234",
            "title": "Serviço de Recuperação",
            "description": "Recuperação de veículo",
            "picture_url": "https://www.recoverytruck.com/logo.jpg",
            "category_id": "services",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 100.00
        }
    ],
    
    # Taxa do marketplace (opcional)
    "marketplace_fee": 0,
    
    # Dados do pagador
    "payer": {
        "name": "João",
        "surname": "Silva",
        "email": "joao.silva@example.com",
        "phone": {
            "area_code": "11",
            "number": "999999999"
        },
        "identification": {
            "type": "CPF",
            "number": "12345678901"
        },
        "address": {
            "zip_code": "01234-567",
            "street_name": "Rua das Flores",
            "street_number": 123
        }
    },
    
    # URLs de retorno
    "back_urls": {
        "success": "https://recoverytruck.com/payment/success",
        "failure": "https://recoverytruck.com/payment/failure",
        "pending": "https://recoverytruck.com/payment/pending"
    },
    
    # Preços diferenciais (opcional)
    "differential_pricing": {
        "id": 1
    },
    
    # Configurações
    "expires": False,
    "additional_info": "Serviço de recuperação de veículo",
    "auto_return": "approved",
    "binary_mode": True,  # Apenas aprovado ou rejeitado
    "external_reference": "payment_123456",
    "marketplace": "marketplace",
    "notification_url": "https://recoverytruck.com/webhooks/mercadopago",
    "operation_type": "regular_payment",
    
    # Métodos de pagamento
    "payment_methods": {
        "default_payment_method_id": "master",
        "excluded_payment_types": [
            {"id": "ticket"}  # Excluir boleto
        ],
        "excluded_payment_methods": [
            {"id": ""}  # Não excluir nenhum método específico
        ],
        "installments": 12,
        "default_installments": 1
    },
    
    # Configurações de envio (opcional)
    "shipments": {
        "mode": "custom",
        "local_pickup": False,
        "default_shipping_method": None,
        "free_methods": [
            {"id": 1}
        ],
        "cost": 0,
        "free_shipping": True,
        "dimensions": "10x10x20,500",
        "receiver_address": {
            "zip_code": "01234-567",
            "street_number": 123,
            "street_name": "Rua das Flores",
            "floor": "1",
            "apartment": "101"
        }
    },
    
    # Descritor da fatura
    "statement_descriptor": "RecoveryTruck"
}
```

## 🎯 Configurações Avançadas

### **Filtrar Métodos de Pagamento**

```python
"payment_methods": {
    # Excluir tipos de pagamento
    "excluded_payment_types": [
        {"id": "ticket"},  # Boleto
        {"id": "atm"}      # PIX
    ],
    
    # Excluir métodos específicos
    "excluded_payment_methods": [
        {"id": "visa"},
        {"id": "mastercard"}
    ],
    
    # Limitar parcelas
    "installments": 6
}
```

### **Configurar Expiração**

```python
"expires": True,
"expiration_date_to": "2024-12-31T23:59:59.000-03:00"
```

### **Dados do Cliente**

```python
"payer": {
    "email": "cliente@exemplo.com",
    "name": "João",
    "surname": "Silva",
    "phone": {
        "area_code": "11",
        "number": "999999999"
    },
    "identification": {
        "type": "CPF",
        "number": "12345678901"
    },
    "address": {
        "street_name": "Rua das Flores",
        "street_number": "123",
        "zip_code": "01234-567",
        "neighborhood": "Centro",
        "city": "São Paulo",
        "state": "SP"
    }
}
```

## 🔄 Webhooks

### **Configurar URL de Notificação**

```python
"notification_url": "https://seu-dominio.com/webhooks/mercadopago"
```

### **Eventos de Webhook**

```python
# Eventos recebidos
webhook_events = [
    "payment.created",
    "payment.updated", 
    "payment.approved",
    "payment.rejected",
    "payment.pending",
    "payment.in_process",
    "payment.cancelled",
    "payment.refunded"
]
```

## 📊 Resposta da API

### **Sucesso (201)**

```json
{
    "id": "1234567890",
    "init_point": "https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=1234567890",
    "sandbox_init_point": "https://sandbox.mercadopago.com.br/checkout/v1/redirect?pref_id=1234567890",
    "items": [...],
    "payer": {...},
    "back_urls": {...},
    "auto_return": "approved",
    "external_reference": "ref_123",
    "notification_url": "https://seu-dominio.com/webhook",
    "metadata": {...}
}
```

### **Erro (400/401/403)**

```json
{
    "error": "invalid_access_token",
    "message": "Invalid access token",
    "status": 401
}
```

## 🧪 Testes

### **Sandbox**

```python
# Credenciais de teste
ACCESS_TOKEN = "TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Testar criação
preference = sdk.preference().create(preference_data)
print(f"Preferência: {preference['response']['id']}")
```

### **Produção**

```python
# Credenciais de produção
ACCESS_TOKEN = "APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Criar preferência real
preference = sdk.preference().create(preference_data)
```

## 🚨 Troubleshooting

### **Erro: Invalid access token**
```python
# Verificar token
print(f"Token: {ACCESS_TOKEN[:10]}...")
```

### **Erro: Invalid preference data**
```python
# Validar dados obrigatórios
required_fields = ["items", "payer", "back_urls"]
for field in required_fields:
    if field not in preference_data:
        print(f"Campo obrigatório faltando: {field}")
```

### **Erro: Invalid notification URL**
```python
# URL deve ser HTTPS
notification_url = "https://seu-dominio.com/webhook"
```

## 📚 Documentação

- **API de Preferências**: [Documentação Oficial](https://www.mercadopago.com.br/developers/pt/docs/checkout-api/integrate-checkout-pro)
- **SDK Python**: [GitHub](https://github.com/mercadopago/sdk-python)
- **Webhooks**: [Guia de Webhooks](https://www.mercadopago.com.br/developers/pt/docs/checkout-api/additional-content/notifications)

---

**🎯 API de Preferências Mercado Pago - Configurada!** 