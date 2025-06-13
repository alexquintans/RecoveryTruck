from sqlalchemy import Column, String, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from uuid import uuid4

from database import Base

class Tenant(Base):
    """Modelo para tenants (clientes)."""
    
    __tablename__ = "tenants"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    cnpj = Column(String(14), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Configurações de pagamento
    payment_adapter = Column(String(50), default="sicredi")  # "sicredi", "stone", etc.
    payment_config = Column(JSON, default=dict)  # Configurações específicas do adquirente
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 