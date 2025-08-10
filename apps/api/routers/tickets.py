from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import case
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import logging
from pydantic import BaseModel
from uuid import UUID

from models import Ticket, Service, PaymentSession, Consent, Equipment, TicketExtra, EquipmentStatus, TicketService, Operator, Extra, OperationConfigExtra
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
    TicketInQueue,
    PaymentForTicket,
    PaymentSessionWithQR,
    TicketForPanel,
    TicketExtraOut,
    ServiceForTicket,
    TicketServiceWithDetails,
    ExtraForTicket,
    TicketExtraWithDetails,
    TicketServiceItem
)
from auth import get_current_operator
from services.websocket import websocket_manager
from services.printer_service import printer_manager
from database import get_db
from constants import (
    TicketStatus, can_transition, get_valid_transitions, 
    TICKET_STATE_CATEGORIES, TICKET_STATUS_DESCRIPTIONS, TICKET_STATUS_COLORS,
    QueueSortOrder, QueuePriority, get_status_info as get_status_info_func,
    get_waiting_time_status, PRIORITY_DESCRIPTIONS, PRIORITY_COLORS
)
from services.queue_manager import get_queue_manager
from services.payment.factory import PaymentAdapterFactory
from services.payment.terminal_manager import TerminalManager
from services.notification_service import OperatorNotificationService as NotificationService
from services.logging import setup_logging
from models import Extra
from models import Tenant
from models import OperationConfig
from models import TicketServiceProgress

# Import do MercadoPagoAdapter será feito localmente quando necessário

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["tickets"]
)

class CallTicketRequest(BaseModel):
    equipment_id: str

class CallServiceRequest(BaseModel):
    equipment_id: str
    service_id: str

