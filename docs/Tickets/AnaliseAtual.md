## 📋 **Entendimento do Contexto**

### **🎯 Fluxo Principal:**
1. **Totem** → Cria **1 Ticket** (não alterar)
2. **Painel do Operador** → Recebe o Ticket e **subdivide em múltiplos tickets** por serviço
3. **Gerenciamento de Ticket ativado** → Ticket vai para "aguardando pagamento"
4. **Pagamento confirmado** → Ticket se subdivide em **N tickets** (um por serviço)
5. **Cada subticket** → Vai para a fila do respectivo serviço
6. **Chamada independente** → Cada serviço é chamado independentemente

### **🔑 Pontos Críticos:**
- **1 Ticket do Totem** → **N Tickets no Painel** (mesma senha, mesmos dados)
- **Chamada independente** → Se cliente tem 3 serviços, chama 1 por vez
- **Outros serviços ficam na fila** → Estáticos até serem chamados

## ✅ **O que Já Temos Implementado**

### **1. Estrutura de Dados:**
```python
# ✅ JÁ EXISTE: Modelo para múltiplos serviços
class TicketService(Base):
    ticket_id = Column(UUID, ForeignKey("tickets.id"))
    service_id = Column(UUID, ForeignKey("services.id"))
    price = Column(Numeric(10,2))

# ✅ JÁ EXISTE: Progresso individual por serviço
class TicketServiceProgress(Base):
    ticket_service_id = Column(UUID, ForeignKey("ticket_services.id"))
    status = Column(String(20))  # pending, in_progress, completed, cancelled
```

### **2. Endpoints de Chamada Individual:**
```python
# ✅ JÁ EXISTE: Chamada por serviço específico
@router.post("/{ticket_id}/call-intelligent")
async def call_ticket_intelligent(
    ticket_id: str,
    service_id: str,  # ✅ Serviço específico
    equipment_id: str
)

# ✅ JÁ EXISTE: Verificação de conflitos por serviço
@router.get("/{ticket_id}/check-conflicts")
async def check_ticket_conflicts(
    ticket_id: str,
    service_id: str  # ✅ Serviço específico
)
```

### **3. Frontend Preparado:**
```typescript
// ✅ JÁ EXISTE: Chamada por serviço
const handleCallTicket = async (ticket: Ticket, serviceId: string) => {
  await callIntelligent({
    ticketId: ticket.id,
    serviceId: serviceId,  // ✅ Serviço específico
    equipmentId: selectedEquipment
  });
}
```

## ❌ **O que Precisa Ser Ajustado**

### **1. Subdivisão de Tickets (CRÍTICO)**
**Problema**: Não temos lógica para subdividir 1 ticket em N tickets por serviço
**Por que**: O fluxo atual mantém 1 ticket com múltiplos serviços, mas precisamos de tickets independentes

### **2. Filtro de "Meus Tickets" (CRÍTICO)**
**Problema**: Endpoint `my-tickets` não filtra corretamente tickets por serviço
**Por que**: Está buscando tickets globais em vez de tickets com serviços específicos em andamento

### **3. Estrutura de Dados (IMPORTANTE)**
**Problema**: Frontend espera `serviceProgress` mas backend não fornece
**Por que**: Modelo `TicketServiceWithDetails` não inclui informações de progresso

## 🛠️ **Soluções Sustentáveis**

### **Solução 1: Subdivisão de Tickets (CRÍTICO)**

#### **Opção A: Criar Tickets Virtuais (RECOMENDADA)**
```python
# ✅ NOVO: Endpoint para subdividir ticket após pagamento
@router.post("/{ticket_id}/subdivide-after-payment")
async def subdivide_ticket_after_payment(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    """Subdivide 1 ticket em N tickets virtuais por serviço"""
    
    # Buscar ticket original
    original_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    # Buscar serviços do ticket
    ticket_services = db.query(TicketService).filter(
        TicketService.ticket_id == ticket_id
    ).all()
    
    # Criar tickets virtuais (não persistir no DB, apenas para UI)
    virtual_tickets = []
    for ts in ticket_services:
        virtual_ticket = {
            "id": f"{original_ticket.id}-{ts.service_id}",  # ID virtual
            "ticket_number": original_ticket.ticket_number,
            "customer_name": original_ticket.customer_name,
            "service_id": ts.service_id,
            "service_name": ts.service.name,
            "status": "in_queue",
            "original_ticket_id": original_ticket.id
        }
        virtual_tickets.append(virtual_ticket)
    
    return {"virtual_tickets": virtual_tickets}
```

