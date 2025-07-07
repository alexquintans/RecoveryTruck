from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import logging
from pydantic import BaseModel
from uuid import UUID

from models import Ticket, Service, PaymentSession, Consent, Equipment, TicketExtra, EquipmentStatus, TicketService
from schemas import (
    Ticket as TicketSchema, 
    TicketList, 
    TicketWithService, 
    TicketQueue,
    TicketStatusUpdate,
    TicketWithStatus,
    TicketListWithStatus,
    TicketCreate,
    TicketOut,
    TicketInQueue
)
from auth import get_current_operator
from services.websocket import websocket_manager
from services.printer import printer_manager
from database import get_db
from constants import (
    TicketStatus, can_transition, get_valid_transitions, 
    TICKET_STATE_CATEGORIES, TICKET_STATUS_DESCRIPTIONS, TICKET_STATUS_COLORS,
    QueueSortOrder, QueuePriority, get_status_info as get_status_info_func
)
from services.queue_manager import get_queue_manager

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["tickets"]
)

class CallTicketRequest(BaseModel):
    equipment_id: str

@router.get("", response_model=TicketListWithStatus)
async def list_tickets(
    status: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = None,  # pending_service, waiting, active, finished
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Lista tickets com filtros avançados por status e categoria"""
    
    query = db.query(Ticket).options(
        joinedload(Ticket.services).joinedload(TicketService.service)
    ).filter(Ticket.tenant_id == current_operator.tenant_id)
    
    # Filtro por status específico
    if status:
        # Aceitar múltiplos status separados por vírgula
        status_list = [s.strip() for s in status.split(',')]
        valid_statuses = []
        
        for status_item in status_list:
            try:
                ticket_status = TicketStatus(status_item)
                valid_statuses.append(ticket_status.value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Status inválido: {status_item}"
            )
        
        if valid_statuses:
            query = query.filter(Ticket.status.in_(valid_statuses))
    
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
    ticket_schemas = [ticket_to_with_status(t) for t in tickets]
    
    return TicketListWithStatus(items=ticket_schemas, total=total)

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
    
    # Buscar tickets da fila (apenas in_queue)
    tickets = queue_manager.get_queue_tickets(
        tenant_id=str(current_operator.tenant_id),
        sort_order=sort_order,
        service_id=service_id,
        priority_filter=priority_filter,
        include_called=False,
        include_in_progress=False
    )
    
    # Converter para TicketInQueue com informações adicionais
    queue_tickets = []
    for ticket in tickets:
        # Calcular tempo de espera
        waiting_minutes = 0
        if ticket.queued_at:
            waiting_minutes = (datetime.utcnow() - ticket.queued_at).total_seconds() / 60
        
        # Criar ticket enriquecido (usando dict básico por enquanto)
        data = ticket.__dict__.copy()
        for field in ["service", "waiting_time_minutes", "waiting_status", "priority_info", "estimated_service_time"]:
            data.pop(field, None)
        
        # Obter todos os serviços associados
        services_list = [ts.service for ts in ticket.services] if ticket.services else []
        data["services"] = services_list
        
        # Obter serviço principal (primeiro)
        service = services_list[0] if services_list else None
        service_id = service.id if service else None
        
        queue_ticket = TicketInQueue(
            **data,
            service=service,
            service_id=service_id,
            waiting_time_minutes=waiting_minutes,
            waiting_status="normal",
            priority_info={},
            estimated_service_time=service.duration_minutes if service else 10
        )
        queue_tickets.append(queue_ticket)
    
    # Agrupar por diferentes critérios
    by_service = {}
    by_status = {}
    by_priority = {}
    
    for ticket in queue_tickets:
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
        for t in queue_tickets 
        if t.status == TicketStatus.IN_QUEUE.value
    ])
    
    return TicketQueue(
        items=queue_tickets,
        total=len(queue_tickets),
        by_service=by_service,
        by_status=by_status,
        by_priority=by_priority,
        queue_stats=queue_stats,
        estimated_total_time=estimated_total_time
    )

@router.get("/queue/public", response_model=TicketQueue)
async def get_public_queue(
    tenant_id: str = Query(..., description="ID do tenant"),
    sort_order: QueueSortOrder = QueueSortOrder.FIFO,
    service_id: Optional[str] = None,
    priority_filter: Optional[QueuePriority] = None,
    include_called: bool = True,
    include_in_progress: bool = True,
    db: Session = Depends(get_db)
):
    """Retorna a fila de tickets para exibição pública (sem autenticação)"""
    
    queue_manager = get_queue_manager(db)
    
    # Buscar tickets da fila
    tickets = queue_manager.get_queue_tickets(
        tenant_id=tenant_id,
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
        data = ticket.__dict__.copy()
        for field in ["service", "waiting_time_minutes", "waiting_status", "priority_info", "estimated_service_time"]:
            data.pop(field, None)
        
        # Obter todos os serviços associados
        services_list = [ts.service for ts in ticket.services] if ticket.services else []
        data["services"] = services_list
        
        # Obter serviço principal (primeiro)
        service = services_list[0] if services_list else None
        service_id = service.id if service else None
        
        queue_ticket = TicketInQueue(
            **data,
            service=service,
            service_id=service_id,
            waiting_time_minutes=waiting_minutes,
            waiting_status="normal",
            priority_info={},
            estimated_service_time=service.duration_minutes if service else 10
        )
        queue_tickets.append(queue_ticket)
    
    # Agrupar por diferentes critérios
    by_service = {}
    by_status = {}
    by_priority = {}
    
    for ticket in queue_tickets:
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
    queue_stats = queue_manager.get_queue_statistics(tenant_id)
    
    # Calcular tempo total estimado
    estimated_total_time = sum([
        getattr(t, 'estimated_wait_minutes', 0) or 0 
        for t in queue_tickets 
        if t.status == TicketStatus.IN_QUEUE.value
    ])
    
    return TicketQueue(
        items=queue_tickets,
        total=len(queue_tickets),
        by_service=by_service,
        by_status=by_status,
        by_priority=by_priority,
        queue_stats=queue_stats,
        estimated_total_time=estimated_total_time
    )

@router.get("/queue/next")
async def get_next_ticket(
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Chama o próximo ticket da fila para o operador atual, atualiza status e dispara eventos"""
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
    # Atualizar status do ticket para 'called'
    old_status = next_ticket.status
    next_ticket.status = TicketStatus.CALLED.value
    next_ticket.called_at = datetime.utcnow()
    next_ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(next_ticket)
    # Buscar informações do equipamento se houver
    equipment_name = None
    if next_ticket.equipment_id:
        equipment = db.query(Equipment).filter(Equipment.id == next_ticket.equipment_id).first()
        if equipment:
            equipment_name = equipment.name
    # Broadcast de ticket chamado
    await websocket_manager.broadcast_ticket_called(
        tenant_id=str(current_operator.tenant_id),
        ticket=next_ticket,
        operator_name=current_operator.name,
        equipment_name=equipment_name
    )
    # Broadcast de atualização da fila para todos os operadores
    queue_manager = get_queue_manager(db)
    queue_data = queue_manager.get_queue_tickets(str(current_operator.tenant_id))
    await websocket_manager.broadcast_queue_update(str(current_operator.tenant_id), queue_data)
    return {
        "message": f"Próximo ticket chamado: #{next_ticket.ticket_number}",
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

def ticket_to_with_status(ticket):
    # Converter serviços associados
    services = []
    service_objs = []
    if hasattr(ticket, "services") and ticket.services:
        for ts in ticket.services:
            # Adiciona info básica para lista de services
            services.append({
                "service_id": ts.service_id,
                "price": float(ts.price)
            })
            # Adiciona info detalhada se houver relação
            if hasattr(ts, "service") and ts.service:
                service_objs.append({
                    "id": str(ts.service.id),
                    "name": ts.service.name,
                    "price": float(ts.service.price) if hasattr(ts.service, "price") else None,
                })
    # Pega o primeiro serviço como principal
    main_service = service_objs[0] if service_objs else None
    # Cliente como objeto
    customer_obj = {
        "name": ticket.customer_name or "Cliente",
        "cpf": ticket.customer_cpf or "",
        "phone": ticket.customer_phone or "",
    }
    # Montar dicionário explicitamente, incluindo todos os campos obrigatórios
    data = {
        'id': ticket.id or UUID('00000000-0000-0000-0000-000000000000'),
        'tenant_id': ticket.tenant_id or UUID('00000000-0000-0000-0000-000000000000'),
        'service_id': main_service['id'] if main_service else UUID('00000000-0000-0000-0000-000000000000'),
        'payment_session_id': getattr(ticket, 'payment_session_id', None) or UUID('00000000-0000-0000-0000-000000000000'),
        'ticket_number': ticket.ticket_number or 0,
        'status': ticket.status or "paid",
        'customer_name': ticket.customer_name or "Cliente",
        'customer_cpf': ticket.customer_cpf or "",
        'customer_phone': ticket.customer_phone or "",
        'consent_version': ticket.consent_version or "1.0",
        'priority': getattr(ticket, 'priority', 'normal') or 'normal',
        'queue_position': getattr(ticket, 'queue_position', None) or None,
        'estimated_wait_minutes': getattr(ticket, 'estimated_wait_minutes', None) or None,
        'assigned_operator_id': getattr(ticket, 'assigned_operator_id', None) or None,
        'created_at': ticket.created_at or datetime.utcnow(),
        'updated_at': ticket.updated_at or datetime.utcnow(),
        'printed_at': getattr(ticket, 'printed_at', None) or None,
        'queued_at': getattr(ticket, 'queued_at', None) or None,
        'called_at': getattr(ticket, 'called_at', None) or None,
        'started_at': getattr(ticket, 'started_at', None) or None,
        'completed_at': getattr(ticket, 'completed_at', None) or None,
        'cancelled_at': getattr(ticket, 'cancelled_at', None) or None,
        'expired_at': getattr(ticket, 'expired_at', None) or None,
        'reprinted_at': getattr(ticket, 'reprinted_at', None) or None,
        'operator_notes': getattr(ticket, 'operator_notes', None) or None,
        'cancellation_reason': getattr(ticket, 'cancellation_reason', None) or None,
        'print_attempts': getattr(ticket, 'print_attempts', 0) or 0,
        'reactivation_count': getattr(ticket, 'reactivation_count', 0) or 0,
        # Novos campos para frontend:
        'services': service_objs,
        'service': main_service,
        'service_name': main_service['name'] if main_service and 'name' in main_service else None,
        'customer': customer_obj,
    }
    try:
        return TicketWithStatus(**data, status_info=get_status_info_func(TicketStatus(ticket.status)), valid_transitions=[s.value for s in get_valid_transitions(TicketStatus(ticket.status))])
    except Exception as e:
        logger.error(f"Erro ao criar TicketWithStatus para ticket {ticket.id}: {e}")
        logger.error(f"Dados: {data}")
        raise

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
        
    return ticket_to_with_status(ticket)

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
        # Broadcast da atualização do ticket
        await websocket_manager.broadcast_ticket_update(str(ticket.tenant_id), ticket)
        
        # Notificação adicional para mudanças específicas
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
        
        # Broadcast da notificação para todos os clientes do tenant
        await websocket_manager.broadcast_to_tenant(str(ticket.tenant_id), notification_data)
        
        logger.info(f"📡 Status change notification sent: {notification_data}")
    except Exception as e:
        logger.error(f"❌ Error sending WebSocket notification: {e}")
    
    return ticket_to_with_status(ticket)

@router.post("/{ticket_id}/call")
async def call_ticket(
    ticket_id: str,
    request: CallTicketRequest,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    # Buscar ticket e equipamento
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    equipment = db.query(Equipment).filter(Equipment.id == request.equipment_id).first()
    if not ticket or not equipment:
        raise HTTPException(status_code=404, detail="Ticket ou equipamento não encontrado")
    # Validação de compatibilidade: o equipamento deve estar associado ao mesmo serviço do ticket
    ticket_service_ids = [str(ts.service_id) for ts in ticket.services]
    if equipment.service_id and str(equipment.service_id) not in ticket_service_ids:
        raise HTTPException(status_code=400, detail="Equipamento selecionado não é compatível com o serviço do ticket.")
    # Verifica se o equipamento está disponível
    if equipment.status != EquipmentStatus.online:
        raise HTTPException(status_code=400, detail="Equipamento não está disponível para uso.")
    # Atualizar status do ticket
    status_update = TicketStatusUpdate(
        status=TicketStatus.CALLED,
        operator_notes=f"Chamado pelo operador {current_operator.name}"
    )
    result = await update_ticket_status(ticket_id, status_update, db, current_operator)
    # Atualizar o equipment_id e operator_id do ticket
    ticket.equipment_id = request.equipment_id
    ticket.assigned_operator_id = current_operator.id
    # Marcar equipamento como indisponível
    equipment.status = EquipmentStatus.offline
    db.commit()
    db.refresh(ticket)
    db.refresh(equipment)
    # Buscar informações do equipamento
    equipment_name = None
    if ticket.equipment_id:
        equipment = db.query(Equipment).filter(Equipment.id == ticket.equipment_id).first()
        if equipment:
            equipment_name = equipment.identifier
    # Broadcast específico para displays e operadores
    await websocket_manager.broadcast_ticket_called(
            tenant_id=str(current_operator.tenant_id),
            ticket=ticket,
            operator_name=current_operator.name,
            equipment_name=equipment_name
        )
    # Broadcast de atualização da fila para todos os operadores
    queue_manager = get_queue_manager(db)
    queue_data = queue_manager.get_queue_tickets(str(current_operator.tenant_id))
    await websocket_manager.broadcast_queue_update(str(current_operator.tenant_id), queue_data)
    return result

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
    # Buscar ticket e equipamento
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    equipment = db.query(Equipment).filter(Equipment.id == ticket.equipment_id).first() if ticket and ticket.equipment_id else None
    status_update = TicketStatusUpdate(
        status=TicketStatus.COMPLETED,
        operator_notes=operator_notes or f"Atendimento concluído por {current_operator.name}"
    )
    result = await update_ticket_status(ticket_id, status_update, db, current_operator)
    # Liberar equipamento
    if equipment:
        equipment.status = EquipmentStatus.online
        db.commit()
        db.refresh(equipment)
    return result

@router.post("/{ticket_id}/cancel")
async def cancel_ticket(
    ticket_id: str,
    cancellation_reason: str,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Cancela um ticket"""
    # Buscar ticket e equipamento
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    equipment = db.query(Equipment).filter(Equipment.id == ticket.equipment_id).first() if ticket and ticket.equipment_id else None
    status_update = TicketStatusUpdate(
        status=TicketStatus.CANCELLED,
        cancellation_reason=cancellation_reason,
        operator_notes=f"Cancelado por {current_operator.name}"
    )
    result = await update_ticket_status(ticket_id, status_update, db, current_operator)
    # Liberar equipamento
    if equipment:
        equipment.status = EquipmentStatus.online
        db.commit()
        db.refresh(equipment)
    return result

@router.post("/{ticket_id}/reprint")
async def reprint_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
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
    status_info = {}
    for ticket_status in TicketStatus:
        status_info[ticket_status.value] = get_status_info_func(ticket_status)
    
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

@router.post("/tickets", response_model=TicketOut)
async def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db)
):
    # Get next ticket number for this tenant
    last_ticket = db.query(Ticket).filter(
        Ticket.tenant_id == ticket_in.tenant_id
    ).order_by(Ticket.ticket_number.desc()).first()
    
    ticket_number = 1 if not last_ticket else last_ticket.ticket_number + 1
    
    # Create ticket with PAID status
    ticket = Ticket(
        tenant_id=ticket_in.tenant_id,
        payment_session_id=None,  # Não há payment session neste fluxo
        ticket_number=ticket_number,
        status=TicketStatus.PAID.value,
        customer_name=ticket_in.customer_name,
        customer_cpf=ticket_in.customer_cpf,
        customer_phone=ticket_in.customer_phone,
        consent_version=ticket_in.consent_version,
        print_attempts=0
    )
    db.add(ticket)
    db.flush()  # para garantir que ticket.id está disponível

    # Adicionar serviços associados
    for service_item in ticket_in.services:
        ticket_service = TicketService(
            ticket_id=ticket.id,
            service_id=service_item.service_id,
            price=service_item.price
        )
        db.add(ticket_service)

    # Adicionar extras
    for extra in ticket_in.extras:
        ticket_extra = TicketExtra(
            ticket_id=ticket.id,
            extra_id=extra.extra_id,
            quantity=extra.quantity,
            price=extra.price
        )
        db.add(ticket_extra)
    
    db.commit()
    db.refresh(ticket)
    
    # Retornar ticket com serviços e extras
    return TicketOut(
        id=ticket.id,
        tenant_id=ticket.tenant_id,
        ticket_number=ticket.ticket_number,
        status=ticket.status,
        customer_name=ticket.customer_name,
        customer_cpf=ticket.customer_cpf,
        customer_phone=ticket.customer_phone,
        consent_version=ticket.consent_version,
        services=ticket_in.services,
        extras=ticket_in.extras,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at
    ) 