# Sistema de Adaptadores de Pagamento

## Visão Geral

O sistema de adaptadores de pagamento foi projetado para fornecer uma interface unificada para integração com diferentes processadores de pagamento. Cada adaptador implementa a interface `PaymentAdapter`, garantindo consistência e facilidade de uso.

## Adaptadores Suportados

Atualmente, os seguintes processadores são suportados:

1. **Sicredi**
   - Suporta cartão de crédito, débito e PIX
   - Integração via API REST

2. **Stone**
   - Suporta cartão de crédito, débito e PIX
   - Integração via API REST

3. **PagSeguro**
   - Suporta cartão de crédito, débito, PIX e boleto
   - Integração via API REST

4. **Mercado Pago**
   - Suporta cartão de crédito, débito, PIX e boleto
   - Integração via API REST

5. **SafraPay**
   - Suporta cartão de crédito, débito e PIX
   - Integração via API REST

6. **PagBank**
   - Suporta cartão de crédito, débito, PIX e boleto
   - Integração via API REST

## Estrutura do Código

```
apps/api/services/payment/
├── adapters/
│   ├── __init__.py
│   ├── base.py
│   ├── sicredi.py
│   ├── stone.py
│   ├── pagseguro.py
│   ├── mercadopago.py
│   ├── safrapay.py
│   └── pagbank.py
├── factory.py
└── models.py
```

## Como Usar

### 1. Configurando um Tenant
Para configurar um tenant com adaptadores específicos:

```python
from apps.api.services.payment.factory import PaymentAdapterFactory

# Configuração do Stone
stone_config = {
    "api_url": "https://api.stone.com.br/v1",
    "api_key": "your-api-key",
    "merchant_id": "your-merchant-id"
}

# Configuração do Mercado Pago
mercadopago_config = {
    "api_url": "https://api.mercadopago.com/v1",
    "access_token": "your-access-token"
}

# Registra os adaptadores
factory = PaymentAdapterFactory()
factory.register_adapter("stone", StoneAdapter, stone_config)
factory.register_adapter("mercadopago", MercadoPagoAdapter, mercadopago_config)
```

### 2. Criando um Pagamento
```python
# Obtém o adaptador
adapter = factory.create_adapter("stone")

# Cria um pagamento
payment = await adapter.create_payment(
    amount=1000,  # R$ 10,00
    description="Compra de ingresso",
    payment_method="credit_card",
    payer={
        "name": "João Silva",
        "document": "123.456.789-00"
    }
)
```

### 3. Verificando Status
```python
status = await adapter.check_status(payment.id)
```

### 4. Cancelando um Pagamento
```python
await adapter.cancel_payment(payment.id)
```

### 5. Imprimindo Recibo
```python
await adapter.print_receipt(payment.id)
```

### 6. Gerando QR Code
```python
payment_link = await adapter.get_payment_link(payment.id)
# Use o payment_link para gerar o QR Code
```

### 7. Webhooks
```python
# Verifica a assinatura do webhook
is_valid = adapter.verify_webhook(request.headers, request.body)

if is_valid:
    # Processa o webhook
    pass
```

## Adicionando Novos Adaptadores

Para adicionar um novo adaptador:

1. Crie uma nova classe que herda de `PaymentAdapter`
2. Implemente todos os métodos requeridos
3. Registre o adaptador na factory

Exemplo:
```python
from .base import PaymentAdapter

class NovoAdapter(PaymentAdapter):
    def __init__(self, config):
        self.api_url = config["api_url"]
        self.api_key = config["api_key"]
        
    async def create_payment(self, amount, description, payment_method, payer):
        # Implementação específica
        pass
        
    # Implemente os outros métodos...
```

## Considerações de Segurança

1. **Autenticação**
   - Todos os adaptadores usam autenticação via Bearer token
   - Webhooks são verificados usando assinatura HMAC

2. **Dados Sensíveis**
   - Nunca armazene tokens ou chaves no banco de dados
   - Use variáveis de ambiente para configurações sensíveis

3. **Rate Limiting**
   - O sistema implementa rate limiting por IP
   - Configurável via variáveis de ambiente:
     - `RATE_LIMIT_REQUESTS`: Número máximo de requisições (padrão: 100)
     - `RATE_LIMIT_PERIOD`: Período em segundos (padrão: 60)
   - Headers de resposta incluem:
     - `X-RateLimit-Limit`: Limite total de requisições
     - `X-RateLimit-Remaining`: Requisições restantes
     - `X-RateLimit-Reset`: Timestamp de reset do limite
   - Em caso de limite excedido:
     - Status code: 429 (Too Many Requests)
     - Header `Retry-After`: Tempo em segundos para próxima tentativa

## Notas

1. **Endpoints**
   - Cada adaptador pode ter endpoints específicos
   - Consulte a documentação do processador para detalhes

2. **Funcionalidades**
   - Nem todos os processadores suportam todas as funcionalidades
   - Verifique a documentação do adaptador específico

3. **Tratamento de Erros**
   - Implemente tratamento de erros específico para cada adaptador
   - Use logging para debug e monitoramento

4. **Testes**
   - Implemente testes unitários para cada adaptador
   - Use mocks para simular respostas da API

5. **Monitoramento**
   - Use OpenTelemetry para rastreamento de requisições
   - Monitore métricas de sucesso/falha
   - Configure alertas para falhas críticas 