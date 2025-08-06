# 🔧 Exemplo Prático: Implementação Multi-Tenant

Este documento demonstra como adaptar o sistema atual para multi-tenant através de exemplos práticos de código.

---

## 📋 **Exemplo 1: Adaptação do Router de Customers**

### **Antes (Código Atual):**

```python
@router.get("/search", response_model=Optional[Customer])
async def search_customer(
    q: str = Query(..., min_length=3, description="Termo de busca (nome ou CPF)"),
    tenant_id: UUID = Query(..., description="ID do tenant"),
    db: Session = Depends(get_db)
):
    # Lógica de busca...
```

### **Depois (Multi-Tenant):**

```python
@router.get("/search", response_model=Optional[Customer])
async def search_customer(
    q: str = Query(..., min_length=3, description="Termo de busca (nome ou CPF)"),
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),  # Extraído do JWT
    config_service: TenantConfigService = Depends(get_tenant_config_service)
):
    """
    Busca cliente com isolamento completo por tenant.
    Configurações específicas do tenant são aplicadas automaticamente.
    """
    
    # Validar limites do tenant
    limits = await get_tenant_limits(tenant_id)
    if not _validate_search_limits(q, limits):
        raise HTTPException(status_code=429, detail="Limite de busca excedido")
    
    # Aplicar configurações específicas do tenant
    tenant_config = config_service.get_tenant_config(tenant_id)
    search_config = tenant_config.get("search", {})
    
    # Lógica de busca com configurações do tenant...
    return await _search_customer_with_config(q, tenant_id, db, search_config)
```

---

## 📋 **Exemplo 2: Sistema de Pagamento Multi-Tenant**

### **Antes (Código Atual):**

```python
# Configuração hardcoded
STONE_API_KEY = os.getenv("STONE_API_KEY")
STONE_MERCHANT_ID = os.getenv("STONE_MERCHANT_ID")

# Uso direto
payment_adapter = StoneAdapter(api_key=STONE_API_KEY, merchant_id=STONE_MERCHANT_ID)
```

### **Depois (Multi-Tenant):**

```python
# apps/api/routers/payments.py
@router.post("/process")
async def process_payment(
    payment_data: PaymentRequest,
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    payment_adapter: PaymentAdapter = Depends(get_payment_adapter),
    limits: dict = Depends(get_tenant_limits)
):
    """
    Processa pagamento com adaptador específico do tenant.
    """
    
    # Validar limites do tenant
    if payment_data.amount > limits.get("max_payment_amount", 10000):
        raise HTTPException(
            status_code=400, 
            detail=f"Valor excede limite máximo de R$ {limits.get('max_payment_amount'):.2f}"
        )
    
    # Processar com adaptador específico do tenant
    result = await payment_adapter.process_payment(payment_data)
    
    # Log específico do tenant
    logger.info(f"[Tenant: {tenant_id}] Pagamento processado: {result.id}")
    
    return result
```

---

## 📋 **Exemplo 3: WebSocket Multi-Tenant**

### **Antes (Código Atual):**

```python
@app.websocket("/ws/queue")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Lógica genérica para todos os tenants
```

### **Depois (Multi-Tenant):**

```python
# apps/api/websocket/queue_websocket.py
@app.websocket("/ws/queue/{tenant_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    tenant_id: UUID,
    ws_manager: MultiTenantWebSocketManager = Depends(get_ws_manager)
):
    """
    WebSocket isolado por tenant.
    """
    await ws_manager.connect(websocket, tenant_id)
    
    try:
        while True:
            # Receber mensagens específicas do tenant
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Processar com configurações do tenant
            await _process_tenant_message(tenant_id, message, ws_manager)
            
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, tenant_id)

async def _process_tenant_message(tenant_id: UUID, message: dict, ws_manager):
    """Processa mensagem com configurações específicas do tenant"""
    
    # Carregar configurações do tenant
    config_service = TenantConfigService(db)
    tenant_config = config_service.get_tenant_config(tenant_id)
    
    # Aplicar regras específicas do tenant
    if tenant_config.get("queue", {}).get("enable_priority", False):
        # Lógica de prioridade específica do tenant
        pass
    
    # Broadcast para outros WebSockets do mesmo tenant
    await ws_manager.broadcast_to_tenant(tenant_id, message)
```

