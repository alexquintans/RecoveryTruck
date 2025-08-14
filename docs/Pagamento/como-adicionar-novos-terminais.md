# 🔧 Como Adicionar Novos Terminais - Guia do Desenvolvedor

## 📋 **Visão Geral**

Este guia explica como adicionar suporte a novos terminais de pagamento no sistema RecoveryTruck. A arquitetura foi projetada para ser **extremamente extensível** e permitir adição de novos terminais com facilidade.

## 🏗️ **Arquitetura Extensível**

### **Padrão de Design Utilizado**
- ✅ **Factory Pattern** - Criação dinâmica de terminais
- ✅ **Strategy Pattern** - Diferentes protocolos de comunicação
- ✅ **Template Method** - Interface padronizada
- ✅ **Dependency Injection** - Configuração flexível

### **Componentes Principais**
1. **TerminalAdapter** (base.py) - Interface abstrata
2. **TerminalAdapterFactory** (factory.py) - Criação de instâncias
3. **Protocols** (protocols.py) - Comunicação física
4. **TerminalManager** (terminal_manager.py) - Gerenciamento

## 🚀 **Passo a Passo para Adicionar Novo Terminal**

### **Passo 1: Criar Adaptador Específico**

```python
# apps/api/services/payment/terminal/novo_terminal.py

from .base import TerminalAdapter, TerminalStatus, PaymentMethod
from .protocols import SerialProtocol, TCPProtocol

class NovoTerminalAdapter(TerminalAdapter):
    """Adaptador para Novo Terminal"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Configurações específicas
        self.novo_config = config.get("novo_terminal", {})
        self.merchant_id = self.novo_config.get("merchant_id")
        
        # Protocolo de comunicação
        self.protocol = self._create_protocol(
            config.get("connection_type", "serial"), 
            config
        )
        
        # Métodos suportados
        self._supported_methods = [
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.DEBIT_CARD,
            # Adicionar métodos específicos
        ]
    
    async def connect(self) -> bool:
        """Implementar conexão específica"""
        try:
            self._set_status(TerminalStatus.CONNECTING)
            
            # 1. Conectar fisicamente
            if not await self.protocol.connect():
                return False
            
            # 2. Inicializar terminal
            response = await self._send_init_command()
            
            # 3. Validar resposta
            if self._is_success_response(response):
                self._set_status(TerminalStatus.CONNECTED)
                return True
            
            return False
            
        except Exception as e:
            self._set_status(TerminalStatus.ERROR)
            return False
    
    async def start_transaction(self, request: TransactionRequest) -> str:
        """Implementar início de transação"""
        # Implementar lógica específica do terminal
        pass
    
    # Implementar outros métodos abstratos...
```

### **Passo 2: Registrar na Factory**

```python
# apps/api/services/payment/terminal/factory.py

from .novo_terminal import NovoTerminalAdapter

class TerminalAdapterFactory:
    _adapters = {
        "mock": MockTerminalAdapter,
        "stone": StoneTerminalAdapter,
        "sicredi": SicrediTerminalAdapter,
        "novo_terminal": NovoTerminalAdapter,  # ← Adicionar aqui
    }
```

### **Passo 3: Atualizar __init__.py**

```python
# apps/api/services/payment/terminal/__init__.py

from .novo_terminal import NovoTerminalAdapter

__all__ = [
    "TerminalAdapter",
    "NovoTerminalAdapter",  # ← Adicionar aqui
    # ... outros
]
```

### **Passo 4: Configurar no main.py**

```python
# apps/api/main.py

async def setup_default_terminals():
    terminal_type = os.getenv("TERMINAL_TYPE", "mock")
    
    # Configurações específicas por tipo
    if terminal_type == "novo_terminal":
        default_configs["default"]["terminal"]["novo_terminal"] = {
            "merchant_id": os.getenv("NOVO_MERCHANT_ID"),
            "api_key": os.getenv("NOVO_API_KEY"),
            # Configurações específicas
        }
```

### **Passo 5: Criar Testes**

```python
# tests/test_novo_terminal.py

import pytest
from apps.api.services.payment.terminal.novo_terminal import NovoTerminalAdapter

class TestNovoTerminalAdapter:
    
    @pytest.fixture
    def terminal_config(self):
        return {
            "type": "novo_terminal",
            "connection_type": "serial",
            "port": "COM1",
            "novo_terminal": {
                "merchant_id": "123456789"
            }
        }
    
    def test_initialization(self, terminal_config):
        terminal = NovoTerminalAdapter(terminal_config)
        assert terminal.merchant_id == "123456789"
    
    @pytest.mark.asyncio
    async def test_connection(self, terminal_config):
        # Implementar testes específicos
        pass
```

### **Passo 6: Documentar**

```markdown
# docs/integracao-novo-terminal.md

# Integração com Novo Terminal

## Configuração
- Merchant ID: Obtido do provedor
- Porta: COM1 ou /dev/ttyUSB0
- Baudrate: 115200

## Variáveis de Ambiente
export TERMINAL_TYPE=novo_terminal
export NOVO_MERCHANT_ID=123456789
```

## 📋 **Template Completo**

### **Estrutura de Arquivos**
```
apps/api/services/payment/terminal/
├── base.py                    # Interface base (não alterar)
├── protocols.py               # Protocolos de comunicação (não alterar)
├── factory.py                 # ← Registrar novo terminal
├── novo_terminal.py           # ← Criar adaptador específico
└── __init__.py               # ← Adicionar import

docs/
└── integracao-novo-terminal.md  # ← Documentar uso

tests/
└── test_novo_terminal.py        # ← Criar testes

config/
└── novo-terminal.example.json   # ← Exemplos de configuração
```

