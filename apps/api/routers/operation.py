from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from database import get_db
from auth import get_current_operator
import threading
from models import Equipment, Service, Extra, OperationConfig, OperationConfigEquipment, OperationConfigExtra, OperationStatusModel
from uuid import UUID
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["operation"]
)

# Estado global da operação (thread-safe)
class OperationStatus(BaseModel):
    is_operating: bool = False
    service_duration: int = 10
    equipment_counts: dict = {}
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    config: dict = {}
    updated_at: Optional[str] = None

operation_status = OperationStatus()
operation_lock = threading.Lock()

class OperationStartRequest(BaseModel):
    service_duration: int
    equipment_counts: dict
    operator_id: str
    operator_name: str
    config: dict

class ServiceConfigIn(BaseModel):
    service_id: UUID
    active: bool
    duration: Optional[int] = 10  # Valor padrão de 10 minutos
    price: Optional[float] = 0.0  # Valor padrão de 0.0
    equipment_count: int
    
    @validator('service_id', pre=True)
    def validate_service_id(cls, v):
        if isinstance(v, str):
            return UUID(v)
        return v

class EquipmentConfigIn(BaseModel):
    equipment_id: UUID
    active: bool
    quantity: int
    
    @validator('equipment_id', pre=True)
    def validate_equipment_id(cls, v):
        if isinstance(v, str):
            return UUID(v)
        return v

class ExtraConfigIn(BaseModel):
    extra_id: UUID
    active: bool
    stock: Optional[int] = 0  # Valor padrão de 0
    price: Optional[float] = 0.0  # Valor padrão de 0.0
    
    @validator('extra_id', pre=True)
    def validate_extra_id(cls, v):
        if isinstance(v, str):
            return UUID(v)
        return v

# Novo enum/string simples para modos de pagamento
PaymentMode = str  # 'none' | 'mercadopago' | 'sicredi' — manter flexível

