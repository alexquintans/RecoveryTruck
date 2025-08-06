# 📚 Estudo: Adaptação do Sistema para Multi-Tenant

## 🎯 **Objetivo do Estudo**

Analisar como adaptar o sistema atual de totens para um modelo multi-tenant robusto, permitindo que múltiplas empresas utilizem a mesma infraestrutura de forma completamente isolada.

---

## 📊 **Análise da Situação Atual**

### ✅ **O que já está implementado:**

1. **Modelo de Dados Multi-Tenant**
   - Tabela `tenants` com configurações básicas
   - Todas as entidades principais já possuem `tenant_id`
   - Relacionamentos estabelecidos entre tenant e outras entidades

2. **Estrutura de Isolamento**
   - Queries já filtram por `tenant_id`
   - Endpoints recebem `tenant_id` como parâmetro
   - Separação de dados por tenant

3. **Configurações por Tenant**
   - Adaptadores de pagamento específicos
   - Limites e regras de negócio
   - Configurações de terminais

### ⚠️ **Pontos que precisam de melhoria:**

1. **Autenticação e Autorização**
   - Sistema de JWT não considera tenant
   - Falta middleware de validação de tenant
   - Permissões não são validadas por tenant

2. **Configuração Dinâmica**
   - Configurações hardcoded no `settings.py`
   - Falta sistema de configuração por tenant
   - Adaptadores não são carregados dinamicamente

3. **Isolamento de Recursos**
   - WebSockets não são isolados por tenant
   - Filas não são segregadas
   - Logs não são separados por tenant

---

## 🏗️ **Estratégia de Implementação**

### **Fase 1: Autenticação e Autorização Multi-Tenant**

#### 1.1 **Sistema de JWT Multi-Tenant**

```python
# apps/api/auth/multi_tenant_jwt.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from uuid import UUID

class MultiTenantJWT:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(self, data: dict, tenant_id: UUID) -> str:
        """Cria token JWT incluindo tenant_id"""
        to_encode = data.copy()
        to_encode.update({"tenant_id": str(tenant_id)})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verifica token e retorna payload com tenant_id"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

# Dependency para extrair tenant do token
async def get_current_tenant(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> UUID:
    jwt_handler = MultiTenantJWT(settings.JWT_SECRET)
    payload = jwt_handler.verify_token(credentials.credentials)
    return UUID(payload.get("tenant_id"))
```

#### 1.2 **Middleware de Validação de Tenant**

```python
# apps/api/middleware/tenant_validation.py
from fastapi import Request, HTTPException
from typing import Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

class TenantValidationMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Extrair tenant_id do header ou query params
            tenant_id = self._extract_tenant_id(request)
            
            if tenant_id:
                # Validar se tenant existe e está ativo
                if not await self._validate_tenant(tenant_id):
                    raise HTTPException(status_code=403, detail="Tenant inválido")
                
                # Adicionar tenant_id ao scope para uso posterior
                scope["tenant_id"] = tenant_id
        
        await self.app(scope, receive, send)
    
    def _extract_tenant_id(self, request: Request) -> Optional[UUID]:
        """Extrai tenant_id de diferentes fontes"""
        # 1. Header X-Tenant-ID
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            return UUID(tenant_header)
        
        # 2. Query parameter tenant_id
        tenant_query = request.query_params.get("tenant_id")
        if tenant_query:
            return UUID(tenant_query)
        
        # 3. JWT token (se disponível)
        # Implementar extração do token JWT
        
        return None
    
    async def _validate_tenant(self, tenant_id: UUID) -> bool:
        """Valida se tenant existe e está ativo"""
        # Implementar validação no banco de dados
        pass
```

### **Fase 2: Sistema de Configuração Dinâmica**

#### 2.1 **Configuração por Tenant**

