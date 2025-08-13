from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

from apps.api.database import get_db
from apps.api.models import TicketServiceProgress, TicketService, Service, Equipment, Ticket
from apps.api.schemas.ticket_service_progress import (
    TicketServiceProgressCreate,
    TicketServiceProgressUpdate,
    TicketServiceProgressOut,
    TicketServiceProgressWithService,
    TicketServiceProgressList
)
from apps.api.dependencies import get_current_operator
from apps.api.models import Operator

router = APIRouter(tags=["ticket-service-progress"])

@router.get("/ticket/{ticket_id}", response_model=TicketServiceProgressList)
async def get_ticket_service_progress(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Obtém o progresso de todos os serviços de um ticket"""
    
    # Verificar se o ticket existe e pertence ao tenant do operador
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_operator.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    # Buscar todos os ticket_services do ticket
    ticket_services = db.query(TicketService).filter(
        TicketService.ticket_id == ticket_id
    ).all()
    
    progress_items = []
    
    for ticket_service in ticket_services:
        # Buscar ou criar progresso para este ticket_service
        progress = db.query(TicketServiceProgress).filter(
            TicketServiceProgress.ticket_service_id == ticket_service.id
        ).first()
        
        if not progress:
            # Criar progresso automaticamente se não existir
            service = db.query(Service).filter(Service.id == ticket_service.service_id).first()
            progress = TicketServiceProgress(
                ticket_service_id=ticket_service.id,
                status="pending",
                duration_minutes=service.duration_minutes if service else 10
            )
            db.add(progress)
            db.commit()
            db.refresh(progress)
        
        # Buscar informações do serviço e equipamento
        service = db.query(Service).filter(Service.id == ticket_service.service_id).first()
        equipment = None
        if progress.equipment_id:
            equipment = db.query(Equipment).filter(Equipment.id == progress.equipment_id).first()
        
        # Criar objeto de resposta
        progress_with_service = TicketServiceProgressWithService(
            id=progress.id,
            ticket_service_id=progress.ticket_service_id,
            status=progress.status,
            duration_minutes=progress.duration_minutes,
            operator_notes=progress.operator_notes,
            equipment_id=progress.equipment_id,
            started_at=progress.started_at,
            completed_at=progress.completed_at,
            created_at=progress.created_at,
            updated_at=progress.updated_at,
            service_name=service.name if service else "Serviço",
            service_price=float(ticket_service.price),
            equipment_name=equipment.identifier if equipment else None
        )
        
        progress_items.append(progress_with_service)
    
    return TicketServiceProgressList(
        items=progress_items,
        total=len(progress_items)
    )

@router.post("/{progress_id}/start", response_model=TicketServiceProgressOut)
async def start_service_progress(
    progress_id: UUID,
    equipment_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Inicia o progresso de um serviço específico"""
    
    # Buscar o progresso
    progress = db.query(TicketServiceProgress).filter(
        TicketServiceProgress.id == progress_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progresso não encontrado")
    
    # Verificar se o ticket pertence ao tenant do operador
    ticket_service = db.query(TicketService).filter(TicketService.id == progress.ticket_service_id).first()
    if not ticket_service:
        raise HTTPException(status_code=404, detail="Ticket service não encontrado")
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_service.ticket_id).first()
    if not ticket or ticket.tenant_id != current_operator.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Verificar se o serviço já está em progresso
    if progress.status == "in_progress":
        raise HTTPException(status_code=400, detail="Serviço já está em progresso")
    
    # Verificar se o equipamento está disponível
    if equipment_id:
        equipment = db.query(Equipment).filter(
            Equipment.id == equipment_id,
            Equipment.tenant_id == current_operator.tenant_id
        ).first()
        
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        
        if equipment.status.value != "online":
            raise HTTPException(status_code=400, detail="Equipamento não está disponível")
        
        # Marcar equipamento como em uso
        equipment.status = "in_use"
        db.commit()
    
    # Atualizar progresso
    progress.status = "in_progress"
    progress.started_at = datetime.now(timezone.utc)
    progress.equipment_id = equipment_id
    progress.operator_notes = f"Iniciado por {current_operator.name}"
    
    db.commit()
    db.refresh(progress)
    
    return progress

@router.post("/{progress_id}/complete", response_model=TicketServiceProgressOut)
async def complete_service_progress(
    progress_id: UUID,
    operator_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Completa o progresso de um serviço específico"""
    
    # Buscar o progresso
    progress = db.query(TicketServiceProgress).filter(
        TicketServiceProgress.id == progress_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progresso não encontrado")
    
    # Verificar se o ticket pertence ao tenant do operador
    ticket_service = db.query(TicketService).filter(TicketService.id == progress.ticket_service_id).first()
    if not ticket_service:
        raise HTTPException(status_code=404, detail="Ticket service não encontrado")
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_service.ticket_id).first()
    if not ticket or ticket.tenant_id != current_operator.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Verificar se o serviço está em progresso
    if progress.status != "in_progress":
        raise HTTPException(status_code=400, detail="Serviço não está em progresso")
    
    # ✅ NOVO: Liberar equipamento se houver
    if progress.equipment_id:
        equipment = db.query(Equipment).filter(Equipment.id == progress.equipment_id).first()
        if equipment:
            logger.info(f"🔧 DEBUG - Liberando equipamento {equipment.identifier} do serviço {progress_id}")
            equipment.status = "online"
            equipment.assigned_operator_id = None
            progress.equipment_id = None
            db.commit()
            logger.info(f"🔧 DEBUG - Equipamento {equipment.identifier} liberado com sucesso")
    
    # Atualizar progresso
    progress.status = "completed"
    progress.completed_at = datetime.now(timezone.utc)
    if operator_notes:
        progress.operator_notes = operator_notes
    
    db.commit()
    db.refresh(progress)
    
    return progress

@router.post("/{progress_id}/cancel", response_model=TicketServiceProgressOut)
async def cancel_service_progress(
    progress_id: UUID,
    reason: str,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Cancela o progresso de um serviço específico"""
    
    # Buscar o progresso
    progress = db.query(TicketServiceProgress).filter(
        TicketServiceProgress.id == progress_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progresso não encontrado")
    
    # Verificar se o ticket pertence ao tenant do operador
    ticket_service = db.query(TicketService).filter(TicketService.id == progress.ticket_service_id).first()
    if not ticket_service:
        raise HTTPException(status_code=404, detail="Ticket service não encontrado")
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_service.ticket_id).first()
    if not ticket or ticket.tenant_id != current_operator.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # ✅ NOVO: Liberar equipamento se houver
    if progress.equipment_id:
        equipment = db.query(Equipment).filter(Equipment.id == progress.equipment_id).first()
        if equipment:
            logger.info(f"🔧 DEBUG - Liberando equipamento {equipment.identifier} do serviço cancelado {progress_id}")
            equipment.status = "online"
            equipment.assigned_operator_id = None
            progress.equipment_id = None
            db.commit()
            logger.info(f"🔧 DEBUG - Equipamento {equipment.identifier} liberado com sucesso")
    
    # Atualizar progresso
    progress.status = "cancelled"
    progress.operator_notes = f"Cancelado por {current_operator.name}: {reason}"
    
    db.commit()
    db.refresh(progress)
    
    return progress

@router.patch("/{progress_id}", response_model=TicketServiceProgressOut)
async def update_service_progress(
    progress_id: UUID,
    progress_update: TicketServiceProgressUpdate,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Atualiza o progresso de um serviço específico"""
    
    # Buscar o progresso
    progress = db.query(TicketServiceProgress).filter(
        TicketServiceProgress.id == progress_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progresso não encontrado")
    
    # Verificar se o ticket pertence ao tenant do operador
    ticket_service = db.query(TicketService).filter(TicketService.id == progress.ticket_service_id).first()
    if not ticket_service:
        raise HTTPException(status_code=404, detail="Ticket service não encontrado")
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_service.ticket_id).first()
    if not ticket or ticket.tenant_id != current_operator.tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Atualizar campos fornecidos
    update_data = progress_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(progress, field, value)
    
    db.commit()
    db.refresh(progress)
    
    return progress 