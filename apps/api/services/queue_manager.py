# 🎯 Gerenciador Avançado de Fila de Tickets

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import Ticket, Service, Operator, TicketService
from constants import (
    TicketStatus, QueuePriority, QueueSortOrder, 
    QUEUE_CONFIG, QUEUE_TIMINGS, calculate_priority, get_waiting_time_status
)
import logging

logger = logging.getLogger(__name__)

class QueueManager:
    """Gerenciador avançado da fila de tickets"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_queue_tickets(
        self, 
        tenant_id: str,
        sort_order: QueueSortOrder = QueueSortOrder.FIFO,
        service_id: Optional[str] = None,
        priority_filter: Optional[QueuePriority] = None,
        include_called: bool = True,
        include_in_progress: bool = True,
        include_paid: bool = False
    ) -> List[Ticket]:
        """Retorna tickets da fila com ordenação e filtros"""
        
        # Estados base da fila - apenas tickets que já foram processados
        queue_statuses = [TicketStatus.IN_QUEUE.value]
        
        # Incluir 'paid' apenas se especificado
        if include_paid:
            queue_statuses.append(TicketStatus.PAID.value)
        
        if include_called:
            queue_statuses.append(TicketStatus.CALLED.value)
        
        if include_in_progress:
            queue_statuses.append(TicketStatus.IN_PROGRESS.value)
        
        # Query base
        query = self.db.query(Ticket)\
            .join(TicketService, TicketService.ticket_id == Ticket.id)\
            .join(Service, Service.id == TicketService.service_id)\
            .filter(
            Ticket.tenant_id == tenant_id,
            Ticket.status.in_(queue_statuses)
        )
        
        # Filtros opcionais
        if service_id:
            query = query.filter(TicketService.service_id == service_id)
        
        if priority_filter:
            query = query.filter(Ticket.priority == priority_filter.value)
        
        # Aplicar ordenação
        query = self._apply_sort_order(query, sort_order)
        
        tickets = query.all()
        
        # Atualizar prioridades e posições
        self._update_queue_priorities(tickets)
        self._update_queue_positions(tickets, sort_order)
        
        return tickets
    
    def _apply_sort_order(self, query, sort_order: QueueSortOrder):
        """Aplica ordenação à query"""
        
        if sort_order == QueueSortOrder.FIFO:
            # First In, First Out - por ordem de chegada na fila
            return query.order_by(Ticket.queued_at.asc())
        
        elif sort_order == QueueSortOrder.PRIORITY:
            # Por prioridade (high -> normal -> low) e depois FIFO
            priority_order = {
                QueuePriority.HIGH.value: 1,
                QueuePriority.NORMAL.value: 2,
                QueuePriority.LOW.value: 3
            }
            return query.order_by(
                Ticket.priority.asc(),  # Assumindo que high=1, normal=2, low=3
                Ticket.queued_at.asc()
            )
        
        elif sort_order == QueueSortOrder.SERVICE:
            # Por tipo de serviço e depois FIFO
            return query.order_by(
                Service.name.asc(),
                Ticket.queued_at.asc()
            )
        
        elif sort_order == QueueSortOrder.WAITING_TIME:
            # Por tempo de espera (mais antigos primeiro)
            return query.order_by(Ticket.queued_at.asc())
        
        else:
            # Default: FIFO
            return query.order_by(Ticket.queued_at.asc())
    
    def _update_queue_priorities(self, tickets: List[Ticket]):
        """Atualiza prioridades dos tickets baseado em regras"""
        
        for ticket in tickets:
            if not ticket.queued_at:
                continue
            
            # Calcular tempo de espera
            waiting_minutes = (datetime.now(timezone.utc) - ticket.queued_at).total_seconds() / 60
            
            # Calcular nova prioridade
            new_priority = calculate_priority(
                TicketStatus(ticket.status),
                waiting_minutes,
                ticket.print_attempts
            )
            
            # Atualizar se mudou
            if ticket.priority != new_priority.value:
                logger.info(f"🔄 Updating priority for ticket #{ticket.ticket_number}: {ticket.priority} → {new_priority.value}")
                ticket.priority = new_priority.value
                self.db.commit()
    
    def _update_queue_positions(self, tickets: List[Ticket], sort_order: QueueSortOrder):
        """Atualiza posições na fila e estimativas de tempo"""
        
        # Separar por status para cálculo correto
        in_queue_tickets = [t for t in tickets if t.status == TicketStatus.IN_QUEUE.value]
        called_tickets = [t for t in tickets if t.status == TicketStatus.CALLED.value]
        in_progress_tickets = [t for t in tickets if t.status == TicketStatus.IN_PROGRESS.value]
        
        # Atualizar posições para tickets na fila
        for position, ticket in enumerate(in_queue_tickets, 1):
            ticket.queue_position = position
            
            # Calcular tempo estimado de espera
            service = ticket.services[0].service if ticket.services else None
            estimated_wait = self._calculate_estimated_wait_time(
                position, service, in_progress_tickets
            )
            ticket.estimated_wait_minutes = estimated_wait
        
        # Tickets chamados têm posição 0 (próximos)
        for ticket in called_tickets:
            ticket.queue_position = 0
            ticket.estimated_wait_minutes = 0
        
        # Tickets em progresso não têm posição na fila
        for ticket in in_progress_tickets:
            ticket.queue_position = None
            ticket.estimated_wait_minutes = None
    
    def _calculate_estimated_wait_time(
        self, 
        position: int, 
        service: Service, 
        in_progress_tickets: List[Ticket]
    ) -> int:
        """Calcula tempo estimado de espera"""
        
        # Tempo base do serviço
        service_duration = QUEUE_TIMINGS["service_duration"].get(
            service.name.lower().replace(" ", "_"),
            QUEUE_TIMINGS["service_duration"]["default"]
        )
        
        # Contar quantos tickets do mesmo serviço estão em progresso
        same_service_in_progress = len([
            t for t in in_progress_tickets 
            if t.service_id == service.id
        ])
        
        # Calcular tempo baseado na posição e capacidade do serviço
        parallel_capacity = min(service.equipment_count, QUEUE_CONFIG["service_parallel_limit"])
        
        # Posições à frente que precisam ser atendidas
        positions_ahead = max(0, position - 1)
        
        # Tempo estimado considerando capacidade paralela
        estimated_minutes = (positions_ahead // parallel_capacity) * service_duration
        
        # Adicionar tempo dos que já estão em progresso
        if same_service_in_progress > 0:
            estimated_minutes += service_duration // 2  # Assumir que estão na metade
        
        return max(1, estimated_minutes)  # Mínimo 1 minuto
    
    def get_queue_statistics(self, tenant_id: str) -> Dict:
        """Retorna estatísticas detalhadas da fila"""
        
        # Buscar todos os tickets ativos
        active_tickets = self.db.query(Ticket).filter(
            Ticket.tenant_id == tenant_id,
            Ticket.status.in_([
                TicketStatus.IN_QUEUE.value,
                TicketStatus.CALLED.value,
                TicketStatus.IN_PROGRESS.value
            ])
        ).all()
        
        # Estatísticas por status
        by_status = {}
        for status in [TicketStatus.IN_QUEUE, TicketStatus.CALLED, TicketStatus.IN_PROGRESS]:
            count = len([t for t in active_tickets if t.status == status.value])
            by_status[status.value] = count
        
        # Estatísticas por prioridade
        by_priority = {}
        for priority in QueuePriority:
            count = len([t for t in active_tickets if t.priority == priority.value])
            by_priority[priority.value] = count
        
        # Estatísticas por serviço
        by_service = {}
        for ticket in active_tickets:
            # Obter nome do serviço através da relação TicketService
            service_name = "Sem serviço"
            if ticket.services:
                service = ticket.services[0].service
                if service:
                    service_name = service.name
            
            if service_name not in by_service:
                by_service[service_name] = {
                    "total": 0,
                    "in_queue": 0,
                    "called": 0,
                    "in_progress": 0
                }
            
            by_service[service_name]["total"] += 1
            by_service[service_name][ticket.status] += 1
        
        # Tempos de espera
        waiting_times = []
        for ticket in active_tickets:
            if ticket.queued_at and ticket.status == TicketStatus.IN_QUEUE.value:
                waiting_minutes = (datetime.now(timezone.utc) - ticket.queued_at).total_seconds() / 60
                waiting_times.append(waiting_minutes)
        
        avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
        max_waiting_time = max(waiting_times) if waiting_times else 0
        
        # Tempo total estimado da fila
        estimated_total_time = sum([
            t.estimated_wait_minutes or 0 
            for t in active_tickets 
            if t.status == TicketStatus.IN_QUEUE.value
        ])
        
        return {
            "total_active": len(active_tickets),
            "by_status": by_status,
            "by_priority": by_priority,
            "by_service": by_service,
            "waiting_times": {
                "average_minutes": round(avg_waiting_time, 1),
                "maximum_minutes": round(max_waiting_time, 1),
                "total_estimated_minutes": estimated_total_time
            },
            "queue_health": self._assess_queue_health(active_tickets, avg_waiting_time)
        }
    
    def _assess_queue_health(self, active_tickets: List[Ticket], avg_waiting_time: float) -> Dict:
        """Avalia a saúde da fila"""
        
        # Contar tickets com problemas
        critical_tickets = len([
            t for t in active_tickets 
            if t.priority == QueuePriority.HIGH.value
        ])
        
        long_waiting_tickets = len([
            t for t in active_tickets 
            if t.queued_at and 
            (datetime.now(timezone.utc) - t.queued_at).total_seconds() / 60 > QUEUE_TIMINGS["critical_waiting"]
        ])
        
        # Determinar status da fila
        if avg_waiting_time <= QUEUE_TIMINGS["normal_waiting"] and critical_tickets == 0:
            status = "healthy"
            message = "Fila funcionando normalmente"
        elif avg_waiting_time <= QUEUE_TIMINGS["warning_waiting"] and critical_tickets <= 2:
            status = "warning"
            message = "Fila com tempo de espera elevado"
        else:
            status = "critical"
            message = "Fila com problemas críticos"
        
        return {
            "status": status,
            "message": message,
            "critical_tickets": critical_tickets,
            "long_waiting_tickets": long_waiting_tickets,
            "recommendations": self._get_queue_recommendations(status, critical_tickets, long_waiting_tickets)
        }
    
    def _get_queue_recommendations(self, status: str, critical_tickets: int, long_waiting_tickets: int) -> List[str]:
        """Retorna recomendações para melhorar a fila"""
        
        recommendations = []
        
        if status == "critical":
            recommendations.append("🚨 Ação imediata necessária")
            
        if critical_tickets > 0:
            recommendations.append(f"⚠️ {critical_tickets} tickets com alta prioridade")
            
        if long_waiting_tickets > 0:
            recommendations.append(f"⏰ {long_waiting_tickets} tickets esperando há muito tempo")
            
        if status == "warning":
            recommendations.append("📈 Considere adicionar mais operadores")
            
        if not recommendations:
            recommendations.append("✅ Fila funcionando bem")
            
        return recommendations
    
    def get_next_ticket_for_operator(self, tenant_id: str, operator_id: str) -> Optional[Ticket]:
        """Retorna o próximo ticket para um operador específico"""
        
        # Verificar se operador já tem tickets atribuídos
        current_tickets = self.db.query(Ticket).filter(
            Ticket.tenant_id == tenant_id,
            Ticket.assigned_operator_id == operator_id,
            Ticket.status.in_([TicketStatus.CALLED.value, TicketStatus.IN_PROGRESS.value])
        ).count()
        
        # Verificar limite de tickets por operador
        if current_tickets >= QUEUE_CONFIG["operator_concurrent_limit"]:
            return None
        
        # Buscar próximo ticket na fila (prioridade + FIFO)
        next_ticket = self.db.query(Ticket).filter(
            Ticket.tenant_id == tenant_id,
            Ticket.status == TicketStatus.IN_QUEUE.value,
            Ticket.assigned_operator_id.is_(None)
        ).order_by(
            Ticket.priority.asc(),  # Alta prioridade primeiro
            Ticket.queued_at.asc()  # Depois FIFO
        ).first()
        
        return next_ticket
    
    def assign_ticket_to_operator(self, ticket_id: str, operator_id: str) -> bool:
        """Atribui um ticket a um operador"""
        
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return False
        
        ticket.assigned_operator_id = operator_id
        self.db.commit()
        
        logger.info(f"🎯 Ticket #{ticket.ticket_number} assigned to operator {operator_id}")
        return True
    
    def auto_expire_old_tickets(self, tenant_id: str) -> int:
        """Expira automaticamente tickets muito antigos"""
        
        if not QUEUE_CONFIG["auto_expire_enabled"]:
            return 0
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=QUEUE_TIMINGS["auto_expire"])
        
        old_tickets = self.db.query(Ticket).filter(
            Ticket.tenant_id == tenant_id,
            Ticket.status == TicketStatus.IN_QUEUE.value,
            Ticket.queued_at < cutoff_time
        ).all()
        
        expired_count = 0
        for ticket in old_tickets:
            ticket.status = TicketStatus.EXPIRED.value
            ticket.expired_at = datetime.now(timezone.utc)
            expired_count += 1
            
            logger.warning(f"⏰ Auto-expired ticket #{ticket.ticket_number} after {QUEUE_TIMINGS['auto_expire']} minutes")
        
        if expired_count > 0:
            self.db.commit()
        
        return expired_count

# Instância global do gerenciador de fila
def get_queue_manager(db: Session) -> QueueManager:
    """Factory function para obter instância do QueueManager"""
    return QueueManager(db) 