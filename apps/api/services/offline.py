from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
import logging
from models import Ticket, PaymentSession as Payment
from database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class OfflineQueue:
    def __init__(self):
        self.tickets: List[Dict[str, Any]] = []
        self.payments: List[Dict[str, Any]] = []
        self.sync_in_progress = False

    async def add_ticket(self, ticket_data: Dict[str, Any]):
        """Adiciona um ticket à fila offline"""
        ticket_data["created_at"] = datetime.utcnow().isoformat()
        ticket_data["status"] = "pending"
        self.tickets.append(ticket_data)
        logger.info(f"Ticket added to offline queue: {ticket_data['ticket_number']}")

    async def add_payment(self, payment_data: Dict[str, Any]):
        """Adiciona um pagamento à fila offline"""
        payment_data["created_at"] = datetime.utcnow().isoformat()
        payment_data["status"] = "pending"
        self.payments.append(payment_data)
        logger.info(f"Payment added to offline queue: {payment_data['transaction_id']}")

    async def sync(self, db: Session):
        """Sincroniza a fila offline com o banco de dados"""
        if self.sync_in_progress:
            logger.warning("Sync already in progress")
            return

        self.sync_in_progress = True
        try:
            # Sincroniza tickets
            for ticket_data in self.tickets[:]:
                try:
                    ticket = Ticket(**ticket_data)
                    db.add(ticket)
                    db.commit()
                    self.tickets.remove(ticket_data)
                    logger.info(f"Ticket synced: {ticket.ticket_number}")
                except Exception as e:
                    logger.error(f"Error syncing ticket: {str(e)}")
                    continue

            # Sincroniza pagamentos
            for payment_data in self.payments[:]:
                try:
                    payment = Payment(**payment_data)
                    db.add(payment)
                    db.commit()
                    self.payments.remove(payment_data)
                    logger.info(f"Payment synced: {payment.transaction_id}")
                except Exception as e:
                    logger.error(f"Error syncing payment: {str(e)}")
                    continue

        finally:
            self.sync_in_progress = False

    def get_queue_status(self) -> Dict[str, Any]:
        """Retorna o status atual da fila offline"""
        return {
            "tickets_count": len(self.tickets),
            "payments_count": len(self.payments),
            "sync_in_progress": self.sync_in_progress,
            "last_sync": datetime.utcnow().isoformat() if not self.sync_in_progress else None
        }

class OfflineManager:
    def __init__(self):
        self.queue = OfflineQueue()
        self.is_online = True
        self._sync_task = None

    async def start_sync_task(self):
        """Inicia a tarefa de sincronização periódica"""
        if self._sync_task is None:
            self._sync_task = asyncio.create_task(self._periodic_sync())

    async def stop_sync_task(self):
        """Para a tarefa de sincronização periódica"""
        if self._sync_task:
            self._sync_task.cancel()
            self._sync_task = None

    async def _periodic_sync(self):
        """Tarefa periódica de sincronização"""
        while True:
            try:
                if self.is_online:
                    db = next(get_db())
                    await self.queue.sync(db)
                await asyncio.sleep(60)  # Sincroniza a cada minuto
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic sync: {str(e)}")
                await asyncio.sleep(60)

    def set_online_status(self, status: bool):
        """Define o status de conexão do sistema"""
        self.is_online = status
        if status:
            asyncio.create_task(self.start_sync_task())
        else:
            asyncio.create_task(self.stop_sync_task())

    async def handle_ticket(self, ticket_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Processa um ticket, online ou offline"""
        if self.is_online:
            try:
                ticket = Ticket(**ticket_data)
                db.add(ticket)
                db.commit()
                return {"status": "success", "ticket": ticket}
            except Exception as e:
                logger.error(f"Error creating ticket: {str(e)}")
                raise
        else:
            await self.queue.add_ticket(ticket_data)
            return {
                "status": "queued",
                "message": "Ticket added to offline queue",
                "ticket_number": ticket_data["ticket_number"]
            }

    async def handle_payment(self, payment_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Processa um pagamento, online ou offline"""
        if self.is_online:
            try:
                payment = Payment(**payment_data)
                db.add(payment)
                db.commit()
                return {"status": "success", "payment": payment}
            except Exception as e:
                logger.error(f"Error creating payment: {str(e)}")
                raise
        else:
            await self.queue.add_payment(payment_data)
            return {
                "status": "queued",
                "message": "Payment added to offline queue",
                "transaction_id": payment_data["transaction_id"]
            }

# Instância global do gerenciador offline
offline_manager = OfflineManager() 