```python
# apps/api/models/tenant_config.py
from sqlalchemy import Column, String, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class TenantConfig(Base):
    __tablename__ = "tenant_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    # Configurações de Pagamento
    payment_adapter = Column(String(50), nullable=False, default="sicredi")
    payment_config = Column(JSON, nullable=False, default={})
    
    # Configurações de Impressão
    printer_config = Column(JSON, nullable=False, default={})
    
    # Configurações de Notificação
    notification_config = Column(JSON, nullable=False, default={})
    
    # Configurações de Limites
    limits_config = Column(JSON, nullable=False, default={})
    
    # Configurações de UI/UX
    ui_config = Column(JSON, nullable=False, default={})
    
    # Configurações de Integração
    integration_config = Column(JSON, nullable=False, default={})
```

#### 2.2 **Serviço de Configuração**

```python
# apps/api/services/config_service.py
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from uuid import UUID
import json

class TenantConfigService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_tenant_config(self, tenant_id: UUID) -> Dict[str, Any]:
        """Retorna configuração completa do tenant"""
        config = self.db.query(TenantConfig).filter(
            TenantConfig.tenant_id == tenant_id
        ).first()
        
        if not config:
            return self._get_default_config()
        
        return {
            "payment": config.payment_config,
            "printer": config.printer_config,
            "notification": config.notification_config,
            "limits": config.limits_config,
            "ui": config.ui_config,
            "integration": config.integration_config
        }
    
    def get_payment_config(self, tenant_id: UUID) -> Dict[str, Any]:
        """Retorna configuração específica de pagamento"""
        config = self.get_tenant_config(tenant_id)
        return config.get("payment", {})
    
    def get_ui_config(self, tenant_id: UUID) -> Dict[str, Any]:
        """Retorna configuração de UI/UX do tenant"""
        config = self.get_tenant_config(tenant_id)
        return config.get("ui", {})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão para novos tenants"""
        return {
            "payment": {
                "adapter": "sicredi",
                "environment": "production",
                "timeout": 30,
                "retry_attempts": 3
            },
            "printer": {
                "type": "usb",
                "vendor_id": "0x0483",
                "product_id": "0x5740"
            },
            "notification": {
                "enabled": True,
                "webhook_url": None,
                "email_enabled": False
            },
            "limits": {
                "max_payment_amount": 10000.00,
                "max_daily_transactions": 1000,
                "max_concurrent_sessions": 10
            },
            "ui": {
                "theme": "default",
                "logo_url": None,
                "primary_color": "#007bff",
                "secondary_color": "#6c757d"
            },
            "integration": {
                "webhook_enabled": False,
                "api_rate_limit": 100
            }
        }
```

### **Fase 3: Isolamento de Recursos**

#### 3.1 **WebSocket Multi-Tenant**

```python
# apps/api/websocket/multi_tenant_manager.py
from fastapi import WebSocket
from typing import Dict, Set
from uuid import UUID
import json

class MultiTenantWebSocketManager:
    def __init__(self):
        self.connections: Dict[UUID, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, tenant_id: UUID):
        """Conecta WebSocket ao tenant específico"""
        await websocket.accept()
        
        if tenant_id not in self.connections:
            self.connections[tenant_id] = set()
        
        self.connections[tenant_id].add(websocket)
    
    async def disconnect(self, websocket: WebSocket, tenant_id: UUID):
        """Desconecta WebSocket do tenant"""
        if tenant_id in self.connections:
            self.connections[tenant_id].discard(websocket)
            
            if not self.connections[tenant_id]:
                del self.connections[tenant_id]
    
    async def broadcast_to_tenant(self, tenant_id: UUID, message: dict):
        """Envia mensagem para todos os WebSockets do tenant"""
        if tenant_id not in self.connections:
            return
        
        disconnected = set()
        for websocket in self.connections[tenant_id]:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.add(websocket)
        
        # Remove conexões desconectadas
        for websocket in disconnected:
            self.connections[tenant_id].discard(websocket)
    
    async def send_to_equipment(self, tenant_id: UUID, equipment_id: str, message: dict):
        """Envia mensagem para equipamento específico do tenant"""
        # Implementar lógica específica por equipamento
        pass
```

