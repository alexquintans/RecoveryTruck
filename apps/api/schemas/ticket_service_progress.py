from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class TicketServiceProgressBase(BaseModel):
    status: str = Field(..., description="Status do serviço: pending, in_progress, completed, cancelled")
    duration_minutes: int = Field(..., description="Duração em minutos do serviço")
    operator_notes: Optional[str] = Field(None, description="Observações do operador")
    equipment_id: Optional[UUID] = Field(None, description="ID do equipamento usado")

class TicketServiceProgressCreate(TicketServiceProgressBase):
    ticket_service_id: UUID = Field(..., description="ID do ticket_service")

class TicketServiceProgressUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Status do serviço")
    started_at: Optional[datetime] = Field(None, description="Quando o serviço foi iniciado")
    completed_at: Optional[datetime] = Field(None, description="Quando o serviço foi concluído")
    operator_notes: Optional[str] = Field(None, description="Observações do operador")
    equipment_id: Optional[UUID] = Field(None, description="ID do equipamento usado")

class TicketServiceProgressOut(TicketServiceProgressBase):
    id: UUID
    ticket_service_id: UUID
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    equipment_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketServiceProgressWithService(TicketServiceProgressOut):
    service_name: str
    service_price: float
    equipment_name: Optional[str] = None

class TicketServiceProgressList(BaseModel):
    items: list[TicketServiceProgressWithService]
    total: int 