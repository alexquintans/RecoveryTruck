# 🐍 Backend SDK Python Mercado Pago

## 📋 Visão Geral

Este guia mostra como configurar o backend da API para usar o **SDK Python oficial do Mercado Pago** que oferece integração mais robusta e funcionalidades avançadas.

## ✅ Vantagens do SDK Python

### **Funcionalidades Avançadas**
- ✅ **Idempotência** automática
- ✅ **Retry automático** em falhas
- ✅ **Validação** de dados
- ✅ **Logs estruturados**
- ✅ **Tratamento de erros** robusto

### **Integração Completa**
- ✅ **Checkout Pro** com preferências
- ✅ **Pagamentos com cartão** direto
- ✅ **Webhooks** processados
- ✅ **Métodos de pagamento** listados
- ✅ **Cancelamento** de transações

## 🚀 Configuração

### **1. Instalar Dependência**

```bash
# No diretório da API
cd apps/api
pip install mercadopago==2.2.0
```

### **2. Atualizar requirements.txt**

```txt
# Mercado Pago SDK Python
mercadopago==2.2.0
```

### **3. Configurar Variáveis de Ambiente**

```bash
# .env
MERCADOPAGO_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
MERCADOPAGO_PUBLIC_KEY=YOUR_PUBLIC_KEY
```

## 🔧 Implementação

### **Adaptador MercadoPago (atualizado)**

```python
import mercadopago
from mercadopago.config import RequestOptions
from typing import Dict, Optional, Any
import logging
from .base import PaymentAdapter

class MercadoPagoAdapter(PaymentAdapter):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        self.access_token = config["access_token"]
        self.webhook_url = config.get("webhook_url")
        self.redirect_url_base = config.get("redirect_url_base")
        
        # Inicializar SDK Python do Mercado Pago
        self.sdk = mercadopago.SDK(self.access_token)
        
        logger.info(f"💰 MercadoPagoAdapter initialized with SDK Python")
    
    async def create_payment_preference(self, amount: float, description: str, metadata: Dict) -> Dict:
        """Cria uma preferência de pagamento para o Checkout Pro usando a API de Preferências."""
        # Dados da preferência conforme API de Preferências do Mercado Pago
        preference_data = {
            "items": [
                {
                    "title": description,
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": amount
                }
            ],
            "payer": {
                "email": metadata.get("customer_email"),
                "name": metadata.get("customer_name"),
            },
            "back_urls": {
                "success": f"{self.redirect_url_base}/success",
                "failure": f"{self.redirect_url_base}/failure",
                "pending": f"{self.redirect_url_base}/pending"
            },
            "auto_return": "approved",
            "external_reference": metadata.get("payment_session_id"),
            "notification_url": self.webhook_url,
            "metadata": metadata
        }
        
        try:
            # Usar API de Preferências do Mercado Pago via SDK Python
            result = self.sdk.preference().create(preference_data)
            
            if result["status"] != 201:
                raise Exception(f"Erro ao criar preferência: {result.get('error', 'Unknown error')}")
            
            preference = result["response"]
            
            return {
                "init_point": preference["init_point"],
                "preference_id": preference["id"]
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar preferência Mercado Pago: {e}")
            raise
```

### **Pagamento com Cartão**

```python
def create_payment_with_card(self, amount: float, card_token: str, payment_method_id: str, 
                            installments: int = 1, payer_email: str = None) -> Dict:
    """Cria pagamento com cartão usando SDK Python."""
    try:
        payment_data = {
            "transaction_amount": amount,
            "token": card_token,
            "description": "Pagamento RecoveryTruck",
            "payment_method_id": payment_method_id,
            "installments": installments,
            "payer": {
                "email": payer_email or "cliente@recoverytruck.com"
            }
        }
        
        # Configurar opções de request com idempotência
        request_options = RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': f'payment_{card_token}_{int(amount * 100)}'
        }
        
        result = self.sdk.preference().create(payment_data, request_options)
        
        if result["status"] != 201:
            raise Exception(f"Erro ao criar pagamento: {result.get('error', 'Unknown error')}")
        
        payment = result["response"]
        logger.info(f"✅ Pagamento com cartão criado: {payment['id']}")
        
        return payment
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar pagamento com cartão: {e}")
        raise
```