---

## 📋 **Exemplo 4: Sistema de Configuração Dinâmica**

### **Implementação do Serviço de Configuração:**

```python
# apps/api/services/tenant_config_service.py
class TenantConfigService:
    def __init__(self, db: Session):
        self.db = db
        self._cache = {}  # Cache para configurações
    
    def get_tenant_config(self, tenant_id: UUID) -> Dict[str, Any]:
        """Retorna configuração do tenant com cache"""
        
        # Verificar cache primeiro
        if tenant_id in self._cache:
            return self._cache[tenant_id]
        
        # Buscar no banco
        config = self.db.query(TenantConfig).filter(
            TenantConfig.tenant_id == tenant_id
        ).first()
        
        if not config:
            # Usar configuração padrão
            config_data = self._get_default_config()
        else:
            config_data = {
                "payment": config.payment_config,
                "printer": config.printer_config,
                "notification": config.notification_config,
                "limits": config.limits_config,
                "ui": config.ui_config,
                "integration": config.integration_config
            }
        
        # Cache por 5 minutos
        self._cache[tenant_id] = config_data
        return config_data
    
    def update_tenant_config(self, tenant_id: UUID, config_data: Dict[str, Any]):
        """Atualiza configuração do tenant"""
        
        config = self.db.query(TenantConfig).filter(
            TenantConfig.tenant_id == tenant_id
        ).first()
        
        if not config:
            config = TenantConfig(tenant_id=tenant_id)
            self.db.add(config)
        
        # Atualizar configurações
        config.payment_config = config_data.get("payment", {})
        config.printer_config = config_data.get("printer", {})
        config.notification_config = config_data.get("notification", {})
        config.limits_config = config_data.get("limits", {})
        config.ui_config = config_data.get("ui", {})
        config.integration_config = config_data.get("integration", {})
        
        self.db.commit()
        
        # Limpar cache
        self._cache.pop(tenant_id, None)
```

---

## 📋 **Exemplo 5: Middleware de Validação**

### **Implementação do Middleware:**

```python
# apps/api/middleware/tenant_validation.py
class TenantValidationMiddleware:
    def __init__(self, app):
        self.app = app
        self.db = SessionLocal()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Extrair tenant_id
            tenant_id = self._extract_tenant_id(request)
            
            if tenant_id:
                # Validar tenant
                if not await self._validate_tenant(tenant_id):
                    response = JSONResponse(
                        status_code=403,
                        content={"detail": "Tenant inválido ou inativo"}
                    )
                    await response(scope, receive, send)
                    return
                
                # Adicionar ao scope
                scope["tenant_id"] = tenant_id
        
        await self.app(scope, receive, send)
    
    def _extract_tenant_id(self, request: Request) -> Optional[UUID]:
        """Extrai tenant_id de diferentes fontes"""
        
        # 1. Header X-Tenant-ID
        tenant_header = request.headers.get("X-Tenant-ID")
        if tenant_header:
            try:
                return UUID(tenant_header)
            except ValueError:
                pass
        
        # 2. Query parameter
        tenant_query = request.query_params.get("tenant_id")
        if tenant_query:
            try:
                return UUID(tenant_query)
            except ValueError:
                pass
        
        # 3. JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
                return UUID(payload.get("tenant_id"))
            except:
                pass
        
        return None
    
    async def _validate_tenant(self, tenant_id: UUID) -> bool:
        """Valida se tenant existe e está ativo"""
        tenant = self.db.query(Tenant).filter(
            Tenant.id == tenant_id,
            Tenant.is_active == True
        ).first()
        
        return tenant is not None
```

---

## 📋 **Exemplo 6: Adaptação de Frontend**

### **Configuração Dinâmica no Frontend:**

