from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from database import get_db
from models import Service
from schemas import ServiceCreate, Service as ServiceSchema, ServiceList
from auth import get_current_operator

router = APIRouter(
    prefix="/services",
    tags=["services"]
)

@router.post("", response_model=ServiceSchema)
async def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Create new service."""
    db_service = Service(
        tenant_id=current_operator.tenant_id,
        name=service.name,
        description=service.description,
        price=service.price,
        duration_minutes=service.duration_minutes,
        equipment_count=service.equipment_count,
        is_active=service.is_active
    )
    
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    
    return db_service

@router.get("", response_model=ServiceList)
async def list_services(
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """List services with optional filters."""
    query = db.query(Service).filter(Service.tenant_id == current_operator.tenant_id)
    
    if is_active is not None:
        query = query.filter(Service.is_active == is_active)
        
    total = query.count()
    services = query.offset(skip).limit(limit).all()
    
    return {"items": services, "total": total}

@router.get("/{service_id}", response_model=ServiceSchema)
async def get_service(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Get service by ID."""
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == current_operator.tenant_id
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
        
    return service

@router.put("/{service_id}", response_model=ServiceSchema)
async def update_service(
    service_id: uuid.UUID,
    service: ServiceCreate,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Update service."""
    db_service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == current_operator.tenant_id
    ).first()
    
    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
        
    for field, value in service.dict().items():
        setattr(db_service, field, value)
        
    db.commit()
    db.refresh(db_service)
    
    return db_service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Soft delete service (set is_active=False)."""
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.tenant_id == current_operator.tenant_id
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
        
    service.is_active = False
    db.commit() 