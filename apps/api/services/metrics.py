from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import Ticket, PaymentSession as Payment, Service
from prometheus_client import Counter, Histogram, Gauge
import logging

logger = logging.getLogger(__name__)

# Métricas Prometheus
TICKET_CREATED = Counter(
    'totem_ticket_created_total',
    'Total number of tickets created',
    ['service_id', 'status']
)

TICKET_COMPLETED = Counter(
    'totem_ticket_completed_total',
    'Total number of tickets completed',
    ['service_id']
)

TICKET_WAIT_TIME = Histogram(
    'totem_ticket_wait_time_seconds',
    'Time spent waiting for service',
    ['service_id'],
    buckets=[60, 300, 600, 900, 1200, 1800, 3600]
)

PAYMENT_PROCESSED = Counter(
    'totem_payment_processed_total',
    'Total number of payments processed',
    ['status', 'payment_method']
)

PAYMENT_AMOUNT = Counter(
    'totem_payment_amount_total',
    'Total amount of payments processed',
    ['status', 'payment_method']
)

PAYMENT_PROCESSING_TIME = Histogram(
    'totem_payment_processing_time_seconds',
    'Time spent processing payments',
    ['payment_method'],
    buckets=[1, 5, 10, 30, 60, 120]
)

QUEUE_LENGTH = Gauge(
    'totem_queue_length',
    'Current length of the queue',
    ['service_id']
)

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    async def get_daily_metrics(self, tenant_id: str, date: datetime = None) -> Dict[str, Any]:
        """Obtém métricas diárias para um tenant"""
        if date is None:
            date = datetime.utcnow()

        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        try:
            # Métricas de tickets
            tickets = self.db.query(Ticket).filter(
                and_(
                    Ticket.tenant_id == tenant_id,
                    Ticket.created_at >= start_date,
                    Ticket.created_at < end_date
                )
            ).all()

            # Métricas de pagamentos
            payments = self.db.query(Payment).filter(
                and_(
                    Payment.tenant_id == tenant_id,
                    Payment.created_at >= start_date,
                    Payment.created_at < end_date
                )
            ).all()

            # Agrupa tickets por serviço
            service_metrics = {}
            for ticket in tickets:
                if ticket.service_id not in service_metrics:
                    service_metrics[ticket.service_id] = {
                        "total": 0,
                        "paid": 0,
                        "called": 0,
                        "cancelled": 0
                    }
                service_metrics[ticket.service_id]["total"] += 1
                service_metrics[ticket.service_id][ticket.status] += 1

                # Atualiza métricas Prometheus
                TICKET_CREATED.labels(
                    service_id=str(ticket.service_id),
                    status=ticket.status
                ).inc()

                if ticket.status == "called":
                    TICKET_COMPLETED.labels(
                        service_id=str(ticket.service_id)
                    ).inc()
                    
                    wait_time = (ticket.updated_at - ticket.created_at).total_seconds()
                    TICKET_WAIT_TIME.labels(
                        service_id=str(ticket.service_id)
                    ).observe(wait_time)

            # Calcula métricas de pagamento
            payment_metrics = {
                "total": len(payments),
                "successful": len([p for p in payments if p.status == "paid"]),
                "failed": len([p for p in payments if p.status == "failed"]),
                "total_amount": sum(p.amount for p in payments if p.status == "paid"),
                "average_amount": sum(p.amount for p in payments if p.status == "paid") / len([p for p in payments if p.status == "paid"]) if len([p for p in payments if p.status == "paid"]) > 0 else 0
            }

            # Atualiza métricas Prometheus de pagamento
            for payment in payments:
                PAYMENT_PROCESSED.labels(
                    status=payment.status,
                    payment_method=payment.payment_method
                ).inc()

                if payment.status == "paid":
                    PAYMENT_AMOUNT.labels(
                        status=payment.status,
                        payment_method=payment.payment_method
                    ).inc(payment.amount)

                processing_time = (payment.updated_at - payment.created_at).total_seconds()
                PAYMENT_PROCESSING_TIME.labels(
                    payment_method=payment.payment_method
                ).observe(processing_time)

            # Calcula tempo médio de atendimento
            completed_tickets = [t for t in tickets if t.status == "called"]
            avg_service_time = sum(
                (t.updated_at - t.created_at).total_seconds()
                for t in completed_tickets
            ) / len(completed_tickets) if completed_tickets else 0

            # Atualiza métricas da fila
            for service_id in service_metrics:
                QUEUE_LENGTH.labels(
                    service_id=str(service_id)
                ).set(service_metrics[service_id]["total"] - service_metrics[service_id]["called"])

            return {
                "date": date.strftime("%Y-%m-%d"),
                "tickets": {
                    "total": len(tickets),
                    "by_service": service_metrics,
                    "avg_service_time": avg_service_time
                },
                "payments": payment_metrics,
                "hourly_distribution": self._get_hourly_distribution(tickets)
            }

        except Exception as e:
            logger.error(f"Error getting daily metrics: {str(e)}", exc_info=e)
            raise

    def _get_hourly_distribution(self, tickets: List[Ticket]) -> Dict[str, int]:
        """Calcula distribuição de tickets por hora"""
        distribution = {str(h).zfill(2): 0 for h in range(24)}
        for ticket in tickets:
            hour = ticket.created_at.hour
            distribution[str(hour).zfill(2)] += 1
        return distribution

    async def get_service_metrics(self, tenant_id: str, service_id: str, days: int = 30) -> Dict[str, Any]:
        """Obtém métricas específicas de um serviço"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)

            tickets = self.db.query(Ticket).filter(
                and_(
                    Ticket.tenant_id == tenant_id,
                    Ticket.service_id == service_id,
                    Ticket.created_at >= start_date,
                    Ticket.created_at < end_date
                )
            ).all()

            return {
                "total_tickets": len(tickets),
                "completion_rate": len([t for t in tickets if t.status == "called"]) / len(tickets) if tickets else 0,
                "average_wait_time": sum(
                    (t.updated_at - t.created_at).total_seconds()
                    for t in tickets if t.status == "called"
                ) / len([t for t in tickets if t.status == "called"]) if [t for t in tickets if t.status == "called"] else 0,
                "daily_trend": self._get_daily_trend(tickets)
            }

        except Exception as e:
            logger.error(f"Error getting service metrics: {str(e)}", exc_info=e)
            raise

    def _get_daily_trend(self, tickets: List[Ticket]) -> Dict[str, int]:
        """Calcula tendência diária de tickets"""
        trend = {}
        for ticket in tickets:
            date = ticket.created_at.strftime("%Y-%m-%d")
            if date not in trend:
                trend[date] = 0
            trend[date] += 1
        return trend

    async def export_metrics_csv(self, tenant_id: str, start_date: datetime, end_date: datetime) -> str:
        """Exporta métricas em formato CSV"""
        try:
            tickets = self.db.query(Ticket).filter(
                and_(
                    Ticket.tenant_id == tenant_id,
                    Ticket.created_at >= start_date,
                    Ticket.created_at < end_date
                )
            ).all()

            # Cria cabeçalho do CSV
            csv_lines = [
                "date,service_id,status,created_at,updated_at,customer_name,payment_status,payment_amount"
            ]

            # Adiciona linhas de dados
            for ticket in tickets:
                payment = self.db.query(Payment).filter(
                    Payment.ticket_id == ticket.id
                ).first()

                csv_lines.append(
                    f"{ticket.created_at.strftime('%Y-%m-%d')},"
                    f"{ticket.service_id},"
                    f"{ticket.status},"
                    f"{ticket.created_at.isoformat()},"
                    f"{ticket.updated_at.isoformat()},"
                    f"{ticket.customer_name},"
                    f"{payment.status if payment else 'N/A'},"
                    f"{payment.amount if payment else '0.00'}"
                )

            return "\n".join(csv_lines)

        except Exception as e:
            logger.error(f"Error exporting metrics CSV: {str(e)}", exc_info=e)
            raise 