```typescript
// apps/totem-client/src/services/tenantConfigService.ts
export class TenantConfigService {
    private config: TenantConfig | null = null;
    private tenantId: string;

    constructor(tenantId: string) {
        this.tenantId = tenantId;
    }

    async loadConfig(): Promise<TenantConfig> {
        const response = await fetch(`/api/tenants/${this.tenantId}/config`);
        this.config = await response.json();
        return this.config;
    }

    getUIConfig(): UIConfig {
        return this.config?.ui || this.getDefaultUIConfig();
    }

    getPaymentConfig(): PaymentConfig {
        return this.config?.payment || this.getDefaultPaymentConfig();
    }

    private getDefaultUIConfig(): UIConfig {
        return {
            theme: "default",
            primaryColor: "#007bff",
            secondaryColor: "#6c757d",
            logoUrl: null,
            customCSS: ""
        };
    }
}

// Uso no componente
const TenantProvider: React.FC<{ tenantId: string; children: React.ReactNode }> = ({ 
    tenantId, 
    children 
}) => {
    const [config, setConfig] = useState<TenantConfig | null>(null);

    useEffect(() => {
        const configService = new TenantConfigService(tenantId);
        configService.loadConfig().then(setConfig);
    }, [tenantId]);

    if (!config) {
        return <LoadingSpinner />;
    }

    return (
        <TenantContext.Provider value={config}>
            {children}
        </TenantContext.Provider>
    );
};
```

---

## 📋 **Exemplo 7: Sistema de Logs Multi-Tenant**

### **Implementação de Logs Isolados:**

```python
# apps/api/services/logging/multi_tenant_logger.py
import logging
from typing import Dict
from uuid import UUID
import json

class MultiTenantLogger:
    def __init__(self):
        self.loggers: Dict[UUID, logging.Logger] = {}
    
    def get_logger(self, tenant_id: UUID) -> logging.Logger:
        """Retorna logger específico do tenant"""
        
        if tenant_id not in self.loggers:
            # Criar logger específico do tenant
            logger = logging.getLogger(f"tenant_{tenant_id}")
            
            # Configurar handler para arquivo específico
            handler = logging.FileHandler(f"logs/tenant_{tenant_id}.log")
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            self.loggers[tenant_id] = logger
        
        return self.loggers[tenant_id]
    
    def log_tenant_event(self, tenant_id: UUID, event: str, data: dict = None):
        """Loga evento específico do tenant"""
        logger = self.get_logger(tenant_id)
        
        log_data = {
            "tenant_id": str(tenant_id),
            "event": event,
            "data": data or {}
        }
        
        logger.info(json.dumps(log_data))

# Uso nos routers
@router.post("/tickets")
async def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    logger: MultiTenantLogger = Depends(get_tenant_logger)
):
    """Cria ticket com log específico do tenant"""
    
    # Criar ticket
    ticket = Ticket(**ticket_data.dict(), tenant_id=tenant_id)
    db.add(ticket)
    db.commit()
    
    # Log específico do tenant
    logger.log_tenant_event(
        tenant_id=tenant_id,
        event="ticket_created",
        data={
            "ticket_id": str(ticket.id),
            "customer_name": ticket.customer_name,
            "amount": float(ticket.amount)
        }
    )
    
    return ticket
```

---

## 🎯 **Benefícios dos Exemplos**

### **1. Isolamento Completo**
- Cada tenant tem seus próprios dados, configurações e logs
- Não há interferência entre tenants
- Segurança garantida por design

### **2. Configuração Dinâmica**
- Adaptadores de pagamento específicos por tenant
- Configurações de UI/UX personalizadas
- Limites e regras de negócio flexíveis

### **3. Escalabilidade**
- Uma infraestrutura serve múltiplos clientes
- Recursos compartilhados de forma eficiente
- Monitoramento individual por tenant

### **4. Manutenibilidade**
- Código organizado e modular
- Testes isolados por tenant
- Debugging facilitado

---

## 🚀 **Próximos Passos**

1. **Implementar os exemplos básicos** (Sprint 1)
2. **Criar testes unitários** para cada componente
3. **Implementar monitoramento** específico por tenant
4. **Criar documentação** de uso para cada tenant
5. **Implementar migração** gradual do sistema atual

---

*Estes exemplos demonstram como transformar o sistema atual em uma solução multi-tenant robusta e escalável.* 