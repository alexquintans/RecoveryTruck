# 🔗 Comunicação Totem-Painel: Identificação de Tenant

## 🎯 **Problema Central**

Como o **totem** e o **painel do operador** podem se comunicar para identificar qual tenant específico devem usar, garantindo isolamento completo entre diferentes empresas?

---

## 📊 **Análise da Situação Atual**

### **Como Funciona Hoje:**

1. **Variável de Ambiente Hardcoded:**
   ```env
   VITE_TENANT_ID=7f02a566-2406-436d-b10d-90ecddd3fe2d
   ```

2. **WebSocket com Tenant ID:**
   ```javascript
   // Totem
   ws://api.com/ws?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=totem
   
   // Painel
   ws://api.com/ws?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=operator
   ```

3. **Headers HTTP:**
   ```javascript
   headers: {
     'X-Tenant-Id': '7f02a566-2406-436d-b10d-90ecddd3fe2d'
   }
   ```

### **Problemas Identificados:**

1. **Configuração Manual:** Cada instalação precisa configurar manualmente o tenant
2. **Sem Flexibilidade:** Não permite trocar tenant dinamicamente
3. **Sem Validação:** Não verifica se o tenant existe ou está ativo
4. **Sem Isolamento:** Mesmo tenant para todos os equipamentos

---

## 🏗️ **Soluções Propostas**

### **Solução 1: Identificação por Hardware (Recomendada)**

#### **1.1 Identificação por MAC Address**

```python
# apps/api/services/equipment_identification.py
import uuid
import hashlib
from typing import Optional
from sqlalchemy.orm import Session

class EquipmentIdentificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_tenant_by_mac(self, mac_address: str) -> Optional[str]:
        """Identifica tenant pelo MAC address do equipamento"""
        
        # Buscar equipamento pelo MAC
        equipment = self.db.query(Equipment).filter(
            Equipment.mac_address == mac_address
        ).first()
        
        if equipment:
            return str(equipment.tenant_id)
        
        return None
    
    def register_equipment(self, mac_address: str, tenant_id: str, equipment_type: str):
        """Registra novo equipamento"""
        
        equipment = Equipment(
            mac_address=mac_address,
            tenant_id=tenant_id,
            type=equipment_type,
            identifier=f"{equipment_type}_{mac_address[-6:]}"
        )
        
        self.db.add(equipment)
        self.db.commit()
        
        return equipment
```

#### **1.2 Frontend - Detecção Automática**

```typescript
// apps/totem-client/src/services/equipmentIdentification.ts
export class EquipmentIdentificationService {
    private macAddress: string | null = null;
    
    async getMacAddress(): Promise<string> {
        if (this.macAddress) return this.macAddress;
        
        try {
            // Tentar obter MAC via WebRTC (funciona em HTTPS)
            const response = await fetch('/api/equipment/mac');
            const data = await response.json();
            this.macAddress = data.mac_address;
            return this.macAddress;
        } catch (error) {
            // Fallback: gerar MAC baseado em características do navegador
            this.macAddress = this.generateFallbackMac();
            return this.macAddress;
        }
    }
    
    private generateFallbackMac(): string {
        const userAgent = navigator.userAgent;
        const screen = `${screen.width}x${screen.height}`;
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        
        const hash = btoa(userAgent + screen + timezone);
        return hash.substring(0, 17).replace(/[^0-9A-F]/gi, '0');
    }
    
    async identifyTenant(): Promise<string> {
        const macAddress = await this.getMacAddress();
        
        const response = await fetch(`/api/equipment/identify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mac_address: macAddress,
                equipment_type: 'totem',
                user_agent: navigator.userAgent,
                screen_resolution: `${screen.width}x${screen.height}`,
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
            })
        });
        
        const data = await response.json();
        return data.tenant_id;
    }
}
```

### **Solução 2: Identificação por URL/Subdomínio**

#### **2.1 Subdomínios por Tenant**

```nginx
# nginx.conf
server {
    listen 80;
    server_name ~^(?<tenant>.+)\.totem\.com$;
    
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header X-Tenant-Subdomain $tenant;
    }
}
```

#### **2.2 Backend - Extração do Subdomínio**

```python
# apps/api/middleware/subdomain_tenant.py
from fastapi import Request, HTTPException
from typing import Optional

class SubdomainTenantMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Extrair tenant do subdomínio
            tenant = self._extract_tenant_from_host(request.headers.get("host", ""))
            
            if tenant:
                scope["tenant_id"] = tenant
        
        await self.app(scope, receive, send)
    
    def _extract_tenant_from_host(self, host: str) -> Optional[str]:
        """Extrai tenant do host (ex: recovery.painel.com -> recovery)"""
        if not host:
            return None
        
        # Padrão: tenant.totem.com ou tenant.painel.com
        parts = host.split('.')
        if len(parts) >= 3:
            return parts[0]
        
        return None
```

### **Solução 3: Identificação por QR Code/Configuração**

#### **3.1 QR Code de Configuração**

```python
# apps/api/routers/equipment.py
@router.post("/setup/qr")
async def generate_setup_qr(tenant_id: str):
    """Gera QR code para configuração do equipamento"""
    
    setup_data = {
        "tenant_id": tenant_id,
        "api_url": settings.API_BASE_URL,
        "timestamp": datetime.utcnow().isoformat(),
        "signature": generate_signature(tenant_id)
    }
    
    qr_code = qrcode.make(json.dumps(setup_data))
    
    return {
        "qr_code": qr_code,
        "setup_url": f"{settings.API_BASE_URL}/setup/{tenant_id}"
    }

@router.get("/setup/{tenant_id}")
async def equipment_setup_page(tenant_id: str):
    """Página de configuração do equipamento"""
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant não encontrado")
    
    return {
        "tenant": tenant,
        "setup_instructions": "Configure seu equipamento com os dados abaixo"
    }
```

#### **3.2 Frontend - Leitura do QR Code**

```typescript
// apps/totem-client/src/services/qrSetup.ts
export class QRSetupService {
    async scanSetupQR(): Promise<TenantConfig> {
        // Usar biblioteca de QR code
        const qrData = await this.scanQRCode();
        
        const setupData = JSON.parse(qrData);
        
        // Validar assinatura
        if (!this.validateSignature(setupData)) {
            throw new Error('QR Code inválido');
        }
        
        // Salvar configuração
        localStorage.setItem('tenant_config', JSON.stringify(setupData));
        
        return setupData;
    }
    