### **Verificação de Status**

```python
async def check_status(self, transaction_id: str) -> str:
    """Verifica o status de uma transação usando o ID de pagamento."""
    try:
        result = self.sdk.preference().get(transaction_id)
        
        if result["status"] != 200:
            raise Exception(f"Erro ao buscar pagamento: {result.get('error', 'Unknown error')}")
        
        payment = result["response"]
        return payment["status"]
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status do pagamento {transaction_id}: {e}")
        raise
```

## 🧪 Testes

### **Sandbox**

```python
# Credenciais de teste
ACCESS_TOKEN = "TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
PUBLIC_KEY = "TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### **Cartões de Teste**

```python
# Cartões para testes
TEST_CARDS = {
    "visa": "4509 9535 6623 3704",
    "mastercard": "5031 4332 1540 6351",
    "elo": "6363680000457013"
}
```

### **Exemplo de Teste**

```python
# Testar criação de preferência
preference = adapter.create_payment_preference(
    amount=50.00,
    description="Serviço de Recuperação",
    metadata={
        "customer_email": "teste@exemplo.com",
        "customer_name": "João Silva",
        "payment_session_id": "session_123"
    }
)

print(f"Preferência criada: {preference['preference_id']}")
```

## 🔄 Webhooks

### **Processamento de Webhook**

```python
def process_webhook(self, webhook_data: dict) -> dict:
    """Processa dados do webhook."""
    try:
        # Verificar se é um webhook de pagamento
        if webhook_data.get("type") == "payment":
            payment_id = webhook_data["data"]["id"]
            payment_info = self.get_payment_status(payment_id)
            
            if payment_info:
                logger.info(f"🔄 Webhook processado: {payment_id} - {payment_info['status']}")
                return payment_info
        
        return webhook_data
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook: {e}")
        return None
```

## 📊 Monitoramento

### **Logs Estruturados**

```python
import logging

logger = logging.getLogger(__name__)

# Logs automáticos do SDK
logger.info(f"✅ Preferência criada: {preference_id}")
logger.error(f"❌ Erro ao criar pagamento: {error}")
logger.warning(f"⚠️ Pagamento pendente: {payment_id}")
```

### **Métricas**

```python
# Métricas disponíveis
- Transações por minuto
- Taxa de sucesso
- Tempo de resposta
- Erros por tipo
- Métodos de pagamento mais usados
```

## 🚨 Troubleshooting

### **Erro: Module not found**
```bash
# Reinstalar dependência
pip install mercadopago==2.2.0
```

### **Erro: Access token inválido**
```python
# Verificar token
print(f"Token: {ACCESS_TOKEN[:10]}...")
```

### **Erro: Status code não 201**
```python
# Verificar resposta completa
print(f"Resposta: {result}")
```

## 🎯 Próximos Passos

1. ✅ **Instalar SDK Python** no requirements.txt
2. ✅ **Atualizar adaptador** com SDK oficial
3. ✅ **Testar criação** de preferências
4. ✅ **Testar webhooks** em sandbox
5. ✅ **Deploy em produção**

## 📚 Documentação

- **SDK Python**: [Documentação Oficial](https://github.com/mercadopago/sdk-python)
- **API Reference**: [Mercado Pago API](https://www.mercadopago.com.br/developers/pt/docs)
- **Webhooks**: [Guia de Webhooks](https://www.mercadopago.com.br/developers/pt/docs/checkout-api/additional-content/notifications)

---

**🐍 SDK Python Mercado Pago - Backend Configurado!** 