#### 3.2 **Sistema de Filas Multi-Tenant**

```python
# apps/api/services/queue/multi_tenant_queue.py
from typing import Dict, List, Optional
from uuid import UUID
import asyncio
import logging

logger = logging.getLogger(__name__)

class MultiTenantQueueManager:
    def __init__(self):
        self.queues: Dict[UUID, List] = {}
        self.locks: Dict[UUID, asyncio.Lock] = {}
    
    def get_queue(self, tenant_id: UUID) -> List:
        """Retorna fila específica do tenant"""
        if tenant_id not in self.queues:
            self.queues[tenant_id] = []
            self.locks[tenant_id] = asyncio.Lock()
        return self.queues[tenant_id]
    
    async def add_to_queue(self, tenant_id: UUID, ticket_id: UUID, priority: str = "normal"):
        """Adiciona ticket à fila do tenant"""
        async with self.locks[tenant_id]:
            queue = self.get_queue(tenant_id)
            
            # Implementar lógica de prioridade
            if priority == "high":
                queue.insert(0, ticket_id)
            else:
                queue.append(ticket_id)
            
            logger.info(f"Ticket {ticket_id} adicionado à fila do tenant {tenant_id}")
    
    async def remove_from_queue(self, tenant_id: UUID, ticket_id: UUID):
        """Remove ticket da fila do tenant"""
        async with self.locks[tenant_id]:
            queue = self.get_queue(tenant_id)
            if ticket_id in queue:
                queue.remove(ticket_id)
                logger.info(f"Ticket {ticket_id} removido da fila do tenant {tenant_id}")
    
    async def get_next_ticket(self, tenant_id: UUID) -> Optional[UUID]:
        """Retorna próximo ticket da fila do tenant"""
        async with self.locks[tenant_id]:
            queue = self.get_queue(tenant_id)
            return queue[0] if queue else None
    
    def get_queue_status(self, tenant_id: UUID) -> dict:
        """Retorna status da fila do tenant"""
        queue = self.get_queue(tenant_id)
        return {
            "total_tickets": len(queue),
            "estimated_wait_time": len(queue) * 5,  # 5 min por ticket
            "queue_position": len(queue)
        }
```

### **Fase 4: Adaptadores Dinâmicos**

#### 4.1 **Factory de Adaptadores Multi-Tenant**

```python
# apps/api/services/payment/multi_tenant_factory.py
from typing import Dict, Type
from uuid import UUID
from .adapters.base import PaymentAdapter
from .adapters.sicredi import SicrediAdapter
from .adapters.stone import StoneAdapter
from .adapters.mercadopago import MercadoPagoAdapter

class MultiTenantPaymentFactory:
    def __init__(self):
        self.adapters: Dict[str, Type[PaymentAdapter]] = {
            "sicredi": SicrediAdapter,
            "stone": StoneAdapter,
            "mercadopago": MercadoPagoAdapter
        }
    
    def get_adapter(self, tenant_id: UUID, config_service) -> PaymentAdapter:
        """Retorna adaptador configurado para o tenant"""
        payment_config = config_service.get_payment_config(tenant_id)
        adapter_name = payment_config.get("adapter", "sicredi")
        
        if adapter_name not in self.adapters:
            raise ValueError(f"Adaptador '{adapter_name}' não encontrado")
        
        adapter_class = self.adapters[adapter_name]
        return adapter_class(tenant_id, payment_config)
    
    def register_adapter(self, name: str, adapter_class: Type[PaymentAdapter]):
        """Registra novo adaptador"""
        self.adapters[name] = adapter_class
```

### **Fase 5: Middleware e Dependencies**

#### 5.1 **Dependency Injection Multi-Tenant**

