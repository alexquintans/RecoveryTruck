from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from database import get_db
from models import Equipment, OperatorSession, Operator, Tenant, Service, Extra, EquipmentType, EquipmentStatus, OperationConfig, OperationConfigEquipment, OperationConfigExtra
from schemas import (
    Equipment as EquipmentSchema,
    EquipmentAssign,
    OperatorSessionStart,
    OperatorSession as OperatorSessionSchema,
    ServiceUpdate,
    ExtraUpdate,
    Extra as ExtraSchema,
    Service as ServiceSchema,
    ServiceCreate,
    ExtraCreate,
)
from uuid import UUID
from services.websocket import ConnectionManager
import re

router = APIRouter(tags=["operator"])

manager = ConnectionManager()

@router.get("/equipments", response_model=List[EquipmentSchema])
async def list_equipments(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    return db.query(Equipment).filter(Equipment.tenant_id == tenant_id).all()

@router.post("/equipments/assign")
async def assign_equipment(
    payload: EquipmentAssign,
    db: Session = Depends(get_db)
):
    eq = db.query(Equipment).filter(Equipment.id == payload.equipment_id).first()
    if not eq:
        raise HTTPException(404, "Equipment not found")
    if eq.assigned_operator_id:
        raise HTTPException(400, "Equipment already assigned")
    eq.assigned_operator_id = payload.operator_id
    eq.status = "in_use"
    db.commit()
    await manager.broadcast_queue_update(str(eq.tenant_id), {"equipment_id": str(eq.id), "status": eq.status})
    return {"status": "assigned"}

@router.post("/equipments/release")
async def release_equipment(
    payload: EquipmentAssign,
    db: Session = Depends(get_db)
):
    eq = db.query(Equipment).filter(Equipment.id == payload.equipment_id).first()
    if not eq:
        raise HTTPException(404, "Equipment not found")
    eq.assigned_operator_id = None
    eq.status = "online"
    db.commit()
    await manager.broadcast_queue_update(str(eq.tenant_id), {"equipment_id": str(eq.id), "status": eq.status})
    return {"status": "released"}

@router.post("/sessions/start", response_model=OperatorSessionSchema)
async def start_session(
    payload: OperatorSessionStart,
    db: Session = Depends(get_db)
):
    operator = db.query(Operator).filter(Operator.id == payload.operator_id).first()
    if not operator:
        raise HTTPException(404, "Operator not found")
    session = OperatorSession(
        operator_id=payload.operator_id,
        tenant_id=operator.tenant_id,
        equipment_id=payload.equipment_id,
        config_json=payload.config_json or {}
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.post("/sessions/finish")
async def finish_session(
    session_id: UUID,
    db: Session = Depends(get_db)
):
    session = db.query(OperatorSession).filter(OperatorSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    session.finished_at = db.func.now()
    db.commit()
    return {"status": "finished"}

@router.get("/sessions/active", response_model=Optional[OperatorSessionSchema])
async def get_active_session(
    operator_id: UUID,
    db: Session = Depends(get_db)
):
    session = db.query(OperatorSession).filter(
        OperatorSession.operator_id == operator_id,
        OperatorSession.finished_at == None
    ).order_by(OperatorSession.created_at.desc()).first()
    return session

# -------------------- Serviços --------------------

@router.get("/services", response_model=List[ServiceSchema])
async def list_services(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    return db.query(Service).filter(Service.tenant_id == tenant_id).all()

@router.put("/services/{service_id}")
async def update_service(
    service_id: UUID,
    payload: ServiceUpdate,
    db: Session = Depends(get_db)
):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(404, "Service not found")
    data = payload.dict(exclude_unset=True)
    data.pop("tenant_id", None)
    for key, value in data.items():
        setattr(svc, key, value)
    db.commit()
    await manager.broadcast_queue_update(str(svc.tenant_id), {"service_id": str(svc.id), **data})
    return {"status": "updated"}

@router.delete("/services/{service_id}")
async def delete_service(
    service_id: UUID,
    db: Session = Depends(get_db)
):
    svc = db.query(Service).filter(Service.id == service_id).first()
    if not svc:
        raise HTTPException(404, "Service not found")
    tenant_id = svc.tenant_id
    # Equipamentos relacionados serão removidos automaticamente pelo cascade
    db.delete(svc)
    db.commit()
    await manager.broadcast_queue_update(str(tenant_id), {"service_id": str(service_id), "deleted": True})
    return {"status": "deleted"}

@router.post("/services", response_model=ServiceSchema, status_code=201)
async def create_service(
    tenant_id: UUID,
    payload: ServiceCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo serviço para o tenant informado."""
    svc = Service(
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        duration_minutes=payload.duration_minutes,
        equipment_count=getattr(payload, 'equipment_count', 1),
        is_active=payload.is_active,
    )
    db.add(svc)
    db.commit()
    db.refresh(svc)

    # ---------------- Criar equipamentos automáticos ----------------
    slug = re.sub(r'[^a-z0-9]+', '_', payload.name.lower()).strip('_') or 'equip'
    existing = db.query(Equipment).filter(Equipment.tenant_id == tenant_id, Equipment.identifier.like(f"{slug}_%"))
    start_idx = existing.count() + 1
    for i in range(getattr(payload, 'equipment_count', 1)):
        identifier = f"{slug}_{start_idx + i}"
        eq = Equipment(
            tenant_id=tenant_id,
            service_id=svc.id,
            type=EquipmentType.totem,
            identifier=identifier,
            status=EquipmentStatus.online,
        )
        db.add(eq)
    db.commit()

    return svc

# -------------------- Extras --------------------

@router.get("/extras", response_model=List[ExtraSchema])
async def list_extras(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    return db.query(Extra).filter(Extra.tenant_id == tenant_id).all()

@router.put("/extras/{extra_id}")
async def update_extra(
    extra_id: UUID,
    payload: ExtraUpdate,
    db: Session = Depends(get_db)
):
    extra = db.query(Extra).filter(Extra.id == extra_id).first()
    if not extra:
        raise HTTPException(404, "Extra not found")
    data = payload.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(extra, key, value)
    db.commit()
    await manager.broadcast_queue_update(str(extra.tenant_id), {"extra_id": str(extra.id), **data})
    return {"status": "updated"}

@router.delete("/extras/{extra_id}")
async def delete_extra(
    extra_id: UUID,
    db: Session = Depends(get_db)
):
    extra = db.query(Extra).filter(Extra.id == extra_id).first()
    if not extra:
        raise HTTPException(404, "Extra not found")
    tenant_id = extra.tenant_id
    db.delete(extra)
    db.commit()
    await manager.broadcast_queue_update(str(tenant_id), {"extra_id": str(extra_id), "deleted": True})
    return {"status": "deleted"}

@router.post("/extras", response_model=ExtraSchema, status_code=201)
async def create_extra(
    tenant_id: UUID,
    payload: ExtraCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo item extra para o tenant informado."""
    extra = Extra(
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        category=payload.category,
        stock=payload.stock,
        is_active=payload.is_active,
    )
    db.add(extra)
    db.commit()
    db.refresh(extra)
    return extra

@router.get("/operation/config", response_model=dict)
async def get_operation_config(
    tenant_id: UUID,
    db: Session = Depends(get_db)
):
    op_cfg = db.query(OperationConfig).options(
        joinedload(OperationConfig.services).joinedload(OperationConfigEquipment.equipment),
        joinedload(OperationConfig.extras).joinedload(OperationConfigExtra.extra),
    ).filter(OperationConfig.tenant_id == tenant_id).order_by(OperationConfig.created_at.desc()).first()

    return {
        "services": [
            {
                "service_id": str(s.service_id),
                "active": s.active,
                "duration": s.duration,
                "price": float(s.price),
                "equipment_count": s.equipment_count,
                "name": s.equipment.name if s.equipment else None,
                "description": s.equipment.description if s.equipment else None,
            } for s in op_cfg.services
        ],
        "equipments": [
            {
                "equipment_id": str(e.equipment_id),
                "active": e.active,
                "duration": e.duration,
                "price": float(e.price),
                "equipment_count": e.equipment_count,
                "name": e.equipment.name if e.equipment else None,
                "description": e.equipment.description if e.equipment else None,
            } for e in op_cfg.equipments
        ],
        "extras": [
            {
                "extra_id": str(e.extra_id),
                "active": e.active,
                "duration": e.duration,
                "price": float(e.price),
                "equipment_count": e.equipment_count,
                "name": e.extra.name if e.extra else None,
                "description": e.extra.description if e.extra else None,
            } for e in op_cfg.extras
        ],
    } 