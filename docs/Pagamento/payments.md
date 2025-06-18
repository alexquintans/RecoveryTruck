# Implementação de Pagamentos

## Visão Geral

O sistema de pagamentos foi implementado com uma arquitetura híbrida que suporta tanto pagamentos via QR Code quanto integração com maquininha física Sicredi. A implementação atual inclui:

- Geração de QR Code para pagamentos via PIX/cartão
- Integração com maquininha física via API
- Webhook para confirmação de pagamentos
- Impressão de comprovantes via ESC/POS

## Arquitetura

### 1. Integração com Sicredi

#### Abordagem Híbrida
- **QR Code**: Para pagamentos via PIX/cartão no celular
- **Maquininha Física**: Integração via API REST
- **Webhook**: Confirmação automática de pagamentos

#### Escalabilidade
- Módulo de pagamentos como microserviço independente
- Adaptadores para múltiplos adquirentes (Sicredi, Stone, etc.)
- Processamento assíncrono via message broker (NATS/Redis)

### 2. Estratégia de Adaptadores

#### Design Pattern
Utilizamos o padrão Strategy com adaptadores para permitir a troca fácil de adquirentes:

```python
# apps/api/services/payment/adapters/base.py
from abc import ABC, abstractmethod

class PaymentAdapter(ABC):
    @abstractmethod
    def create_payment(self, amount: float, description: str) -> dict:
        pass
    
    @abstractmethod
    def check_status(self, transaction_id: str) -> str:
        pass
    
    @abstractmethod
    def cancel_payment(self, transaction_id: str) -> bool:
        pass
    
    @abstractmethod
    def print_receipt(self, transaction_id: str) -> bool:
        pass

# apps/api/services/payment/adapters/sicredi.py
class SicrediAdapter(PaymentAdapter):
    def create_payment(self, amount: float, description: str) -> dict:
        # Implementação específica do Sicredi
        pass

# apps/api/services/payment/adapters/stone.py
class StoneAdapter(PaymentAdapter):
    def create_payment(self, amount: float, description: str) -> dict:
        # Implementação específica da Stone
        pass
```

#### Configuração por Tenant
Cada tenant pode configurar seu próprio adquirente:

```python
# apps/api/models/tenant.py
class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String)
    payment_adapter = Column(String)  # "sicredi", "stone", etc.
    payment_config = Column(JSON)     # Configurações específicas
```

#### Factory de Adaptadores
```python
# apps/api/services/payment/factory.py
class PaymentAdapterFactory:
    @staticmethod
    def create_adapter(tenant: Tenant) -> PaymentAdapter:
        if tenant.payment_adapter == "sicredi":
            return SicrediAdapter(tenant.payment_config)
        elif tenant.payment_adapter == "stone":
            return StoneAdapter(tenant.payment_config)
        raise ValueError(f"Adapter não suportado: {tenant.payment_adapter}")
```

#### Migração de Adquirente
Para trocar o adquirente de um tenant:

1. **Configuração**:
   ```sql
   UPDATE tenants 
   SET payment_adapter = 'stone',
       payment_config = '{"api_key": "xxx", "merchant_id": "yyy"}'
   WHERE id = 'tenant_id';
   ```

2. **Migração de Dados**:
   - Exportar histórico de transações
   - Importar no novo adquirente
   - Atualizar referências

3. **Testes**:
   - Ambiente sandbox
   - Transações de teste
   - Validação de webhooks

4. **Go-live**:
   - Manter ambos adquirentes ativos
   - Migração gradual
   - Monitoramento

#### Vantagens
- Desacoplamento do código
- Fácil adição de novos adquirentes
- Configuração flexível por tenant
- Migração sem downtime

### 2. Maquininha Física

#### Requisitos
1. Conta no portal Sicredi
2. Acesso à API Sicredi
3. Registro da maquininha
4. Credenciais de API:
   - API Key
   - Merchant ID

#### Endpoints
- `/payments/pos/status` - Status da maquininha
- `/payments/pos/transaction` - Iniciar transação
- `/payments/pos/cancel` - Cancelar transação
- `/payments/pos/receipt` - Imprimir comprovante

### 3. Impressora ESC/POS

#### Implementação
- Biblioteca `python-escpos` para comunicação
- Serviço de impressão dedicado:
  - Formatação de ticket (logo, número, data/hora)
  - Impressão de QR code
  - Impressão de comprovante

#### Funcionalidades
- Formatação personalizada
- Suporte a múltiplas impressoras
- Queue de impressão com prioridade
- Fallback para PDF

## Escalabilidade

### 1. Multi-tenant
- Implementado com `tenant_id` em todas as tabelas
- Isolamento de dados por tenant
- Configurações específicas por tenant

### 2. Pagamentos
- Queue local para pagamentos offline
- Retry automático em caso de falha
- Cache de status de pagamento
- Processamento assíncrono

### 3. Impressão
- Pool de impressoras por tenant
- Queue de impressão com prioridade
- Fallback para PDF se impressora offline
- Balanceamento de carga

## Segurança

### 1. Dados Sensíveis
- Criptografia de dados sensíveis
- Mascaramento de números de cartão
- Armazenamento seguro de credenciais

### 2. Transações
- Assinatura de webhooks
- Validação de transações
- Logs de auditoria
- Monitoramento em tempo real

### 3. Conformidade
- LGPD: Base legal "execução de contrato"
- PCI-DSS (nível 4)
- OWASP Top-10

## Implementação Técnica

### 1. Dependências
```python
# requirements.txt
qrcode==7.4.2
python-escpos==3.0a8
cryptography==42.0.2
```

### 2. Configuração
```python
# .env
SICREDI_API_URL=https://api.sicredi.com.br/v1
SICREDI_API_KEY=your_api_key
SICREDI_MERCHANT_ID=your_merchant_id
```

### 3. Estrutura de Arquivos
```
apps/api/
├── routers/
│   └── payments.py
├── services/
│   ├── payment.py
│   └── printer.py
└── models/
    └── payment.py
```

## Próximos Passos

1. **Integração com Sicredi**
   - Implementar endpoints da API
   - Testar em ambiente sandbox
   - Configurar webhook

2. **Impressora**
   - Configurar driver ESC/POS
   - Testar formatos de impressão
   - Implementar queue

3. **Monitoramento**
   - Configurar logs
   - Implementar métricas
   - Criar dashboards

4. **Documentação**
   - API Reference
   - Guia de integração
   - Troubleshooting

## Referências

- [Documentação Sicredi API](https://api.sicredi.com.br/docs)
- [python-escpos Documentation](https://python-escpos.readthedocs.io/)
- [PCI-DSS Requirements](https://www.pcisecuritystandards.org/)
- [LGPD Guidelines](https://www.gov.br/cnpj/pt-br/assuntos/noticias/lgpd) 