    private validateSignature(data: any): boolean {
        // Implementar validação de assinatura
        return true;
    }
}
```

### **Solução 4: Identificação por JWT Token (Painel)**

#### **4.1 JWT Multi-Tenant**

```python
# apps/api/auth/multi_tenant_jwt.py
class MultiTenantJWT:
    def create_token(self, user_id: str, tenant_id: str, role: str) -> str:
        """Cria token JWT incluindo tenant_id"""
        payload = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    
    def verify_token(self, token: str) -> dict:
        """Verifica token e retorna payload com tenant_id"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido")

# Dependency para extrair tenant do JWT
async def get_current_tenant_from_jwt(
    token: str = Depends(HTTPBearer())
) -> str:
    jwt_handler = MultiTenantJWT()
    payload = jwt_handler.verify_token(token.credentials)
    return payload.get("tenant_id")
```

---

## 🔧 **Implementação Recomendada**

### **Fase 1: Identificação por Hardware**

```python
# apps/api/routers/equipment.py
@router.post("/identify")
async def identify_equipment(
    request: EquipmentIdentificationRequest,
    db: Session = Depends(get_db)
):
    """Identifica equipamento e retorna tenant_id"""
    
    # Buscar equipamento pelo MAC
    equipment = db.query(Equipment).filter(
        Equipment.mac_address == request.mac_address
    ).first()
    
    if equipment:
        return {
            "tenant_id": str(equipment.tenant_id),
            "equipment_id": str(equipment.id),
            "equipment_type": equipment.type
        }
    
    # Se não encontrado, criar novo equipamento (modo setup)
    if request.setup_mode:
        # Criar equipamento com tenant padrão ou permitir seleção
        equipment = Equipment(
            mac_address=request.mac_address,
            tenant_id=request.tenant_id,
            type=request.equipment_type,
            identifier=f"{request.equipment_type}_{request.mac_address[-6:]}"
        )
        
        db.add(equipment)
        db.commit()
        
        return {
            "tenant_id": str(equipment.tenant_id),
            "equipment_id": str(equipment.id),
            "equipment_type": equipment.type,
            "setup_complete": True
        }
    
    raise HTTPException(status_code=404, detail="Equipamento não encontrado")
```

### **Fase 2: Frontend Automático**

```typescript
// apps/totem-client/src/services/tenantIdentification.ts
export class TenantIdentificationService {
    private tenantId: string | null = null;
    
    async identifyTenant(): Promise<string> {
        // 1. Tentar carregar de localStorage
        const savedTenant = localStorage.getItem('tenant_id');
        if (savedTenant) {
            this.tenantId = savedTenant;
            return savedTenant;
        }
        
        // 2. Identificar automaticamente
        const equipmentId = await this.getEquipmentId();
        const response = await fetch('/api/equipment/identify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mac_address: equipmentId,
                equipment_type: 'totem',
                setup_mode: true
            })
        });
        
        const data = await response.json();
        
        // 3. Salvar para uso futuro
        localStorage.setItem('tenant_id', data.tenant_id);
        this.tenantId = data.tenant_id;
        
        return data.tenant_id;
    }
    
    private async getEquipmentId(): Promise<string> {
        // Implementar detecção de MAC address
        // ou usar outras características do equipamento
        return 'mock-mac-address';
    }
}
```

### **Fase 3: Painel com JWT Multi-Tenant**

```typescript
// apps/panel-client/src/services/auth.ts
export class MultiTenantAuthService {
    async login(email: string, password: string, tenantId: string): Promise<string> {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                password,
                tenant_id: tenantId
            })
        });
        
        const data = await response.json();
        
        // Token já contém tenant_id
        localStorage.setItem('token', data.access_token);
        
        return data.access_token;
    }
    
    getCurrentTenant(): string | null {
        const token = localStorage.getItem('token');
        if (!token) return null;
        
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.tenant_id;
        } catch {
            return null;
        }
    }
}
```

---

## 🎯 **Fluxo de Funcionamento**

### **Totem (Automático):**

1. **Inicialização:**
   ```
   Totem liga → Detecta MAC → API identifica → Retorna tenant_id → Salva localmente
   ```

2. **Comunicação:**
   ```
   Totem → WebSocket com tenant_id → Backend filtra por tenant → Painel recebe apenas dados do seu tenant
   ```

### **Painel (Manual + JWT):**

1. **Login:**
   ```
   Operador faz login → JWT contém tenant_id → Todas as requisições incluem tenant
   ```

2. **Comunicação:**
   ```
   Painel → JWT com tenant_id → Backend valida → WebSocket isolado por tenant
   ```

---

## 📋 **Benefícios da Solução**

### **1. Automatização**
- Totem identifica tenant automaticamente
- Zero configuração manual
- Setup único por equipamento

### **2. Segurança**
- Isolamento completo por tenant
- Validação de equipamento
- JWT com tenant_id

### **3. Flexibilidade**
- Suporte a múltiplos tenants
- Configuração dinâmica
- Migração fácil entre tenants

### **4. Escalabilidade**
- Novos equipamentos se auto-configuram
- Painel suporta múltiplos tenants
- Infraestrutura compartilhada

---

## 🚀 **Próximos Passos**

1. **Implementar identificação por hardware** (Sprint 1)
2. **Criar sistema de setup automático** (Sprint 2)
3. **Implementar JWT multi-tenant** (Sprint 3)
4. **Testar isolamento completo** (Sprint 4)

---

*Esta solução resolve o problema de comunicação entre totem e painel, garantindo isolamento completo por tenant.* 