class OperationConfigIn(BaseModel):
    tenant_id: UUID
    operator_id: Optional[UUID] = None  # Tornar opcional
    services: list[ServiceConfigIn]
    equipments: list[EquipmentConfigIn]
    extras: list[ExtraConfigIn]
    payment_modes: Optional[List[PaymentMode]] = None
    payment_config: Optional[dict] = None
    
    @validator('tenant_id', pre=True)
    def validate_tenant_id(cls, v):
        if isinstance(v, str):
            return UUID(v)
        return v
    
    @validator('operator_id', pre=True)
    def validate_operator_id(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return UUID(v)
        return v

@router.get("", summary="Informações da operação atual")
async def get_operation_info(request: Request, db: Session = Depends(get_db)):
    """Retorna informações reais da operação (persistente)."""
    tenant_id = request.query_params.get('tenant_id')
    if not tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id é obrigatório")
    status_obj = db.query(OperationStatusModel).filter(OperationStatusModel.tenant_id == tenant_id).first()
    if not status_obj:
        return {"is_operating": False, "service_duration": 10, "equipment_counts": {}}
    return {
        "is_operating": status_obj.is_operating,
        "service_duration": status_obj.service_duration,
        "equipment_counts": status_obj.equipment_counts,
        "operator_id": str(status_obj.operator_id) if status_obj.operator_id else None,
        "operator_name": status_obj.operator_name,
        "started_at": status_obj.started_at.isoformat() if status_obj.started_at else None,
        "ended_at": status_obj.ended_at.isoformat() if status_obj.ended_at else None,
        "updated_at": status_obj.updated_at.isoformat() if status_obj.updated_at else None,
    }

@router.post("/start", summary="Inicia uma operação")
async def start_operation(req: OperationStartRequest, db: Session = Depends(get_db)):
    """Inicia uma nova operação, persistindo status no banco."""
    tenant_id = req.config.get('tenant_id')
    if not tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id é obrigatório na config")
    status_obj = db.query(OperationStatusModel).filter(OperationStatusModel.tenant_id == tenant_id).first()
    now = datetime.utcnow()
    if not status_obj:
        status_obj = OperationStatusModel(
            tenant_id=tenant_id,
            is_operating=True,
            service_duration=req.service_duration,
            equipment_counts=req.equipment_counts,
            operator_id=req.operator_id,
            operator_name=req.operator_name,
            started_at=now,
            ended_at=None,
            updated_at=now,
        )
        db.add(status_obj)
    else:
        if status_obj.is_operating:
            raise HTTPException(status_code=400, detail="Já existe uma operação ativa.")
        status_obj.is_operating = True
        status_obj.service_duration = req.service_duration
        status_obj.equipment_counts = req.equipment_counts
        status_obj.operator_id = req.operator_id
        status_obj.operator_name = req.operator_name
        status_obj.started_at = now
        status_obj.ended_at = None
        status_obj.updated_at = now
    db.commit()
    return {"message": "Operação iniciada com sucesso", "status": {
        "is_operating": status_obj.is_operating,
        "service_duration": status_obj.service_duration,
        "equipment_counts": status_obj.equipment_counts,
        "operator_id": str(status_obj.operator_id) if status_obj.operator_id else None,
        "operator_name": status_obj.operator_name,
        "started_at": status_obj.started_at.isoformat() if status_obj.started_at else None,
        "ended_at": status_obj.ended_at.isoformat() if status_obj.ended_at else None,
        "updated_at": status_obj.updated_at.isoformat() if status_obj.updated_at else None,
    }}

@router.post("/stop", summary="Encerra a operação atual")
async def stop_operation(request: Request, db: Session = Depends(get_db)):
    """Encerra a operação atual (persistente)."""
    tenant_id = request.query_params.get('tenant_id')
    if not tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id é obrigatório")
    status_obj = db.query(OperationStatusModel).filter(OperationStatusModel.tenant_id == tenant_id).first()
    now = datetime.utcnow()
    if not status_obj or not status_obj.is_operating:
            raise HTTPException(status_code=400, detail="Nenhuma operação ativa para encerrar.")
    status_obj.is_operating = False
    status_obj.ended_at = now
    status_obj.updated_at = now
    db.commit()
    return {"message": "Operação encerrada com sucesso", "status": {
        "is_operating": status_obj.is_operating,
        "service_duration": status_obj.service_duration,
        "equipment_counts": status_obj.equipment_counts,
        "operator_id": str(status_obj.operator_id) if status_obj.operator_id else None,
        "operator_name": status_obj.operator_name,
        "started_at": status_obj.started_at.isoformat() if status_obj.started_at else None,
        "ended_at": status_obj.ended_at.isoformat() if status_obj.ended_at else None,
        "updated_at": status_obj.updated_at.isoformat() if status_obj.updated_at else None,
    }}

@router.get("/equipment", summary="Lista de equipamentos")
async def list_equipment(
    db: Session = Depends(get_db),
    current_operator=Depends(get_current_operator)
):
    """Lista os equipamentos cadastrados no banco."""
    equipment = db.query(Equipment).all()
    return [
        {
            "id": str(eq.id),
            "name": eq.identifier,
            "type": eq.type,
            "status": eq.status,
            "location": eq.location,
        } for eq in equipment
    ]

@router.post("/config", summary="Salva configuração vigente da operação")
async def save_operation_config(
    cfg: OperationConfigIn,
    db: Session = Depends(get_db)
):
    # Remove configurações antigas garantindo cascata correta
    old_cfgs = db.query(OperationConfig).filter(OperationConfig.tenant_id == cfg.tenant_id).all()
    for oc in old_cfgs:
        db.delete(oc)
    db.commit()
    op_cfg = OperationConfig(
        tenant_id=cfg.tenant_id,
        operator_id=cfg.operator_id,
        payment_modes=cfg.payment_modes or [],
        payment_config=cfg.payment_config or {},
    )
    db.add(op_cfg)
    db.commit()
    db.refresh(op_cfg)

    # Adicionar equipamentos
    for e in cfg.equipments:
        eq = OperationConfigEquipment(
            operation_config_id=op_cfg.id,
            equipment_id=e.equipment_id,
            active=e.active,
            quantity=e.quantity,
        )
        db.add(eq)

    # Adicionar extras
    for x in cfg.extras:
        # Buscar o extra atual para sincronizar o estoque
        current_extra = db.query(Extra).filter(Extra.id == x.extra_id).first()
        if current_extra:
            # Sincronizar o estoque da tabela extras com a configuração
            current_extra.stock = x.stock
            db.add(current_extra)
            logger.info(f"🔍 DEBUG - Sincronizando estoque do extra {current_extra.name}: {x.stock}")
        
        ex = OperationConfigExtra(
            operation_config_id=op_cfg.id,
            extra_id=x.extra_id,
            active=x.active,
            stock=x.stock,
            price=x.price,
        )
        db.add(ex)

    db.commit()

    # --- Atualizar status dos equipamentos ---
    equipment_ids_active = [e.equipment_id for e in cfg.equipments if e.active]
    db.query(Equipment).filter(Equipment.id.in_(equipment_ids_active)).update(
        {Equipment.status: "online"}, synchronize_session=False
    )
    db.query(Equipment).filter(~Equipment.id.in_(equipment_ids_active)).update(
        {Equipment.status: "offline"}, synchronize_session=False
    )

    # --- Atualizar status dos serviços ---
    service_ids_active = [s.service_id for s in cfg.services if s.active]
    db.query(Service).filter(Service.id.in_(service_ids_active)).update(
        {Service.is_active: True}, synchronize_session=False
    )
    db.query(Service).filter(~Service.id.in_(service_ids_active)).update(
        {Service.is_active: False}, synchronize_session=False
    )

    # --- Atualizar status dos extras ---
    extra_ids_active = [x.extra_id for x in cfg.extras if x.active]
    db.query(Extra).filter(Extra.id.in_(extra_ids_active)).update(
        {Extra.is_active: True}, synchronize_session=False
    )
    db.query(Extra).filter(~Extra.id.in_(extra_ids_active)).update(
        {Extra.is_active: False}, synchronize_session=False
    )

    # --- Atualizar ou criar status da operação ---
    status_obj = db.query(OperationStatusModel).filter(OperationStatusModel.tenant_id == cfg.tenant_id).first()
    now = datetime.utcnow()
    if not status_obj:
        status_obj = OperationStatusModel(
            tenant_id=cfg.tenant_id,
            is_operating=True,
            service_duration=cfg.services[0].duration if cfg.services else 10,
            equipment_counts={str(e.equipment_id): e.quantity for e in cfg.equipments},
            operator_id=cfg.operator_id,
            operator_name=None,
            started_at=now,
            ended_at=None,
            updated_at=now,
        )
        db.add(status_obj)
    else:
        status_obj.is_operating = True
        status_obj.service_duration = cfg.services[0].duration if cfg.services else 10
        status_obj.equipment_counts = {str(e.equipment_id): e.quantity for e in cfg.equipments}
        status_obj.operator_id = cfg.operator_id
        status_obj.updated_at = now
        status_obj.ended_at = None
    db.commit()

    return {"message": "Configuração salva com sucesso"}

@router.get("/config", summary="Consulta configuração vigente da operação")
async def get_operation_config(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    op_cfg = db.query(OperationConfig).options(
        joinedload(OperationConfig.equipments).joinedload(OperationConfigEquipment.equipment),
        joinedload(OperationConfig.extras).joinedload(OperationConfigExtra.extra),
    ).filter(OperationConfig.tenant_id == tenant_id).order_by(OperationConfig.created_at.desc()).first()
    if not op_cfg:
        return {"message": "Nenhuma configuração encontrada"}
    
    # Importar configurações do Mercado Pago
    from config.settings import Settings
    settings = Settings()
    
    # Buscar serviços ativos do tenant
    services = db.query(Service).filter(
        Service.tenant_id == tenant_id,
        Service.is_active == True
    ).all()
    
    logger.info(f"🔍 DEBUG - Serviços encontrados: {len(services)}")
    for s in services:
        logger.info(f"🔍 DEBUG - Serviço: {s.id} - {s.name}")
    
    return {
        "id": str(op_cfg.id),
        "tenant_id": str(op_cfg.tenant_id),
        "operator_id": str(op_cfg.operator_id),
        "created_at": op_cfg.created_at.isoformat(),
        "updated_at": op_cfg.updated_at.isoformat(),
        "payment_modes": op_cfg.payment_modes or [],
        "payment_config": {
            "mercado_pago": {
                "access_token": settings.MERCADOPAGO_ACCESS_TOKEN,
                "public_key": settings.MERCADOPAGO_PUBLIC_KEY,
                "webhook_url": settings.MERCADOPAGO_WEBHOOK_URL,
                "redirect_url_base": "http://localhost:5174"
            },
            "mercado_pago_public_key": settings.MERCADOPAGO_PUBLIC_KEY,
        },
        "services": [
            {
                "id": str(s.id),
                "name": s.name,
                "description": s.description,
                "price": float(s.price),
                "duration_minutes": s.duration_minutes,
                "equipment_count": s.equipment_count,
                "is_active": s.is_active,
                "tenant_id": str(s.tenant_id),
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            } for s in services
        ],
        "equipments": [
            {
                "equipment_id": str(e.equipment_id),
                "active": e.active,
                "quantity": e.quantity,
                "name": e.equipment.identifier if e.equipment else None,
                "type": e.equipment.type if e.equipment else None,
            } for e in op_cfg.equipments
        ],
        "extras": [
            {
                "id": str(x.extra_id),  # Adicionando o campo id que o totem espera
                "extra_id": str(x.extra_id),
                "active": x.active,
                "is_active": x.active,  # Adicionando compatibilidade com o frontend
                "stock": x.stock,
                "price": float(x.price),
                "name": x.extra.name if x.extra else f"Extra {x.extra_id}",
                "description": x.extra.description if x.extra else "",
            } for x in op_cfg.extras
        ]
    } 