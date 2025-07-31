from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, JSON, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
import datetime

from database import Base

# --------------------------------------------------------
# Enums auxiliares
# --------------------------------------------------------

class EquipmentType(enum.Enum):
    totem = "totem"
    panel = "panel"
    printer = "printer"

class EquipmentStatus(enum.Enum):
    online = "online"
    offline = "offline"
    maintenance = "maintenance"

# --------------------------------------------------------
# Novos modelos
# --------------------------------------------------------

class Receipt(Base):
    """Recibo emitido após conclusão (ou tentativa) de pagamento"""
    __tablename__ = "receipts"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_session_id = Column(UUID(as_uuid=True), ForeignKey("payment_sessions.id"), nullable=False, unique=True)
    content = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    payment_session = relationship("PaymentSession", back_populates="receipt")

class Equipment(Base):
    __tablename__ = "equipments"
    __table_args__ = {'extend_existing': True}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"))  # Equipamento relativo a um serviço
    type = Column(SQLEnum(EquipmentType, name="equipment_type"), nullable=False)
    identifier = Column(String(100), nullable=False, unique=True)
    location = Column(String(255))
    status = Column(SQLEnum(EquipmentStatus, name="equipment_status"), nullable=False, default=EquipmentStatus.online)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"))

    # Relationships
    tenant = relationship("Tenant", back_populates="equipments")
    assigned_operator = relationship("Operator", foreign_keys=[assigned_operator_id])
    service = relationship("Service", back_populates="equipments")

class ConfigNotification(Base):
    __tablename__ = "config_notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    slack_webhook = Column(Text)
    email_from = Column(String(255))
    smtp_host = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ConfigWebhook(Base):
    __tablename__ = "config_webhooks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    target_url = Column(Text, nullable=False)
    secret = Column(String(255))
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"))
    action = Column(String(50), nullable=False)
    entity = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    data_json = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --------------------------------------------------------
# Relacionamentos adicionais
# --------------------------------------------------------

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    cnpj = Column(String(14), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    services = relationship("Service", back_populates="tenant")
    tickets = relationship("Ticket", back_populates="tenant")
    operators = relationship("Operator", back_populates="tenant")
    payment_sessions = relationship("PaymentSession", back_populates="tenant")
    equipments = relationship("Equipment", back_populates="tenant", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    equipment_count = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="services")
    tickets_assoc = relationship("TicketService", back_populates="service", cascade="all, delete-orphan")
    payment_sessions = relationship("PaymentSession", back_populates="service")
    equipments = relationship("Equipment", back_populates="service", cascade="all, delete-orphan")

class PaymentSession(Base):
    """Sessão de pagamento criada quando cliente escolhe serviço, antes do pagamento ser confirmado"""
    __tablename__ = "payment_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=True)  # Adicionado
    customer_name = Column(String(100), nullable=False)
    customer_cpf = Column(String(14), nullable=True)  # Aceita CPF formatado (11 dígitos + formatação)
    customer_phone = Column(String(20), nullable=True)
    consent_version = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, paid, failed, expired
    payment_method = Column(String(20), nullable=False)  # credit, debit, pix, tap
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_id = Column(String(100), nullable=True)  # Preenchido após criar pagamento
    payment_link = Column(Text, nullable=True)
    webhook_data = Column(JSONB)
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Sessão expira em 30 min
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    tenant = relationship("Tenant", back_populates="payment_sessions")
    service = relationship("Service", back_populates="payment_sessions")
    ticket = relationship("Ticket", foreign_keys=[ticket_id])  # Removido back_populates
    consent = relationship("Consent", back_populates="payment_session", uselist=False)
    receipt = relationship("Receipt", back_populates="payment_session", uselist=False)

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    payment_session_id = Column(UUID(as_uuid=True), ForeignKey("payment_sessions.id"), nullable=False)
    ticket_number = Column(Integer, nullable=False)
    
    # Estados: paid -> printing -> in_queue -> called -> in_progress -> completed
    # Alternativos: print_error, cancelled, expired
    status = Column(String(20), nullable=False, default="paid")
    
    # Dados do cliente
    customer_name = Column(String(100), nullable=False)
    customer_cpf = Column(String(14), nullable=True)  # Aceita CPF formatado (11 dígitos + formatação)
    customer_phone = Column(String(20), nullable=True)
    consent_version = Column(String(10), nullable=False)
    
    # Sistema de fila e priorização
    priority = Column(String(10), nullable=False, default="normal")  # high, normal, low
    queue_position = Column(Integer)                                 # Posição na fila
    estimated_wait_minutes = Column(Integer)                         # Tempo estimado de espera
    assigned_operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"))  # Operador atribuído
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipments.id"), nullable=True)  # Equipamento atribuído
    
    # Timestamps do ciclo de vida
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    printed_at = Column(DateTime(timezone=True))           # Quando foi impresso
    queued_at = Column(DateTime(timezone=True))            # Quando entrou na fila (in_queue)
    called_at = Column(DateTime(timezone=True))            # Quando foi chamado
    started_at = Column(DateTime(timezone=True))           # Quando iniciou atendimento
    completed_at = Column(DateTime(timezone=True))         # Quando foi concluído
    cancelled_at = Column(DateTime(timezone=True))         # Quando foi cancelado
    expired_at = Column(DateTime(timezone=True))           # Quando expirou
    reprinted_at = Column(DateTime(timezone=True))         # Última reimpressão
    
    # Metadados adicionais
    operator_notes = Column(Text)                          # Observações do operador
    cancellation_reason = Column(String(255))              # Motivo do cancelamento
    print_attempts = Column(Integer, default=0)            # Tentativas de impressão
    reactivation_count = Column(Integer, default=0)        # Quantas vezes foi reativado

    # Novo: indica se o pagamento foi confirmado manualmente (uso de maquininha física)
    payment_confirmed = Column(Boolean, default=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="tickets")
    services = relationship("TicketService", back_populates="ticket", cascade="all, delete-orphan")
    payment_session = relationship("PaymentSession", foreign_keys=[payment_session_id])
    assigned_operator = relationship("Operator", foreign_keys=[assigned_operator_id])
    equipment = relationship("Equipment", foreign_keys=[equipment_id])
    extras = relationship("TicketExtra", back_populates="ticket", cascade="all, delete-orphan")

class Operator(Base):
    __tablename__ = "operators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="operators")

class Consent(Base):
    __tablename__ = "consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    payment_session_id = Column(UUID(as_uuid=True), ForeignKey("payment_sessions.id"), nullable=False)
    version = Column(String(10), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    signature = Column(Text, nullable=True)  # Assinatura base64

    # Relationships
    tenant = relationship("Tenant")
    payment_session = relationship("PaymentSession", back_populates="consent")

class OperatorSession(Base):
    __tablename__ = "operator_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipments.id"))
    config_json = Column(JSONB)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))

    operator = relationship("Operator")
    tenant = relationship("Tenant")
    equipment = relationship("Equipment")