### **Métodos Obrigatórios**
```python
class NovoTerminalAdapter(TerminalAdapter):
    
    # Métodos abstratos que DEVEM ser implementados:
    async def connect(self) -> bool
    async def disconnect(self) -> bool
    async def is_connected(self) -> bool
    async def get_terminal_info(self) -> TerminalInfo
    async def start_transaction(self, request: TransactionRequest) -> str
    async def get_transaction_status(self, transaction_id: str) -> TransactionResponse
    async def cancel_transaction(self, transaction_id: str) -> bool
    async def confirm_transaction(self, transaction_id: str) -> TransactionResponse
    async def print_receipt(self, transaction_id: str, receipt_type: str) -> bool
    async def print_custom_text(self, text: str) -> bool
    async def get_supported_payment_methods(self) -> List[PaymentMethod]
    async def configure_terminal(self, settings: Dict[str, Any]) -> bool
```

## 🔧 **Protocolos de Comunicação Disponíveis**

### **Serial/USB**
```python
from .protocols import SerialProtocol

protocol = SerialProtocol(
    config=conn_config,
    port="/dev/ttyUSB0",
    baudrate=115200,
    bytesize=8,
    parity='N',
    stopbits=1
)
```

### **TCP/IP**
```python
from .protocols import TCPProtocol

protocol = TCPProtocol(
    config=conn_config,
    host="192.168.1.100",
    port=8080
)
```

### **Bluetooth**
```python
from .protocols import BluetoothProtocol

protocol = BluetoothProtocol(
    config=conn_config,
    device_address="00:11:22:33:44:55",
    port=1
)
```

### **USB Direto**
```python
from .protocols import USBProtocol

protocol = USBProtocol(
    config=conn_config,
    vendor_id=0x1234,
    product_id=0x5678
)
```

## 🧪 **Exemplo Prático: PagSeguro**

Vou mostrar como seria implementar o PagSeguro:

### **1. Pesquisar Documentação**
- Protocolo de comunicação
- Comandos específicos
- Códigos de resposta
- Métodos de pagamento suportados

### **2. Implementar Adaptador**
```python
class PagSeguroTerminalAdapter(TerminalAdapter):
    
    COMMANDS = {
        "INIT": b"\x02INIT\x03",
        "SALE": b"\x02SALE\x03",
        "STATUS": b"\x02STATUS\x03"
    }
    
    def __init__(self, config):
        super().__init__(config)
        self.pagseguro_config = config.get("pagseguro", {})
        self.merchant_id = self.pagseguro_config.get("merchant_id")
        
        # PagSeguro usa baudrate 115200
        self.protocol = SerialProtocol(
            port=config.get("port"),
            baudrate=115200
        )
    
    async def connect(self):
        # Implementar protocolo específico PagSeguro
        pass
```

### **3. Registrar e Testar**
```python
# factory.py
_adapters = {
    "pagseguro": PagSeguroTerminalAdapter
}

# Usar
export TERMINAL_TYPE=pagseguro
export PAGSEGURO_MERCHANT_ID=123456789
```

## 🚀 **Vantagens da Arquitetura**

### **Para Desenvolvedores**
- ✅ **Interface padronizada** - Mesma API para todos
- ✅ **Protocolos prontos** - Serial, TCP, Bluetooth, USB
- ✅ **Testes automatizados** - Framework de testes
- ✅ **Documentação consistente** - Templates prontos

### **Para o Negócio**
- ✅ **Time to Market** - Implementação rápida
- ✅ **Flexibilidade** - Troca fácil de terminais
- ✅ **Escalabilidade** - Suporte a múltiplos terminais
- ✅ **Manutenibilidade** - Código organizado

### **Para Clientes**
- ✅ **Zero downtime** - Troca sem parar sistema
- ✅ **Mesma interface** - API não muda
- ✅ **Configuração simples** - Apenas variáveis de ambiente
- ✅ **Suporte completo** - Todas funcionalidades disponíveis

## 📊 **Terminais Suportados Atualmente**

| Terminal | Status | Implementação | Métodos Suportados |
|----------|--------|---------------|-------------------|
| **Mock** | ✅ Completo | 100% | Todos (simulado) |
| **Stone** | ✅ Completo | 100% | Débito, Crédito, Contactless |
| **Sicredi** | ✅ Completo | 100% | Débito, Crédito, Contactless, Voucher |
| **PagSeguro** | 🔄 Exemplo | 50% | Débito, Crédito, PIX |
| **MercadoPago** | ⏳ Pendente | 0% | - |
| **PagBank** | ⏳ Pendente | 0% | - |

## 🎯 **Roadmap de Implementação**

### **Próximos Terminais (Prioridade)**
1. **PagSeguro** - Finalizar implementação
2. **MercadoPago** - Implementar do zero
4. **PagBank** - Implementar do zero

### **Tempo Estimado por Terminal**
- **Pesquisa e documentação**: 1-2 dias
- **Implementação do adaptador**: 2-3 dias
- **Testes e validação**: 1-2 dias
- **Documentação**: 1 dia
- **Total por terminal**: 5-8 dias

## ✅ **Conclusão**

A arquitetura do sistema foi projetada para **máxima extensibilidade**. Adicionar um novo terminal é um processo:

- 🚀 **Rápido** - 5-8 dias por terminal
- 🔧 **Padronizado** - Mesma estrutura para todos
- 🧪 **Testável** - Framework de testes pronto
- 📚 **Documentado** - Templates e exemplos
- 🔄 **Flexível** - Troca sem downtime

**Seu cliente nunca ficará "preso" a um terminal específico!** 