#### **Opção B: Modificar Estrutura Existente (ALTERNATIVA)**
```python
# ✅ MODIFICAR: Endpoint my-tickets para tratar serviços como tickets virtuais
@router.get("/my-tickets")
async def get_my_tickets(
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    # Buscar tickets com serviços
    tickets = db.query(Ticket).filter(
        Ticket.tenant_id == current_operator.tenant_id,
        Ticket.status.in_(['called', 'in_progress'])
    ).all()
    
    # Converter serviços em "tickets virtuais"
    virtual_tickets = []
    for ticket in tickets:
        for ts in ticket.services:
            virtual_ticket = {
                "id": f"{ticket.id}-{ts.service_id}",
                "ticket_number": ticket.ticket_number,
                "customer_name": ticket.customer_name,
                "service_id": ts.service_id,
                "service_name": ts.service.name,
                "status": get_service_status(ts.id),  # Função para buscar status do serviço
                "original_ticket_id": ticket.id
            }
            virtual_tickets.append(virtual_ticket)
    
    return virtual_tickets
```

### **Solução 2: Filtro Correto de "Meus Tickets"**

```python
# ✅ CORREÇÃO: Filtrar por serviços em andamento
@router.get("/my-tickets")
async def get_my_tickets(
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    # Buscar tickets que têm serviços em andamento
    tickets_with_active_services = db.query(Ticket).join(TicketService).join(TicketServiceProgress).filter(
        Ticket.tenant_id == current_operator.tenant_id,
        TicketServiceProgress.status == "in_progress"
    ).distinct().all()
    
    # Converter para formato esperado pelo frontend
    result = []
    for ticket in tickets_with_active_services:
        # Buscar apenas serviços em andamento
        active_services = db.query(TicketService).join(TicketServiceProgress).filter(
            TicketService.ticket_id == ticket.id,
            TicketServiceProgress.status == "in_progress"
        ).all()
        
        # Criar ticket com apenas serviços ativos
        ticket_data = {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_name": ticket.customer_name,
            "status": "in_progress",
            "services": [format_service_for_frontend(ts) for ts in active_services]
        }
        result.append(ticket_data)
    
    return result
```

### **Solução 3: Estrutura de Dados Completa**

```python
# ✅ NOVO: Modelo com progresso
class TicketServiceWithProgress(BaseModel):
    price: float
    service: ServiceForTicket
    progress: Optional[TicketServiceProgressOut] = None
    status: str  # pending, in_progress, completed, cancelled

# ✅ MODIFICAR: TicketForPanel
class TicketForPanel(Ticket):
    services: List[TicketServiceWithProgress] = []
    extras: List[TicketExtraWithDetails] = []
```

## 🎯 **Plano de Implementação**

### **Fase 1: Subdivisão de Tickets (CRÍTICO)**
1. Implementar endpoint de subdivisão após pagamento
2. Modificar endpoint `my-tickets` para tratar serviços como tickets virtuais
3. Testar fluxo completo

### **Fase 2: Chamada Independente (CRÍTICO)**
1. Verificar se endpoints `call-intelligent` e `check-conflicts` estão funcionando
2. Testar chamada de serviços individuais
3. Confirmar que outros serviços permanecem na fila

### **Fase 3: Estrutura de Dados (IMPORTANTE)**
1. Adicionar progresso ao modelo `TicketServiceWithDetails`
2. Atualizar frontend para usar nova estrutura
3. Testar exibição correta dos estados

### **Fase 4: Testes e Refinamentos**
1. Testar fluxo completo: Totem → Pagamento → Subdivisão → Chamada Independente
2. Verificar que tickets permanecem independentes
3. Confirmar que filas funcionam corretamente

## 🚀 **Próximo Passo Recomendado**

**Implementar a Solução 1 - Opção A (Tickets Virtuais)** porque:
- ✅ Mantém compatibilidade com estrutura atual
- ✅ Permite independência total dos serviços
- ✅ Não requer mudanças no banco de dados
- ✅ Facilita implementação gradual

Quer que eu implemente essa solução? 🎯