class Extra(Base):
    __tablename__ = "extras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10,2), nullable=False)
    category = Column(String(50))
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant") 

# ====== MODELS DE OPERATION_CONFIG (migrados do operation_config.py) ======

class OperationConfig(Base):
    __tablename__ = 'operation_config'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False)
    operator_id = Column(UUID(as_uuid=True), ForeignKey('operators.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Lista de métodos de pagamento habilitados para a operação (none, mercadopago, sicredi, etc.)
    payment_modes = Column(JSONB, default=list)  # Armazenado como array JSON
    
    # Configurações de pagamento (Mercado Pago, etc.)
    payment_config = Column(JSONB, nullable=True)  # Adicionado

    equipments = relationship('OperationConfigEquipment', back_populates='operation_config', cascade="all, delete-orphan")
    extras = relationship('OperationConfigExtra', back_populates='operation_config', cascade="all, delete-orphan")

class OperationConfigEquipment(Base):
    __tablename__ = 'operation_config_equipments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_config_id = Column(UUID(as_uuid=True), ForeignKey('operation_config.id'), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipments.id'), nullable=False)
    active = Column(Boolean, default=True)
    quantity = Column(Integer, nullable=False)

    operation_config = relationship('OperationConfig', back_populates='equipments')
    equipment = relationship('Equipment')

class OperationConfigExtra(Base):
    __tablename__ = 'operation_config_extras'
    id = Column(Integer, primary_key=True, autoincrement=True)
    operation_config_id = Column(UUID(as_uuid=True), ForeignKey('operation_config.id'), nullable=False)
    extra_id = Column(UUID(as_uuid=True), ForeignKey('extras.id'), nullable=False)
    active = Column(Boolean, default=True)
    stock = Column(Integer, nullable=False)
    price = Column(Numeric(10,2), nullable=False)

    operation_config = relationship('OperationConfig', back_populates='extras')
    extra = relationship('Extra') 

class TicketExtra(Base):
    __tablename__ = "ticket_extras"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    extra_id = Column(UUID(as_uuid=True), ForeignKey("extras.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Numeric(10,2), nullable=False)

    ticket = relationship("Ticket", back_populates="extras")
    extra = relationship("Extra") 

class OperationStatusModel(Base):
    __tablename__ = "operation_status"
    id = Column(Integer, primary_key=True)
    is_operating = Column(Boolean, default=False)
    service_duration = Column(Integer, default=10)
    equipment_counts = Column(JSONB, default={})
    operator_id = Column(UUID(as_uuid=True), nullable=True)
    operator_name = Column(String(100), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False) 

# NOVO: Modelo associativo entre Ticket e Service
class TicketService(Base):
    __tablename__ = "ticket_services"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    # outros campos relevantes podem ser adicionados aqui

    ticket = relationship("Ticket", back_populates="services")
    service = relationship("Service", back_populates="tickets_assoc") 