from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

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

class TicketBase(BaseModel):
    service_id: UUID
    customer_name: str = Field(..., min_length=3, max_length=100)
    customer_cpf: str = Field(..., min_length=11, max_length=11)
    customer_phone: str = Field(..., min_length=10, max_length=20)
    consent_version: str = Field(..., min_length=1, max_length=10)

class PaymentBase(BaseModel):
    ticket_id: UUID
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., regex="^(credit|debit|pix|tap)$")

class OperatorBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    is_active: bool = True

class ConsentBase(BaseModel):
    ticket_id: UUID
    version: str = Field(..., min_length=1, max_length=10)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# Create schemas
class TenantCreate(TenantBase):
    pass

class ServiceCreate(ServiceBase):
    pass

class TicketCreate(TicketBase):
    pass

class PaymentCreate(PaymentBase):
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

class Ticket(TicketBase):
    id: UUID
    tenant_id: UUID
    ticket_number: int
    status: str
    created_at: datetime
    updated_at: datetime
    called_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Payment(PaymentBase):
    id: UUID
    tenant_id: UUID
    transaction_id: str
    status: str
    payment_link: Optional[str] = None
    webhook_data: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

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

class TicketList(BaseModel):
    items: List[Ticket]
    total: int

class PaymentList(BaseModel):
    items: List[Payment]
    total: int

class OperatorList(BaseModel):
    items: List[Operator]
    total: int

class ConsentList(BaseModel):
    items: List[Consent]
    total: int 