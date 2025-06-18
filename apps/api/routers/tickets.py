from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from models import Ticket, Service, PaymentSession, Consent
from schemas import (
    Ticket as TicketSchema, 
    TicketList, 
    TicketWithService, 
    TicketQueue,
    TicketStatusUpdate,
    TicketWithStatus,
    TicketListWithStatus
)
from auth import get_current_operator, get_current_user
from services.websocket import websocket_manager
from services.printer import printer_manager
from database import get_db
from constants import (
    TicketStatus, can_transition, get_valid_transitions, 
    TICKET_STATE_CATEGORIES, TICKET_STATUS_DESCRIPTIONS, TICKET_STATUS_COLORS,
    QueueSortOrder, QueuePriority
)
from services.queue_manager import get_queue_manager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"]
)

@router.get("", response_model=TicketListWithStatus)
async def list_tickets(
    status: Optional[str] = None,
    category: Optional[str] = None,  # pending_service, waiting, active, finished
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Lista tickets com filtros avançados por status e categoria"""
    
    query = db.query(Ticket).filter(Ticket.tenant_id == current_operator.tenant_id)
    
    # Filtro por status específico
    if status:
        try:
            ticket_status = TicketStatus(status)
            query = query.filter(Ticket.status == ticket_status.value)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Status inválido: {status}"
            )
    
    # Filtro por categoria
    if category:
        if category not in TICKET_STATE_CATEGORIES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Categoria inválida: {category}. Opções: {list(TICKET_STATE_CATEGORIES.keys())}"
            )
        
        category_statuses = TICKET_STATE_CATEGORIES[category]
        status_values = [s.value for s in category_statuses]
        query = query.filter(Ticket.status.in_(status_values))
        
    total = query.count()
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"items": tickets, "total": total}

@router.get("/queue", response_model=TicketQueue)
async def get_ticket_queue(
    sort_order: QueueSortOrder = QueueSortOrder.FIFO,
    service_id: Optional[str] = None,
    priority_filter: Optional[QueuePriority] = None,
    include_called: bool = True,
    include_in_progress: bool = True,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Retorna a fila de tickets com ordenação e filtros avançados"""
    
    queue_manager = get_queue_manager(db)
    
    # Buscar tickets da fila
    tickets = queue_manager.get_queue_tickets(
        tenant_id=str(current_operator.tenant_id),
        sort_order=sort_order,
        service_id=service_id,
        priority_filter=priority_filter,
        include_called=include_called,
        include_in_progress=include_in_progress
    )
    
    # Converter para TicketInQueue com informações adicionais
    queue_tickets = []
    for ticket in tickets:
        # Calcular tempo de espera
        waiting_minutes = 0
        if ticket.queued_at:
            waiting_minutes = (datetime.utcnow() - ticket.queued_at).total_seconds() / 60
        
        # Criar ticket enriquecido (usando dict básico por enquanto)
        queue_ticket = {
            **ticket.__dict__,
            "service": ticket.service,
            "waiting_time_minutes": waiting_minutes,
            "estimated_service_time": ticket.service.duration_minutes if ticket.service else 10
        }
        queue_tickets.append(queue_ticket)
    
    # Agrupar por diferentes critérios
    by_service = {}
    by_status = {}
    by_priority = {}
    
    for ticket in tickets:
        # Por serviço
        service_name = ticket.service.name if ticket.service else "Sem serviço"
        if service_name not in by_service:
            by_service[service_name] = []
        by_service[service_name].append(ticket)
        
        # Por status
        if ticket.status not in by_status:
            by_status[ticket.status] = []
        by_status[ticket.status].append(ticket)
        
        # Por prioridade
        priority = getattr(ticket, 'priority', 'normal')
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(ticket)
    
    # Obter estatísticas da fila
    queue_stats = queue_manager.get_queue_statistics(str(current_operator.tenant_id))
    
    # Calcular tempo total estimado
    estimated_total_time = sum([
        getattr(t, 'estimated_wait_minutes', 0) or 0 
        for t in tickets 
        if t.status == TicketStatus.IN_QUEUE.value
    ])
    
    return {
        "items": tickets,
        "total": len(tickets),
        "by_service": by_service,
        "by_status": by_status,
        "by_priority": by_priority,
        "queue_stats": queue_stats,
        "estimated_total_time": estimated_total_time
    }

@router.get("/queue/next")
async def get_next_ticket(
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Retorna o próximo ticket para o operador atual"""
    
    queue_manager = get_queue_manager(db)
    
    next_ticket = queue_manager.get_next_ticket_for_operator(
        tenant_id=str(current_operator.tenant_id),
        operator_id=str(current_operator.id)
    )
    
    if not next_ticket:
        return {
            "message": "Nenhum ticket disponível na fila",
            "ticket": None
        }
    
    return {
        "message": f"Próximo ticket: #{next_ticket.ticket_number}",
        "ticket": next_ticket
    }

@router.post("/queue/assign/{ticket_id}")
async def assign_ticket(
    ticket_id: str,
    operator_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Atribui um ticket a um operador"""
    
    # Se não especificado, atribuir ao operador atual
    target_operator_id = operator_id or str(current_operator.id)
    
    queue_manager = get_queue_manager(db)
    
    success = queue_manager.assign_ticket_to_operator(ticket_id, target_operator_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado"
        )
    
    return {
        "message": f"Ticket atribuído ao operador {target_operator_id}",
        "ticket_id": ticket_id,
        "operator_id": target_operator_id
    }

@router.post("/queue/auto-expire")
async def auto_expire_tickets(
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Expira automaticamente tickets antigos"""
    
    queue_manager = get_queue_manager(db)
    
    expired_count = queue_manager.auto_expire_old_tickets(
        tenant_id=str(current_operator.tenant_id)
    )
    
    return {
        "message": f"{expired_count} tickets expirados automaticamente",
        "expired_count": expired_count
    }

@router.get("/queue/statistics")
async def get_queue_statistics(
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Retorna estatísticas detalhadas da fila"""
    
    queue_manager = get_queue_manager(db)
    
    stats = queue_manager.get_queue_statistics(str(current_operator.tenant_id))
    
    return stats

@router.get("/{ticket_id}", response_model=TicketWithStatus)
async def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Retorna um ticket específico com informações de status"""
    
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_operator.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado"
        )
        
    return ticket

@router.patch("/{ticket_id}/status", response_model=TicketWithStatus)
async def update_ticket_status(
    ticket_id: str,
    status_update: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Atualiza o status de um ticket com validação de transições"""
    
    # Buscar ticket
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_operator.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado"
        )
    
    # Validar transição
    current_status = TicketStatus(ticket.status)
    new_status = status_update.status
    
    if not can_transition(current_status, new_status):
        valid_transitions = [s.value for s in get_valid_transitions(current_status)]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transição inválida de '{current_status.value}' para '{new_status.value}'. "
                   f"Transições válidas: {valid_transitions}"
        )
        
    # Atualizar status e timestamps
    old_status = ticket.status
    ticket.status = new_status.value
    ticket.updated_at = datetime.utcnow()
    
    # Atualizar timestamps específicos baseado no novo status
    now = datetime.utcnow()
    
    if new_status == TicketStatus.IN_QUEUE:
        ticket.queued_at = now
    elif new_status == TicketStatus.CALLED:
        ticket.called_at = now
    elif new_status == TicketStatus.IN_PROGRESS:
        ticket.started_at = now
    elif new_status == TicketStatus.COMPLETED:
        ticket.completed_at = now
    elif new_status == TicketStatus.CANCELLED:
        ticket.cancelled_at = now
        ticket.cancellation_reason = status_update.cancellation_reason
    elif new_status == TicketStatus.EXPIRED:
        ticket.expired_at = now
    
    # Adicionar notas do operador
    if status_update.operator_notes:
        ticket.operator_notes = status_update.operator_notes
    
    db.commit()
    db.refresh(ticket)
    
    logger.info(f"🔄 Ticket #{ticket.ticket_number} status changed: {old_status} → {new_status.value}")
    
    # Notificar via WebSocket (se disponível)
    try:
        notification_data = {
            "type": "ticket_status_changed",
            "ticket": {
                "id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "old_status": old_status,
                "new_status": new_status.value,
                "operator": current_operator.name
            }
        }
        # await websocket_manager.broadcast_to_tenant(ticket.tenant_id, notification_data)
        logger.info(f"📡 Status change notification prepared: {notification_data}")
    except Exception as e:
        logger.error(f"❌ Error sending WebSocket notification: {e}")
    
    return ticket

# Endpoints específicos para transições comuns
@router.post("/{ticket_id}/call")
async def call_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Chama um ticket da fila (in_queue → called)"""
    
    status_update = TicketStatusUpdate(
        status=TicketStatus.CALLED,
        operator_notes=f"Chamado pelo operador {current_operator.name}"
    )
    
    return await update_ticket_status(ticket_id, status_update, db, current_operator)

@router.post("/{ticket_id}/start")
async def start_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Inicia atendimento de um ticket (called → in_progress)"""
    
    status_update = TicketStatusUpdate(
        status=TicketStatus.IN_PROGRESS,
        operator_notes=f"Atendimento iniciado por {current_operator.name}"
    )
    
    return await update_ticket_status(ticket_id, status_update, db, current_operator)

@router.post("/{ticket_id}/complete")
async def complete_ticket(
    ticket_id: str,
    operator_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Completa um ticket (in_progress → completed)"""
    
    status_update = TicketStatusUpdate(
        status=TicketStatus.COMPLETED,
        operator_notes=operator_notes or f"Atendimento concluído por {current_operator.name}"
    )
    
    return await update_ticket_status(ticket_id, status_update, db, current_operator)

@router.post("/{ticket_id}/cancel")
async def cancel_ticket(
    ticket_id: str,
    cancellation_reason: str,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Cancela um ticket"""
    
    status_update = TicketStatusUpdate(
        status=TicketStatus.CANCELLED,
        cancellation_reason=cancellation_reason,
        operator_notes=f"Cancelado por {current_operator.name}"
    )
    
    return await update_ticket_status(ticket_id, status_update, db, current_operator)

@router.post("/{ticket_id}/reprint")
async def reprint_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Reimprimir um ticket"""
    
    # Buscar ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket não encontrado"
        )
    
    # Buscar serviço
    service = db.query(Service).filter(Service.id == ticket.service_id).first()
    
    try:
        # Preparar dados para reimpressão
        print_data = {
            "ticket_number": ticket.ticket_number,
            "service_name": service.name if service else "Serviço",
            "customer_name": ticket.customer_name,
            "customer_cpf": ticket.customer_cpf[-4:] if ticket.customer_cpf else "",
            "status": "REIMPRESSO",
            "created_at": ticket.created_at.isoformat() if ticket.created_at else datetime.utcnow().isoformat()
        }
        
        # Enviar para fila de impressão
        await printer_manager.queue_print_job("default", "ticket", print_data)
        
        # Atualizar ticket
        ticket.reprinted_at = datetime.utcnow()
        ticket.print_attempts += 1
        db.commit()
        
        logger.info(f"🖨️ Ticket #{ticket.ticket_number} queued for reprint (attempt #{ticket.print_attempts})")
        
        return {
            "status": "success",
            "message": f"Ticket #{ticket.ticket_number} enviado para reimpressão",
            "ticket_id": str(ticket.id),
            "print_attempt": ticket.print_attempts,
            "queue_size": printer_manager.print_queue.qsize()
        }
        
    except Exception as e:
        logger.error(f"❌ Error reprinting ticket #{ticket.ticket_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao reimprimir ticket: {str(e)}"
        )

@router.get("/status/info")
async def get_status_info():
    """Retorna informações sobre todos os status possíveis"""
    from constants import TicketStatus, get_status_info, TICKET_STATE_CATEGORIES
    
    status_info = {}
    for ticket_status in TicketStatus:
        status_info[ticket_status.value] = get_status_info(ticket_status)
    
    return {
        "statuses": status_info,
        "categories": TICKET_STATE_CATEGORIES,
        "workflow": "paid → printing → in_queue → called → in_progress → completed"
    }

@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Retorna estatísticas do dashboard para o operador"""
    
    # Buscar todos os tickets do tenant
    tickets = db.query(Ticket).filter(
        Ticket.tenant_id == current_operator.tenant_id
    ).all()
    
    # Estatísticas por status
    stats_by_status = {}
    for status in TicketStatus:
        count = len([t for t in tickets if t.status == status.value])
        stats_by_status[status.value] = {
            "count": count,
            "description": TICKET_STATUS_DESCRIPTIONS.get(status, ""),
            "color": TICKET_STATUS_COLORS.get(status, "#000000")
        }
    
    # Estatísticas por categoria
    stats_by_category = {}
    for category, statuses in TICKET_STATE_CATEGORIES.items():
        count = len([t for t in tickets if TicketStatus(t.status) in statuses])
        stats_by_category[category] = count
    
    # Tickets ativos (precisam de atenção)
    active_tickets = [t for t in tickets if t.status in [
        TicketStatus.IN_QUEUE.value,
        TicketStatus.CALLED.value,
        TicketStatus.IN_PROGRESS.value
    ]]
    
    # Tickets com problemas
    problem_tickets = [t for t in tickets if t.status in [
        TicketStatus.PRINT_ERROR.value,
        TicketStatus.EXPIRED.value
    ]]
    
    # Estatísticas de hoje
    today = datetime.utcnow().date()
    today_tickets = [t for t in tickets if t.created_at.date() == today]
    today_completed = [t for t in today_tickets if t.status == TicketStatus.COMPLETED.value]
    
    # Tempo médio de atendimento (tickets completados hoje)
    avg_service_time = None
    if today_completed:
        service_times = []
        for ticket in today_completed:
            if ticket.started_at and ticket.completed_at:
                service_time = (ticket.completed_at - ticket.started_at).total_seconds() / 60  # em minutos
                service_times.append(service_time)
        
        if service_times:
            avg_service_time = sum(service_times) / len(service_times)
    
    return {
        "summary": {
            "total_tickets": len(tickets),
            "active_tickets": len(active_tickets),
            "problem_tickets": len(problem_tickets),
            "today_tickets": len(today_tickets),
            "today_completed": len(today_completed),
            "avg_service_time_minutes": round(avg_service_time, 1) if avg_service_time else None
        },
        "by_status": stats_by_status,
        "by_category": stats_by_category,
        "active_queue": [
            {
                "id": str(t.id),
                "ticket_number": t.ticket_number,
                "customer_name": t.customer_name,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
                "waiting_time_minutes": round((datetime.utcnow() - t.created_at).total_seconds() / 60, 1)
            }
            for t in active_tickets
        ],
        "problems": [
            {
                "id": str(t.id),
                "ticket_number": t.ticket_number,
                "customer_name": t.customer_name,
                "status": t.status,
                "issue": TICKET_STATUS_DESCRIPTIONS.get(TicketStatus(t.status), ""),
                "created_at": t.created_at.isoformat()
            }
            for t in problem_tickets
        ]
    } 