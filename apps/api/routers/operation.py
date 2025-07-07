from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from database import get_db
from auth import get_current_operator
import threading
from models import Equipment, Service, Extra, OperationConfig, OperationConfigEquipment, OperationConfigExtra, OperationStatusModel
from uuid import UUID
from fastapi import Request

router = APIRouter(
    tags=["operation"],
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
    duration: int
    price: float
    equipment_count: int

class EquipmentConfigIn(BaseModel):
    equipment_id: UUID
    active: bool
    quantity: int

class ExtraConfigIn(BaseModel):
    extra_id: UUID
    active: bool
    stock: int
    price: float

class OperationConfigIn(BaseModel):
    tenant_id: UUID
    operator_id: UUID
    services: list[ServiceConfigIn]
    equipments: list[EquipmentConfigIn]
    extras: list[ExtraConfigIn]

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
        joinedload(OperationConfig.services).joinedload(Service.service),
        joinedload(OperationConfig.equipments).joinedload(OperationConfigEquipment.equipment),
        joinedload(OperationConfig.extras).joinedload(OperationConfigExtra.extra),
    ).filter(OperationConfig.tenant_id == tenant_id).order_by(OperationConfig.created_at.desc()).first()
    if not op_cfg:
        return {"message": "Nenhuma configuração encontrada"}
    return {
        "id": str(op_cfg.id),
        "tenant_id": str(op_cfg.tenant_id),
        "operator_id": str(op_cfg.operator_id),
        "created_at": op_cfg.created_at.isoformat(),
        "updated_at": op_cfg.updated_at.isoformat(),
        "services": [
            {
                "service_id": str(s.service_id),
                "active": s.active,
                "duration": s.duration,
                "price": float(s.price),
                "equipment_count": getattr(s, 'equipment_count', None),
                "name": s.service.name if s.service else None,
                "description": s.service.description if s.service else None,
            } for s in op_cfg.services
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
                "extra_id": str(x.extra_id),
                "active": x.active,
                "stock": x.stock,
                "price": float(x.price),
                "name": x.extra.name if x.extra else None,
                "description": x.extra.description if x.extra else None,
            } for x in op_cfg.extras
        ]
    } 