@router.get("/my-tickets", response_model=List[TicketForPanel], tags=["operator"])
async def get_my_tickets(
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Lista os tickets atribuídos ao operador logado."""
    logger.info(f"🔍 DEBUG - Buscando tickets para operador {current_operator.id}")
    logger.info(f"🔍 DEBUG - Tenant ID: {current_operator.tenant_id}")
    logger.info(f"🔍 DEBUG - Operador nome: {current_operator.name}")
    
    # Buscar tickets do operador
    tickets = db.query(Ticket).options(
        joinedload(Ticket.services).joinedload(TicketService.service),
        joinedload(Ticket.extras).joinedload(TicketExtra.extra)
    ).filter(
        Ticket.tenant_id == current_operator.tenant_id,
        Ticket.assigned_operator_id == current_operator.id,
        Ticket.status.in_(['called', 'in_progress'])
    ).order_by(Ticket.called_at.desc()).all()
    
    logger.info(f"🔍 DEBUG - Tickets encontrados: {len(tickets)}")
    
    result = []
    for ticket in tickets:
        logger.info(f"🔍 DEBUG - Processando ticket {ticket.id} (status: {ticket.status})")
        
        # Converter serviços
        services_with_details = []
        if ticket.services:
            for ts in ticket.services:
                service_for_ticket = ServiceForTicket(
                    id=ts.service.id,
                    name=ts.service.name,
                    price=ts.service.price
                )
                service_with_details = TicketServiceWithDetails(
                    price=ts.price,
                    service=service_for_ticket
                )
                services_with_details.append(service_with_details)
                logger.info(f"🔍 DEBUG - Serviço adicionado: {ts.service.name} (R$ {ts.price})")
        
        # Converter extras
        extras_with_details = []
        if ticket.extras:
            for te in ticket.extras:
                extra_for_ticket = ExtraForTicket(
                    id=te.extra.id,
                    name=te.extra.name,
                    price=te.extra.price
                )
                extra_with_details = TicketExtraWithDetails(
                    quantity=te.quantity,
                    price=te.price,
                    extra=extra_for_ticket
                )
                extras_with_details.append(extra_with_details)
                logger.info(f"🔍 DEBUG - Extra adicionado: {te.extra.name} x{te.quantity} (R$ {te.price})")
        
        # Criar TicketForPanel
        ticket_for_panel = TicketForPanel(
            id=ticket.id,
            tenant_id=ticket.tenant_id,
            payment_session_id=ticket.payment_session_id,
            ticket_number=ticket.ticket_number,
            status=ticket.status,
            customer_name=ticket.customer_name,
            customer_cpf=ticket.customer_cpf,
            customer_phone=ticket.customer_phone,
            consent_version=ticket.consent_version,
            priority=ticket.priority,
            queue_position=ticket.queue_position,
            estimated_wait_minutes=ticket.estimated_wait_minutes,
            assigned_operator_id=ticket.assigned_operator_id,
            equipment_id=ticket.equipment_id,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            printed_at=ticket.printed_at,
            queued_at=ticket.queued_at,
            called_at=ticket.called_at,
            started_at=ticket.started_at,
            completed_at=ticket.completed_at,
            cancelled_at=ticket.cancelled_at,
            expired_at=ticket.expired_at,
            reprinted_at=ticket.reprinted_at,
            operator_notes=ticket.operator_notes,
            cancellation_reason=ticket.cancellation_reason,
            print_attempts=ticket.print_attempts,
            reactivation_count=ticket.reactivation_count,
            payment_confirmed=ticket.payment_confirmed,
            services=services_with_details,
            extras=extras_with_details
        )
        
        result.append(ticket_for_panel)
        logger.info(f"🔍 DEBUG - Ticket {ticket.id} processado com {len(services_with_details)} serviços e {len(extras_with_details)} extras")
    
    logger.info(f"🔍 DEBUG - Retornando {len(result)} tickets")
    return result

@router.get("/completed", response_model=List[TicketForPanel], tags=["operator"])
async def get_completed_tickets(
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Lista os tickets concluídos pelo operador logado nos últimos 30 minutos."""
    since = datetime.now(timezone.utc) - timedelta(minutes=30)
    return db.query(Ticket).options(
        joinedload(Ticket.services).joinedload(TicketService.service),
        joinedload(Ticket.extras).joinedload(TicketExtra.extra)
    ).filter(
        Ticket.tenant_id == current_operator.tenant_id,
        Ticket.assigned_operator_id == current_operator.id,
        Ticket.status == 'completed',
        Ticket.completed_at >= since
    ).order_by(Ticket.completed_at.desc()).all()


@router.get("", response_model=List[TicketForPanel], tags=["operator"])
async def list_tickets(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Lista tickets com base em filtros. Usado para cancelados, etc."""
    query = db.query(Ticket).options(
        joinedload(Ticket.services).joinedload(TicketService.service),
        joinedload(Ticket.extras).joinedload(TicketExtra.extra)
    ).filter(Ticket.tenant_id == current_operator.tenant_id)

    if status:
        query = query.filter(Ticket.status == status)
    
    if category:
        # Usar a função get_tickets_by_category para obter os status da categoria
        from constants import get_tickets_by_category
        category_statuses = get_tickets_by_category(category)
        if category_statuses:
            query = query.filter(Ticket.status.in_([s.value for s in category_statuses]))

    return query.order_by(Ticket.updated_at.desc()).limit(50).all()

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
    
    # ✅ CORREÇÃO: Logs para debug da fila
    logger.info(f"🔍 DEBUG - Fila carregada: {len(tickets)} tickets para tenant {current_operator.tenant_id}")
    for ticket in tickets:
        logger.info(f"🔍 DEBUG - Ticket {ticket.ticket_number}: status={ticket.status}, services={len(ticket.services) if ticket.services else 0}")
        if ticket.services:
            for ts in ticket.services:
                logger.info(f"🔍 DEBUG -   Serviço: {ts.service.name if ts.service else 'N/A'} (ID: {ts.service_id})")
    
    # Converter para TicketInQueue com informações adicionais
    queue_tickets = []
    for ticket in tickets:
        # Calcular tempo de espera
        waiting_minutes = 0
        if ticket.queued_at:
            waiting_minutes = (datetime.now(timezone.utc) - ticket.queued_at).total_seconds() / 60
        
        # Criar ticket enriquecido (usando dict básico por enquanto)
        data = ticket.__dict__.copy()
        for field in ["service", "waiting_time_minutes", "waiting_status", "priority_info", "estimated_service_time", "services", "extras"]:
            data.pop(field, None)
        
        # Converter serviços para o formato esperado pelo schema
        services_with_details = []
        if ticket.services:
            for ts in ticket.services:
                service_for_ticket = ServiceForTicket(
                    id=ts.service.id,
                    name=ts.service.name,
                    price=ts.service.price
                )
                service_with_details = TicketServiceWithDetails(
                    price=ts.price,
                    service=service_for_ticket
                )
                services_with_details.append(service_with_details)
        
        # Converter extras para o formato esperado pelo schema
        extras_with_details = []
        if ticket.extras:
            for te in ticket.extras:
                extra_for_ticket = ExtraForTicket(
                    id=te.extra.id,
                    name=te.extra.name,
                    price=te.extra.price
                )
                extra_with_details = TicketExtraWithDetails(
                    quantity=te.quantity,
                    price=te.price,
                    extra=extra_for_ticket
                )
                extras_with_details.append(extra_with_details)
        
        # Criar o TicketInQueue com os dados corretos
        queue_ticket = TicketInQueue(
            **data,
            services=services_with_details,
            extras=extras_with_details,
            waiting_time_minutes=waiting_minutes,
            waiting_status="normal",
            priority_info={}
        )
        queue_tickets.append(queue_ticket)
    
    # Agrupar por diferentes critérios
    by_service = {}
    by_status = {}
    by_priority = {}
    
    for ticket in queue_tickets:
        # Por serviço
        service_name = "Sem serviço"
        if ticket.services and len(ticket.services) > 0:
            service_name = ticket.services[0].service.name
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
    
    # ✅ CORREÇÃO: Logs para debug do resultado final
    logger.info(f"🔍 DEBUG - Resultado final da fila:")
    logger.info(f"🔍 DEBUG -   Total de tickets: {len(queue_tickets)}")
    logger.info(f"🔍 DEBUG -   Agrupamento por serviço: {list(by_service.keys())}")
    for service_name, tickets in by_service.items():
        logger.info(f"🔍 DEBUG -     '{service_name}': {len(tickets)} tickets")
    
    return TicketQueue(
        items=queue_tickets,
        total=len(queue_tickets),
        by_service=by_service,
        by_status=by_status,
        by_priority=by_priority,
        queue_stats=queue_stats,
        estimated_total_time=estimated_total_time
    )

@router.get("/queue/public", response_model=TicketQueue, tags=["queue"])
async def get_public_queue(
    tenant_id: UUID,
    include_called: bool = Query(True, description="Incluir tickets já chamados (últimos 5 min)"),
    include_in_progress: bool = Query(True, description="Incluir tickets em atendimento"),
    db: Session = Depends(get_db)
):
    """Retorna a fila pública de tickets para exibição."""
    queue_manager = get_queue_manager(db)
    
    # Usar o método correto do QueueManager
    tickets = queue_manager.get_queue_tickets(
        tenant_id=str(tenant_id),
        sort_order=QueueSortOrder.FIFO,
        include_called=include_called,
        include_in_progress=include_in_progress
    )

    if not tickets:
        return {
            "items": [], "total": 0, "by_service": {}, "by_status": {}, 
            "by_priority": {}, "queue_stats": {}, "estimated_total_time": 0
        }

    # Converter tickets para o formato esperado
    queue_tickets = []
    for ticket in tickets:
        # Calcular tempo de espera
        waiting_minutes = 0
        if ticket.queued_at:
            waiting_minutes = (datetime.now(timezone.utc) - ticket.queued_at).total_seconds() / 60
        
        # Converter serviços para o formato esperado pelo schema
        services_with_details = []
        if ticket.services:
            for ts in ticket.services:
                service_for_ticket = ServiceForTicket(
                    id=ts.service.id,
                    name=ts.service.name,
                    price=ts.service.price
                )
                service_with_details = TicketServiceWithDetails(
                    price=ts.price,
                    service=service_for_ticket
                )
                services_with_details.append(service_with_details)
    
        # Converter extras para o formato esperado pelo schema
        extras_with_details = []
        if ticket.extras:
            for te in ticket.extras:
                extra_for_ticket = ExtraForTicket(
                    id=te.extra.id,
                    name=te.extra.name,
                    price=te.extra.price
                )
                extra_with_details = TicketExtraWithDetails(
                    quantity=te.quantity,
                    price=te.price,
                    extra=extra_for_ticket
                )
                extras_with_details.append(extra_with_details)
        
        # Criar ticket enriquecido
        ticket_data = {
            "id": ticket.id,
            "tenant_id": ticket.tenant_id,
            "ticket_number": ticket.ticket_number,
            "status": ticket.status,
            "priority": ticket.priority,
            "queue_position": ticket.queue_position,
            "estimated_wait_minutes": ticket.estimated_wait_minutes,
            "customer_name": ticket.customer_name,
            "customer_cpf": ticket.customer_cpf,
            "customer_phone": ticket.customer_phone,
            "consent_version": ticket.consent_version,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
            "queued_at": ticket.queued_at,
            "called_at": ticket.called_at,
            "started_at": ticket.started_at,
            "completed_at": ticket.completed_at,
            "cancelled_at": ticket.cancelled_at,
            "expired_at": ticket.expired_at,
            "reprinted_at": ticket.reprinted_at,
            "operator_notes": ticket.operator_notes,
            "cancellation_reason": ticket.cancellation_reason,
            "print_attempts": ticket.print_attempts,
            "reactivation_count": ticket.reactivation_count,
            "payment_confirmed": getattr(ticket, 'payment_confirmed', False),
            "services": services_with_details,
            "extras": extras_with_details,
            "waiting_time_minutes": waiting_minutes,
            "waiting_status": get_waiting_time_status(waiting_minutes),
            "priority_info": {
                "level": ticket.priority,
                "description": PRIORITY_DESCRIPTIONS.get(QueuePriority(ticket.priority), ""),
                "color": PRIORITY_COLORS.get(QueuePriority(ticket.priority), "#000000")
            }
        }
        
        queue_ticket = TicketInQueue(**ticket_data)
        queue_tickets.append(queue_ticket)
    
    # Agrupar por diferentes critérios
    by_service = {}
    by_status = {}
    by_priority = {}
    
    for ticket in queue_tickets:
        # Por serviço
        service_name = "Sem serviço"
        if ticket.services and len(ticket.services) > 0:
            service_name = ticket.services[0].service.name
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
    queue_stats = queue_manager.get_queue_statistics(str(tenant_id))
    
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
    next_ticket.called_at = datetime.now(timezone.utc)
    next_ticket.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(next_ticket)
    # Buscar informações do equipamento se houver
    equipment_name = None
    if next_ticket.equipment_id:
        equipment = db.query(Equipment).filter(Equipment.id == next_ticket.equipment_id).first()
        if equipment:
            equipment_name = equipment.identifier
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

@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: UUID,
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
        
    # Converter serviços associados
    services = []
    if hasattr(ticket, "services") and ticket.services:
        for ts in ticket.services:
            services.append({
                "service_id": ts.service_id,
                "price": float(ts.price)
            })
    
    # Converter extras com nomes
    extras_out = []
    if hasattr(ticket, "extras") and ticket.extras:
        for te in ticket.extras:
            # Buscar o extra para obter o nome
            extra = db.query(Extra).filter(Extra.id == te.extra_id).first()
            extra_name = extra.name if extra else f"Extra {te.extra_id}"
            
            extras_out.append(TicketExtraOut(
                id=te.id, 
                extra_id=te.extra_id, 
                name=extra_name,  # Incluindo o nome do extra
                quantity=te.quantity, 
                price=float(te.price)
            ))
    
    return TicketOut(
        id=ticket.id,
        tenant_id=ticket.tenant_id,
        ticket_number=ticket.ticket_number,
        number=f"#{str(ticket.ticket_number).zfill(3)}",
        status=ticket.status,
        customer_name=ticket.customer_name,
        customer_cpf=ticket.customer_cpf or "",
        customer_phone=ticket.customer_phone or "",
        consent_version=ticket.consent_version,
        services=services,
        extras=extras_out,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        payment_confirmed=getattr(ticket, 'payment_confirmed', False)
    )

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
    logger.info(f"🔍 DEBUG - Chamando ticket {ticket_id} com equipamento {request.equipment_id}")
    
    # Buscar ticket e equipamento
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    equipment = db.query(Equipment).filter(Equipment.id == request.equipment_id).first()
    
    logger.info(f"🔍 DEBUG - Ticket encontrado: {ticket is not None}")
    logger.info(f"🔍 DEBUG - Equipamento encontrado: {equipment is not None}")
    
    if not ticket or not equipment:
        raise HTTPException(status_code=404, detail="Ticket ou equipamento não encontrado")
    
    logger.info(f"🔍 DEBUG - Status atual do ticket: {ticket.status}")
    logger.info(f"🔍 DEBUG - Status atual do equipamento: {equipment.status}")
    
    # Verificar se o ticket já foi chamado
    if ticket.status == TicketStatus.CALLED.value:
        raise HTTPException(
            status_code=400, 
            detail=f"Ticket #{ticket.ticket_number} já foi chamado. Status atual: {ticket.status}"
        )
    
    # Verificar se o ticket está na fila
    if ticket.status != TicketStatus.IN_QUEUE.value:
        raise HTTPException(
            status_code=400, 
            detail=f"Ticket #{ticket.ticket_number} não está na fila. Status atual: {ticket.status}. Apenas tickets com status 'in_queue' podem ser chamados."
        )
    
    # Validação de compatibilidade: o equipamento deve estar associado ao mesmo serviço do ticket
    ticket_service_ids = [str(ts.service_id) for ts in ticket.services]
    if equipment.service_id and str(equipment.service_id) not in ticket_service_ids:
        raise HTTPException(status_code=400, detail="Equipamento selecionado não é compatível com o serviço do ticket.")
    
    # Verifica se o equipamento está disponível
    if equipment.status != EquipmentStatus.online:
        raise HTTPException(status_code=400, detail="Equipamento não está disponível para uso.")
    
    logger.info(f"🔍 DEBUG - Atualizando status do ticket para CALLED")
    
    # Atualizar status do ticket
    status_update = TicketStatusUpdate(
        status=TicketStatus.CALLED,
        operator_notes=f"Chamado pelo operador {current_operator.name}"
    )
    result = await update_ticket_status(ticket_id, status_update, db, current_operator)
    
    logger.info(f"🔍 DEBUG - Status atualizado. Atualizando equipamento e operador")
    
    # Atualizar o equipment_id e operator_id do ticket
    ticket.equipment_id = request.equipment_id
    ticket.assigned_operator_id = current_operator.id
    
    logger.info(f"🔍 DEBUG - Equipment ID: {ticket.equipment_id}")
    logger.info(f"🔍 DEBUG - Operator ID: {ticket.assigned_operator_id}")
    
    # Marcar equipamento como indisponível
    equipment.status = EquipmentStatus.offline
    db.commit()
    db.refresh(ticket)
    db.refresh(equipment)
    
    logger.info(f"🔍 DEBUG - Ticket após commit - Status: {ticket.status}, Equipment: {ticket.equipment_id}, Operator: {ticket.assigned_operator_id}")
    
    # Broadcast de atualização do equipamento
    equipment_update_data = {
        "id": str(equipment.id),
        "identifier": equipment.identifier,
        "status": equipment.status.value,
        "assigned_operator_id": str(current_operator.id),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await websocket_manager.broadcast_equipment_update(str(current_operator.tenant_id), equipment_update_data)
    
    # Buscar informações do equipamento
    equipment_name = None
    if ticket.equipment_id:
        equipment = db.query(Equipment).filter(Equipment.id == ticket.equipment_id).first()
        if equipment:
            equipment_name = equipment.identifier
    
    logger.info(f"🔍 DEBUG - Enviando broadcast de ticket chamado")
    
    # Broadcast específico para displays e operadores
    await websocket_manager.broadcast_ticket_called(
            tenant_id=str(current_operator.tenant_id),
            ticket=ticket,
            operator_name=current_operator.name,
            equipment_name=equipment_name
        )
    
    logger.info(f"🔍 DEBUG - Enviando broadcast de atualização da fila")
    
    # Broadcast de atualização da fila para todos os operadores
    queue_manager = get_queue_manager(db)
    queue_data = queue_manager.get_queue_tickets(str(current_operator.tenant_id))
    await websocket_manager.broadcast_queue_update(str(current_operator.tenant_id), queue_data)
    
    logger.info(f"🔍 DEBUG - Call ticket concluído com sucesso")
    
    return result

@router.post("/{ticket_id}/call-service")
async def call_ticket_service(
    ticket_id: str,
    request: CallServiceRequest,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Chama um serviço específico de um ticket"""
    logger.info(f"🔍 DEBUG - Chamando serviço {request.service_id} do ticket {ticket_id} com equipamento {request.equipment_id}")
    
    # Buscar ticket, serviço e equipamento
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    ticket_service = db.query(TicketService).filter(
        TicketService.ticket_id == ticket_id,
        TicketService.service_id == request.service_id
    ).first()
    equipment = db.query(Equipment).filter(Equipment.id == request.equipment_id).first()
    
    if not ticket or not ticket_service or not equipment:
        raise HTTPException(status_code=404, detail="Ticket, serviço ou equipamento não encontrado")
    
    # Verificar se o ticket está na fila ou já foi chamado
    if ticket.status not in [TicketStatus.IN_QUEUE.value, TicketStatus.CALLED.value]:
        raise HTTPException(
            status_code=400, 
            detail=f"Ticket #{ticket.ticket_number} não está disponível para chamada. Status atual: {ticket.status}"
        )
    
    # Verificar se o equipamento é compatível com o serviço
    if equipment.service_id and str(equipment.service_id) != request.service_id:
        raise HTTPException(status_code=400, detail="Equipamento selecionado não é compatível com o serviço.")
    
    # Verificar se o equipamento está disponível
    if equipment.status != EquipmentStatus.online:
        raise HTTPException(status_code=400, detail="Equipamento não está disponível para uso.")
    
    # Buscar ou criar progresso do serviço
    progress = db.query(TicketServiceProgress).filter(
        TicketServiceProgress.ticket_service_id == ticket_service.id
    ).first()
    
    if not progress:
        # Criar progresso automaticamente
        service = db.query(Service).filter(Service.id == request.service_id).first()
        progress = TicketServiceProgress(
            ticket_service_id=ticket_service.id,
            status="pending",
            duration_minutes=service.duration_minutes if service else 10
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    # Verificar se o serviço já foi iniciado
    if progress.status == "in_progress":
        raise HTTPException(status_code=400, detail="Este serviço já está em andamento.")
    
    if progress.status == "completed":
        raise HTTPException(status_code=400, detail="Este serviço já foi concluído.")
    
    # Se o ticket não foi chamado ainda, chamá-lo primeiro
    if ticket.status == TicketStatus.IN_QUEUE.value:
        logger.info(f"🔍 DEBUG - Chamando ticket completo primeiro")
        status_update = TicketStatusUpdate(
            status=TicketStatus.CALLED,
            operator_notes=f"Chamado pelo operador {current_operator.name} para serviço específico"
        )
        await update_ticket_status(ticket_id, status_update, db, current_operator)
        
        # Atualizar o equipment_id e operator_id do ticket
        ticket.equipment_id = request.equipment_id
        ticket.assigned_operator_id = current_operator.id
    
    # Iniciar o serviço específico
    logger.info(f"🔍 DEBUG - Iniciando serviço específico")
    progress.status = "in_progress"
    progress.started_at = datetime.now(timezone.utc)
    progress.equipment_id = request.equipment_id
    progress.operator_notes = f"Iniciado pelo operador {current_operator.name}"
    
    # Marcar equipamento como indisponível
    equipment.status = EquipmentStatus.offline
    
    db.commit()
    db.refresh(progress)
    db.refresh(equipment)
    
    # Buscar informações do serviço
    service = db.query(Service).filter(Service.id == request.service_id).first()
    service_name = service.name if service else "Serviço"
    
    # Broadcast de atualização do equipamento
    equipment_update_data = {
        "id": str(equipment.id),
        "identifier": equipment.identifier,
        "status": equipment.status.value,
        "assigned_operator_id": str(current_operator.id),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await websocket_manager.broadcast_equipment_update(str(current_operator.tenant_id), equipment_update_data)
    
    # Broadcast de atualização da fila
    queue_manager = get_queue_manager(db)
    queue_data = queue_manager.get_queue_tickets(str(current_operator.tenant_id))
    await websocket_manager.broadcast_queue_update(str(current_operator.tenant_id), queue_data)
    
    logger.info(f"🔍 DEBUG - Serviço {service_name} iniciado com sucesso")
    
    return {
        "message": f"Serviço {service_name} iniciado para ticket #{ticket.ticket_number}",
        "ticket_id": ticket_id,
        "service_id": request.service_id,
        "service_name": service_name,
        "equipment_id": request.equipment_id,
        "progress_id": str(progress.id)
    }

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
        
        # Broadcast de atualização do equipamento
        equipment_update_data = {
            "id": str(equipment.id),
            "identifier": equipment.identifier,
            "status": equipment.status.value,
            "assigned_operator_id": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await websocket_manager.broadcast_equipment_update(str(current_operator.tenant_id), equipment_update_data)
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
    
    # Restaurar estoque dos extras se o ticket foi cancelado
    if ticket and ticket.extras:
        for ticket_extra in ticket.extras:
            # Restaurar estoque na tabela extras
            extra_model = db.query(Extra).filter(Extra.id == ticket_extra.extra_id).first()
            if extra_model:
                extra_model.stock += ticket_extra.quantity
                logger.info(f"🔍 DEBUG - Restaurando estoque do extra {extra_model.name}: {extra_model.stock - ticket_extra.quantity} -> {extra_model.stock}")
            
            # Restaurar estoque na tabela operation_config_extras
            operation_config_extra = db.query(OperationConfigExtra).filter(
                OperationConfigExtra.extra_id == ticket_extra.extra_id
            ).first()
            if operation_config_extra:
                operation_config_extra.stock += ticket_extra.quantity
                logger.info(f"🔍 DEBUG - Restaurando estoque na config do extra {ticket_extra.extra_id}: {operation_config_extra.stock - ticket_extra.quantity} -> {operation_config_extra.stock}")
        
        db.commit()
    
    # Liberar equipamento
    if equipment:
        equipment.status = EquipmentStatus.online
        db.commit()
        db.refresh(equipment)
        
        # Broadcast de atualização do equipamento
        equipment_update_data = {
            "id": str(equipment.id),
            "identifier": equipment.identifier,
            "status": equipment.status.value,
            "assigned_operator_id": None,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await websocket_manager.broadcast_equipment_update(str(current_operator.tenant_id), equipment_update_data)
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

@router.post("", response_model=TicketOut)
async def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db)
):
    # Debug: Log dos dados recebidos
    logger.info(f"🔍 DEBUG - Criando ticket com dados: {ticket_in}")
    logger.info(f"🔍 DEBUG - Services: {ticket_in.services}")
    logger.info(f"🔍 DEBUG - Extras: {ticket_in.extras}")
    logger.info(f"🔍 DEBUG - Signature: {ticket_in.signature is not None}")
    # Get next ticket number for this tenant
    last_ticket = db.query(Ticket).filter(
        Ticket.tenant_id == ticket_in.tenant_id
    ).order_by(Ticket.ticket_number.desc()).first()
    
    ticket_number = 1 if not last_ticket else last_ticket.ticket_number + 1
    
    # Create ticket with PENDING_PAYMENT status (aguardando confirmação de pagamento)
    ticket = Ticket(
        tenant_id=ticket_in.tenant_id,
        payment_session_id=None,  # Não há payment session neste fluxo
        ticket_number=ticket_number,
        status=TicketStatus.PENDING_PAYMENT.value,  # Novo status inicial
        customer_name=ticket_in.customer_name,
        customer_cpf=ticket_in.customer_cpf,
        customer_phone=ticket_in.customer_phone,
        consent_version=ticket_in.consent_version,
        print_attempts=0
    )
    db.add(ticket)
    db.flush()  # para garantir que ticket.id está disponível

    # SALVAR ASSINATURA NA TABELA CONSENT (se fornecida)
    if ticket_in.signature:
        logger.info(f"🔍 DEBUG - Salvando assinatura para ticket {ticket.id}")
        
        # Criar um PaymentSession temporário para vincular o consentimento
        # (já que Consent precisa de payment_session_id)
        # Pegar o service_id do primeiro serviço do ticket
        service_id = ticket_in.services[0].service_id if ticket_in.services else None
        
        if not service_id:
            raise HTTPException(
                status_code=400, 
                detail="Ticket deve ter pelo menos um serviço para criar payment session"
            )
        
        temp_payment_session = PaymentSession(
            tenant_id=ticket_in.tenant_id,
            service_id=service_id,  # Usar o service_id do primeiro serviço
            customer_name=ticket_in.customer_name,
            customer_cpf=ticket_in.customer_cpf,
            customer_phone=ticket_in.customer_phone,
            consent_version=ticket_in.consent_version,
            payment_method="none",  # Temporário
            amount=0.0,  # Será atualizado quando o pagamento for criado
            status="pending",
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(temp_payment_session)
        db.flush()  # para garantir que temp_payment_session.id está disponível
        
        # Criar o consentimento
        consent = Consent(
            tenant_id=ticket_in.tenant_id,
            payment_session_id=temp_payment_session.id,
            version=ticket_in.consent_version,
            signature=ticket_in.signature,
            ip_address=None,  # Pode ser adicionado se necessário
            user_agent=None   # Pode ser adicionado se necessário
        )
        db.add(consent)
        
        # Vincular o ticket ao payment session temporário
        ticket.payment_session_id = temp_payment_session.id
        
        logger.info(f"✅ Assinatura salva com sucesso para ticket {ticket.id}")

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
    
    # Decrementar estoque dos extras
    logger.info(f"🔍 DEBUG - Iniciando decremento de estoque para {len(ticket_in.extras)} extras")
    for extra_item in ticket_in.extras:
        logger.info(f"🔍 DEBUG - Processando extra: {extra_item.extra_id}, quantidade: {extra_item.quantity}")
        
        # Decrementar estoque na tabela extras
        extra_model = db.query(Extra).filter(Extra.id == extra_item.extra_id).first()
        if extra_model:
            old_stock = extra_model.stock
            extra_model.stock = max(0, extra_model.stock - extra_item.quantity)
            logger.info(f"🔍 DEBUG - Decrementando estoque do extra {extra_model.name}: {old_stock} -> {extra_model.stock}")
        else:
            logger.warning(f"⚠️ WARNING - Extra não encontrado na tabela extras: {extra_item.extra_id}")
        
        # Decrementar estoque na tabela operation_config_extras
        operation_config_extra = db.query(OperationConfigExtra).filter(
            OperationConfigExtra.extra_id == extra_item.extra_id
        ).first()
        if operation_config_extra:
            old_config_stock = operation_config_extra.stock
            operation_config_extra.stock = max(0, operation_config_extra.stock - extra_item.quantity)
            logger.info(f"🔍 DEBUG - Decrementando estoque na config do extra {extra_item.extra_id}: {old_config_stock} -> {operation_config_extra.stock}")
        else:
            logger.warning(f"⚠️ WARNING - Extra não encontrado na tabela operation_config_extras: {extra_item.extra_id}")
    
    logger.info(f"🔍 DEBUG - Commit das alterações de estoque")
    db.commit()

    # Broadcast da atualização da fila para todos os clientes
    try:
        await websocket_manager.broadcast_queue_update(str(ticket.tenant_id), {
            "type": "queue_update",
            "data": {
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "customer_name": ticket.customer_name,
                "action": "created"
            }
        })
        logger.info(f"🔍 DEBUG - Broadcast de ticket criado enviado para tenant {ticket.tenant_id}")
    except Exception as e:
        logger.error(f"❌ ERRO ao enviar broadcast de ticket criado: {e}")
    
    # Converter extras para schema de saída
    extras_out = []
    for te in ticket.extras:
        # Buscar o extra para obter o nome
        extra = db.query(Extra).filter(Extra.id == te.extra_id).first()
        extra_name = extra.name if extra else f"Extra {te.extra_id}"
        
        extras_out.append(TicketExtraOut(
            id=te.id,
            extra_id=te.extra_id,
            quantity=te.quantity,
            price=te.price
        ))
    
    # Converter serviços para schema de saída
    services_out = []
    for ts in ticket.services:
        services_out.append(TicketServiceItem(
            service_id=ts.service_id,
            price=ts.price
        ))
    
    # Debug: Log dos dados antes de criar TicketOut
    logger.info(f"🔍 DEBUG - Criando TicketOut com dados:")
    logger.info(f"🔍 DEBUG - customer_cpf: {ticket.customer_cpf} (tipo: {type(ticket.customer_cpf)})")
    logger.info(f"🔍 DEBUG - customer_phone: {ticket.customer_phone} (tipo: {type(ticket.customer_phone)})")
    
    return TicketOut(
        id=ticket.id,
        tenant_id=ticket.tenant_id,
        ticket_number=ticket.ticket_number,
        status=ticket.status,
        customer_name=ticket.customer_name,
        customer_cpf=ticket.customer_cpf,
        customer_phone=ticket.customer_phone,
        consent_version=ticket.consent_version,
        services=services_out,
        extras=extras_out,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        payment_confirmed=False
    ) 

@router.post("/{ticket_id}/create-payment", response_model=PaymentSessionWithQR, tags=["payments"])
async def create_payment_for_ticket(
    ticket_id: UUID,
    payload: PaymentForTicket,
    db: Session = Depends(get_db)
):
    """Cria uma sessão de pagamento para um ticket existente."""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")

    # Calcular o valor total a partir dos serviços e extras do ticket
    total_amount = sum(s.price for s in ticket.services) + sum(e.price * e.quantity for e in ticket.extras)

    # Pegar o service_id do primeiro serviço do ticket
    service_id = ticket.services[0].service_id if ticket.services else None

    # Criar a sessão de pagamento
    payment_session = PaymentSession(
        tenant_id=ticket.tenant_id,
        service_id=service_id,
        ticket_id=ticket.id,
        customer_name=ticket.customer_name,
        customer_cpf=ticket.customer_cpf,
        customer_phone=ticket.customer_phone,
        consent_version=ticket.consent_version,
        payment_method=payload.payment_method,
        amount=total_amount,
        status="pending",
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(payment_session)
    db.commit()
    db.refresh(payment_session)

    # Integrar com Mercado Pago se o método for mercadopago
    preference_id = None
    qr_code = None
    
    if payload.payment_method == "mercadopago":
        try:
            logger.info(f"🔍 DEBUG - Iniciando criação de preferência Mercado Pago para ticket {ticket_id}")
            
            # Buscar configuração do Mercado Pago da tabela operation_config
            operation_config = db.query(OperationConfig).filter(OperationConfig.tenant_id == ticket.tenant_id).first()
            logger.info(f"🔍 DEBUG - OperationConfig encontrado: {operation_config is not None}")
            
            if not operation_config or not operation_config.payment_config:
                logger.error(f"❌ Configuração de pagamento não encontrada para tenant {ticket.tenant_id}")
                raise HTTPException(status_code=400, detail="Configuração de pagamento não encontrada")
            
            logger.info(f"🔍 DEBUG - Payment config: {operation_config.payment_config}")
            
            mercadopago_config = operation_config.payment_config.get("mercado_pago", {})
            logger.info(f"🔍 DEBUG - MercadoPago config: {mercadopago_config}")
            
            if not mercadopago_config.get("access_token"):
                logger.error(f"❌ Token de acesso do Mercado Pago não configurado")
                raise HTTPException(status_code=400, detail="Token de acesso do Mercado Pago não configurado")
            
            # Importar e usar o adaptador do Mercado Pago
            from services.payment.adapters.mercadopago import MercadoPagoAdapter
            
            adapter = MercadoPagoAdapter(mercadopago_config)
            logger.info(f"🔍 DEBUG - MercadoPagoAdapter criado com sucesso")
            
            # Preparar metadados para a preferência
            metadata = {
                "payment_session_id": str(payment_session.id),
                "ticket_id": str(ticket.id),
                "service_id": str(service_id),
                "customer_name": ticket.customer_name,
                "customer_cpf": ticket.customer_cpf,
                "customer_phone": ticket.customer_phone,
                "service_description": "Serviço de Recuperação",
                "redirect_url_base": mercadopago_config.get("redirect_url_base", "http://localhost:5173")
            }
            
            logger.info(f"🔍 DEBUG - Criando preferência com metadados: {metadata}")
            
            # Criar preferência no Mercado Pago
            preference_result = await adapter.create_payment_preference(
                amount=float(total_amount),
                description=f"Serviço - {ticket.services[0].service.name if ticket.services else 'Serviço'}",
                metadata=metadata
            )
            
            preference_id = preference_result.get("preference_id")
            logger.info(f"🔍 DEBUG - Preferência criada: {preference_id}")
            
            # Atualizar a sessão com o preference_id
            payment_session.transaction_id = preference_id
            db.commit()
            
            logger.info(f"✅ Preferência Mercado Pago criada: {preference_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar preferência Mercado Pago: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            # Não falhar completamente, apenas logar o erro
            preference_id = None
    
    elif payload.payment_method == "pix":
        # Simular QR code para PIX em desenvolvimento
        qr_code = f"PIX_QR_CODE_FOR_SESSION_{payment_session.id}"

    return PaymentSessionWithQR(
        id=payment_session.id,
        tenant_id=payment_session.tenant_id,
        service_id=payment_session.service_id,
        ticket_id=payment_session.ticket_id,
        customer_name=payment_session.customer_name,
        customer_cpf=payment_session.customer_cpf,
        customer_phone=payment_session.customer_phone,
        consent_version=payment_session.consent_version,
        payment_method=payment_session.payment_method,
        status=payment_session.status,
        amount=payment_session.amount,
        transaction_id=payment_session.transaction_id,
        payment_link=payment_session.payment_link,
        webhook_data=payment_session.webhook_data,
        expires_at=payment_session.expires_at,
        created_at=payment_session.created_at,
        updated_at=payment_session.updated_at,
        completed_at=payment_session.completed_at,
        qr_code=qr_code,
        preference_id=preference_id
    ) 

@router.post("/{ticket_id}/confirm-payment")
async def confirm_payment(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Confirma manualmente o pagamento de um ticket (uso de maquininha física)."""
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_operator.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")

    # Verificar se o ticket está no status correto
    if ticket.status != TicketStatus.PENDING_PAYMENT.value:
        raise HTTPException(
            status_code=400, 
            detail=f"Ticket deve ter status 'pending_payment', atual: {ticket.status}"
        )

    # Já confirmado?
    if ticket.payment_confirmed:
        return {"status": "already_confirmed"}

    # Confirmar pagamento e mover para fila
    ticket.payment_confirmed = True
    ticket.status = TicketStatus.IN_QUEUE.value
    ticket.queued_at = datetime.now(timezone.utc)
    ticket.updated_at = datetime.now(timezone.utc)
    
    # ✅ CORREÇÃO: Garantir que o ticket tenha serviços associados na tabela ticket_services
    if not ticket.services:
        # Buscar os serviços do payment_session se disponível
        service_ids = []
        if ticket.payment_session_id:
            payment_session = db.query(PaymentSession).filter(PaymentSession.id == ticket.payment_session_id).first()
            if payment_session:
                service_ids.append(payment_session.service_id)
        
        # Se não encontrou service_ids, usar serviços padrão do tenant
        if not service_ids:
            default_services = db.query(Service).filter(
                Service.tenant_id == ticket.tenant_id,
                Service.is_active == True
            ).limit(3).all()  # Limitar a 3 serviços padrão
            service_ids = [s.id for s in default_services]
        
        # Criar associações na tabela ticket_services para múltiplos serviços
        for service_id in service_ids:
            ticket_service = TicketService(
                ticket_id=ticket.id,
                service_id=service_id,
                price=0.0  # Valor será atualizado quando necessário
            )
            db.add(ticket_service)
            logger.info(f"🔍 DEBUG - Criada associação ticket_service para ticket {ticket.id} com service_id {service_id}")
        
        logger.info(f"🔍 DEBUG - Total de {len(service_ids)} serviços associados ao ticket {ticket.id}")
    
    db.commit()

    logger.info(f"🎯 Ticket #{ticket.ticket_number} pagamento confirmado e movido para fila")

    # ✅ CORREÇÃO: Enviar update pelo websocket com estrutura correta
    try:
        await websocket_manager.broadcast_to_tenant(str(ticket.tenant_id), {
            "type": "payment_update",
            "data": {
                "id": str(ticket.id),
                "ticket_id": str(ticket.id),
                "payment_confirmed": True,
                "status": "in_queue",
                "ticket_number": ticket.ticket_number,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        })
        logger.info(f"🔍 DEBUG - Broadcast de confirmação de pagamento enviado para tenant {ticket.tenant_id}")
    except Exception as e:
        logger.error(f"❌ ERRO ao enviar broadcast de confirmação de pagamento: {e}")

    return {
        "status": "confirmed",
        "message": f"Ticket #{ticket.ticket_number} pagamento confirmado e movido para fila",
        "new_status": ticket.status
    }


@router.post("/{ticket_id}/move-to-queue")
async def move_ticket_to_queue(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_operator = Depends(get_current_operator)
):
    """Move um ticket de 'paid' para 'in_queue' para que apareça na fila do operador."""
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_operator.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    if ticket.status != TicketStatus.PAID.value:
        raise HTTPException(
            status_code=400, 
            detail=f"Ticket deve ter status 'paid', atual: {ticket.status}"
        )
    
    # Mover para in_queue
    ticket.status = TicketStatus.IN_QUEUE.value
    ticket.queued_at = datetime.now(timezone.utc)
    ticket.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    logger.info(f"🎯 Ticket #{ticket.ticket_number} movido para fila (paid -> in_queue)")
    
    return {
        "status": "success",
        "message": f"Ticket #{ticket.ticket_number} movido para fila",
        "ticket_id": str(ticket.id),
        "new_status": ticket.status
    } 



@router.get("/status/pending-payment", response_model=List[TicketForPanel], tags=["operator"])
async def get_pending_payment_tickets(
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Retorna tickets aguardando confirmação de pagamento"""
    
    tickets = db.query(Ticket).options(
        joinedload(Ticket.services).joinedload(TicketService.service),
        joinedload(Ticket.extras).joinedload(TicketExtra.extra)
    ).filter(
        Ticket.tenant_id == current_operator.tenant_id,
        Ticket.status == TicketStatus.PENDING_PAYMENT.value
    ).order_by(Ticket.created_at.desc()).all()
    
    return tickets 