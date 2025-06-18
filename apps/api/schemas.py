from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from constants import TicketStatus, PaymentSessionStatus, QueuePriority, QueueSortOrder

# Base schemas
class TenantBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    cnpj: str = Field(..., min_length=14, max_length=14)
    is_active: bool = True

class ServiceBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    duration_minutes: int = Field(..., gt=0)
    equipment_count: int = Field(..., gt=0)
    is_active: bool = True

class PaymentSessionBase(BaseModel):
    service_id: UUID
    customer_name: str = Field(..., min_length=3, max_length=100)
    customer_cpf: str = Field(..., min_length=11, max_length=11)
    customer_phone: str = Field(..., min_length=10, max_length=20)
    consent_version: str = Field(..., min_length=1, max_length=10)
    payment_method: str = Field(..., regex="^(credit|debit|pix|tap)$")

class TicketBase(BaseModel):
    # Ticket não é criado diretamente, apenas através de PaymentSession
    pass

class TicketStatusUpdate(BaseModel):
    """Schema para atualização de status do ticket"""
    status: TicketStatus
    operator_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    
    @validator('cancellation_reason')
    def validate_cancellation_reason(cls, v, values):
        if values.get('status') == TicketStatus.CANCELLED and not v:
            raise ValueError('Motivo do cancelamento é obrigatório')
        return v

class QueueSettings(BaseModel):
    """Configurações da fila"""
    sort_order: QueueSortOrder = QueueSortOrder.FIFO
    show_only_service: Optional[UUID] = None
    show_only_priority: Optional[QueuePriority] = None
    include_called: bool = True
    include_in_progress: bool = True

class OperatorBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    is_active: bool = True

class ConsentBase(BaseModel):
    payment_session_id: UUID
    version: str = Field(..., min_length=1, max_length=10)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# Create schemas
class TenantCreate(TenantBase):
    pass

class ServiceCreate(ServiceBase):
    pass

class PaymentSessionCreate(PaymentSessionBase):
    pass

class OperatorCreate(OperatorBase):
    password: str = Field(..., min_length=8)

class ConsentCreate(ConsentBase):
    pass

# Read schemas
class Tenant(TenantBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Service(ServiceBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaymentSession(PaymentSessionBase):
    id: UUID
    tenant_id: UUID
    status: PaymentSessionStatus
    amount: float
    transaction_id: Optional[str] = None
    payment_link: Optional[str] = None
    webhook_data: Optional[dict] = None
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Ticket(BaseModel):
    id: UUID
    tenant_id: UUID
    service_id: UUID
    payment_session_id: UUID
    ticket_number: int
    status: TicketStatus
    customer_name: str
    customer_cpf: str
    customer_phone: str
    consent_version: str
    
    # Sistema de fila e priorização
    priority: QueuePriority
    queue_position: Optional[int] = None
    estimated_wait_minutes: Optional[int] = None
    assigned_operator_id: Optional[UUID] = None
    
    # Timestamps do ciclo de vida
    created_at: datetime
    updated_at: datetime
    printed_at: Optional[datetime] = None
    queued_at: Optional[datetime] = None
    called_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    reprinted_at: Optional[datetime] = None
    
    # Metadados adicionais
    operator_notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    print_attempts: int = 0
    reactivation_count: int = 0

    class Config:
        from_attributes = True

class TicketWithStatus(Ticket):
    """Ticket com informações detalhadas do status"""
    status_info: dict
    valid_transitions: List[str]
    
    @validator('status_info', pre=True, always=True)
    def set_status_info(cls, v, values):
        from constants import get_status_info
        status = values.get('status')
        if status:
            return get_status_info(TicketStatus(status))
        return {}
    
    @validator('valid_transitions', pre=True, always=True)
    def set_valid_transitions(cls, v, values):
        from constants import get_valid_transitions
        status = values.get('status')
        if status:
            return [s.value for s in get_valid_transitions(TicketStatus(status))]
        return []

class TicketInQueue(Ticket):
    """Ticket na fila com informações adicionais"""
    service: Service
    waiting_time_minutes: float
    waiting_status: str  # normal, warning, critical, expired
    priority_info: dict
    estimated_service_time: int
    
    @validator('waiting_time_minutes', pre=True, always=True)
    def calculate_waiting_time(cls, v, values):
        queued_at = values.get('queued_at')
        if queued_at:
            return (datetime.utcnow() - queued_at).total_seconds() / 60
        return 0
    
    @validator('waiting_status', pre=True, always=True)
    def set_waiting_status(cls, v, values):
        from constants import get_waiting_time_status
        waiting_minutes = values.get('waiting_time_minutes', 0)
        return get_waiting_time_status(waiting_minutes)
    
    @validator('priority_info', pre=True, always=True)
    def set_priority_info(cls, v, values):
        from constants import PRIORITY_DESCRIPTIONS, PRIORITY_COLORS
        priority = values.get('priority', 'normal')
        return {
            "level": priority,
            "description": PRIORITY_DESCRIPTIONS.get(QueuePriority(priority), ""),
            "color": PRIORITY_COLORS.get(QueuePriority(priority), "#000000")
        }

class Operator(OperatorBase):
    id: UUID
    tenant_id: UUID
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Consent(ConsentBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# List schemas
class TenantList(BaseModel):
    items: List[Tenant]
    total: int

class ServiceList(BaseModel):
    items: List[Service]
    total: int

class PaymentSessionList(BaseModel):
    items: List[PaymentSession]
    total: int

class TicketList(BaseModel):
    items: List[Ticket]
    total: int

class TicketListWithStatus(BaseModel):
    items: List[TicketWithStatus]
    total: int

class OperatorList(BaseModel):
    items: List[Operator]
    total: int

class ConsentList(BaseModel):
    items: List[Consent]
    total: int

# Response schemas com dados relacionados
class PaymentSessionWithQR(PaymentSession):
    qr_code: Optional[str] = None

class TicketWithService(Ticket):
    service: Service

class TicketQueue(BaseModel):
    items: List[TicketInQueue]
    total: int
    by_service: dict
    by_status: dict
    by_priority: dict
    queue_stats: dict
    estimated_total_time: int 