```python
# apps/api/dependencies/multi_tenant.py
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from database import get_db
from services.config_service import TenantConfigService
from services.payment.multi_tenant_factory import MultiTenantPaymentFactory

async def get_tenant_config_service(
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant)
) -> TenantConfigService:
    """Dependency para serviço de configuração do tenant"""
    return TenantConfigService(db)

async def get_payment_adapter(
    config_service: TenantConfigService = Depends(get_tenant_config_service),
    tenant_id: UUID = Depends(get_current_tenant)
):
    """Dependency para adaptador de pagamento do tenant"""
    factory = MultiTenantPaymentFactory()
    return factory.get_adapter(tenant_id, config_service)

async def get_tenant_limits(
    config_service: TenantConfigService = Depends(get_tenant_config_service),
    tenant_id: UUID = Depends(get_current_tenant)
) -> dict:
    """Dependency para limites do tenant"""
    config = config_service.get_tenant_config(tenant_id)
    return config.get("limits", {})
```

---

## 🚀 **Plano de Implementação**

### **Sprint 1: Fundação Multi-Tenant**
- [ ] Implementar sistema de JWT multi-tenant
- [ ] Criar middleware de validação de tenant
- [ ] Implementar sistema de configuração dinâmica
- [ ] Criar tabelas de configuração por tenant

### **Sprint 2: Isolamento de Recursos**
- [ ] Implementar WebSocket manager multi-tenant
- [ ] Criar sistema de filas segregadas
- [ ] Implementar logs separados por tenant
- [ ] Criar sistema de métricas por tenant

### **Sprint 3: Adaptadores Dinâmicos**
- [ ] Implementar factory de adaptadores
- [ ] Criar sistema de configuração de pagamento
- [ ] Implementar fallback por tenant
- [ ] Criar sistema de validação de limites

### **Sprint 4: UI/UX Multi-Tenant**
- [ ] Implementar configuração de tema por tenant
- [ ] Criar sistema de branding dinâmico
- [ ] Implementar configurações de UI por tenant
- [ ] Criar sistema de personalização

### **Sprint 5: Testes e Validação**
- [ ] Criar testes unitários multi-tenant
- [ ] Implementar testes de integração
- [ ] Criar testes de performance
- [ ] Validar isolamento completo

---

## 📈 **Benefícios Esperados**

### **Para o Negócio:**
1. **Escalabilidade**: Uma infraestrutura serve múltiplos clientes
2. **Isolamento**: Dados e configurações completamente separados
3. **Flexibilidade**: Cada tenant com suas regras específicas
4. **Redução de Custos**: Compartilhamento de infraestrutura

### **Para Desenvolvimento:**
1. **Manutenibilidade**: Código organizado por responsabilidades
2. **Testabilidade**: Testes isolados por tenant
3. **Flexibilidade**: Configurações dinâmicas
4. **Segurança**: Isolamento completo de dados

### **Para Operação:**
1. **Monitoramento**: Métricas individuais por tenant
2. **Debugging**: Logs segregados
3. **Backup**: Estratégias específicas por tenant
4. **Deploy**: Rollouts independentes

---

## 🔧 **Próximos Passos**

1. **Validação da Arquitetura**: Revisar proposta com equipe
2. **Criação de POC**: Implementar protótipo básico
3. **Definição de Prioridades**: Estabelecer roadmap detalhado
4. **Início da Implementação**: Começar pela Sprint 1

---

## 📚 **Recursos Adicionais**

- [Documentação Multi-Tenant](docs/Geral/SistemaMultiTenant.md)
- [Arquitetura do Sistema](docs/architecture.md)
- [Modelo de Dados](docs/banco%20de%20dados.md)
- [Configurações de Pagamento](docs/Pagamento/)

---

*Este estudo fornece uma base sólida para a implementação de um sistema multi-tenant robusto e escalável.* 