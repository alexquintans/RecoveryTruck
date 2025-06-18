from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio
from ..models.ticket import Ticket
from ..models.payment import Payment

# Importar o serviço de notificações
from .notification_service import notification_service, NotificationEvent

class ConnectionManager:
    def __init__(self):
        # Conexões por tenant
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Conexões de operadores
        self.operator_connections: Dict[str, Set[WebSocket]] = {}
        # Conexões de totens
        self.totem_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: str, client_type: str):
        """Conecta um novo cliente WebSocket"""
        await websocket.accept()
        
        if client_type == "operator":
            if tenant_id not in self.operator_connections:
                self.operator_connections[tenant_id] = set()
            self.operator_connections[tenant_id].add(websocket)
        elif client_type == "totem":
            if tenant_id not in self.totem_connections:
                self.totem_connections[tenant_id] = set()
            self.totem_connections[tenant_id].add(websocket)
        else:
            if tenant_id not in self.active_connections:
                self.active_connections[tenant_id] = set()
            self.active_connections[tenant_id].add(websocket)

    def disconnect(self, websocket: WebSocket, tenant_id: str, client_type: str):
        """Desconecta um cliente WebSocket"""
        if client_type == "operator":
            if tenant_id in self.operator_connections:
                self.operator_connections[tenant_id].discard(websocket)
        elif client_type == "totem":
            if tenant_id in self.totem_connections:
                self.totem_connections[tenant_id].discard(websocket)
        else:
            if tenant_id in self.active_connections:
                self.active_connections[tenant_id].discard(websocket)

    async def broadcast_ticket_update(self, tenant_id: str, ticket: Ticket):
        """Transmite atualização de ticket para todos os clientes do tenant"""
        message = {
            "type": "ticket_update",
            "data": {
                "id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "customer_name": ticket.customer_name,
                "service_id": str(ticket.service_id) if ticket.service_id else None,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
        # 🔊 Criar notificação sonora baseada no status do ticket
        await self._handle_ticket_sound_notification(tenant_id, ticket, message)
        
        # Envia para operadores
        if tenant_id in self.operator_connections:
            for connection in self.operator_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    self.disconnect(connection, tenant_id, "operator")

        # Envia para totens
        if tenant_id in self.totem_connections:
            for connection in self.totem_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    self.disconnect(connection, tenant_id, "totem")

    async def _handle_ticket_sound_notification(self, tenant_id: str, ticket: Ticket, message: Dict):
        """Processa notificações sonoras baseadas em mudanças de status do ticket"""
        
        # Determinar evento baseado no status do ticket
        event = None
        if ticket.status == "in_queue":
            event = NotificationEvent.NEW_TICKET_IN_QUEUE
        elif ticket.status == "called":
            event = NotificationEvent.TICKET_CALLED
        elif ticket.status == "expired" or ticket.status == "timeout":
            event = NotificationEvent.TICKET_TIMEOUT
        
        if not event:
            return
        
        # Dados do ticket para notificação
        ticket_data = {
            "id": str(ticket.id),
            "ticket_number": ticket.ticket_number,
            "customer_name": ticket.customer_name,
            "status": ticket.status,
            "assigned_operator_id": str(ticket.assigned_operator_id) if ticket.assigned_operator_id else None,
            "service_name": ticket.service.name if ticket.service else "Serviço"
        }
        
        # Enviar notificação sonora para todos os operadores do tenant
        await self._send_sound_notifications_to_operators(tenant_id, event, ticket_data)

    async def _send_sound_notifications_to_operators(self, tenant_id: str, event: NotificationEvent, ticket_data: Dict):
        """Envia notificações sonoras para operadores conectados"""
        
        if tenant_id not in self.operator_connections:
            return
        
        # Para cada operador conectado, verificar se deve enviar notificação sonora
        for connection in list(self.operator_connections[tenant_id]):
            try:
                # Obter ID do operador da conexão (seria necessário armazenar isso na conexão)
                # Por enquanto, vamos enviar para todos os operadores
                operator_id = getattr(connection, 'operator_id', None)
                
                if operator_id:
                    # Criar payload de notificação sonora
                    sound_payload = notification_service.create_notification_payload(
                        operator_id=operator_id,
                        event=event,
                        ticket_data=ticket_data
                    )
                    
                    if sound_payload:
                        await connection.send_json(sound_payload)
                        
            except WebSocketDisconnect:
                self.disconnect(connection, tenant_id, "operator")
            except Exception as e:
                print(f"Error sending sound notification: {e}")

    async def broadcast_payment_update(self, tenant_id: str, payment: Payment):
        """Transmite atualização de pagamento para todos os clientes do tenant"""
        message = {
            "type": "payment_update",
            "data": {
                "id": str(payment.id),
                "transaction_id": payment.transaction_id,
                "status": payment.status,
                "amount": float(payment.amount),
                "payment_method": payment.payment_method,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
        # 🔊 Notificação sonora para pagamento completado
        if payment.status == "completed":
            await self._send_payment_sound_notification(tenant_id, payment)
        
        # Envia para operadores
        if tenant_id in self.operator_connections:
            for connection in self.operator_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    self.disconnect(connection, tenant_id, "operator")

        # Envia para totens
        if tenant_id in self.totem_connections:
            for connection in self.totem_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    self.disconnect(connection, tenant_id, "totem")

    async def _send_payment_sound_notification(self, tenant_id: str, payment: Payment):
        """Envia notificação sonora para pagamento completado"""
        
        payment_data = {
            "id": str(payment.id),
            "transaction_id": payment.transaction_id,
            "amount": float(payment.amount),
            "payment_method": payment.payment_method
        }
        
        await self._send_sound_notifications_to_operators(
            tenant_id, 
            NotificationEvent.PAYMENT_COMPLETED, 
            payment_data
        )

    async def broadcast_queue_update(self, tenant_id: str, queue_data: dict):
        """Transmite atualização da fila para todos os clientes do tenant"""
        message = {
            "type": "queue_update",
            "data": queue_data
        }
        
        # Envia para operadores
        if tenant_id in self.operator_connections:
            for connection in self.operator_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    self.disconnect(connection, tenant_id, "operator")

        # Envia para totens
        if tenant_id in self.totem_connections:
            for connection in self.totem_connections[tenant_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    self.disconnect(connection, tenant_id, "totem")

    async def send_operator_notification(self, tenant_id: str, message: str, operator_id: Optional[str] = None):
        """Envia notificação para operadores"""
        notification = {
            "type": "notification",
            "data": {
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        if tenant_id in self.operator_connections:
            for connection in self.operator_connections[tenant_id]:
                try:
                    # Se operator_id específico, verificar se é o operador correto
                    if operator_id and hasattr(connection, 'operator_id'):
                        if connection.operator_id != operator_id:
                            continue
                    
                    await connection.send_json(notification)
                except WebSocketDisconnect:
                    self.disconnect(connection, tenant_id, "operator")

    async def send_sound_notification(self, tenant_id: str, operator_id: str, event: NotificationEvent, ticket_data: Optional[Dict] = None):
        """Envia notificação sonora específica para um operador"""
        
        sound_payload = notification_service.create_notification_payload(
            operator_id=operator_id,
            event=event,
            ticket_data=ticket_data
        )
        
        if not sound_payload:
            return
        
        if tenant_id in self.operator_connections:
            for connection in self.operator_connections[tenant_id]:
                try:
                    # Verificar se é o operador correto
                    if hasattr(connection, 'operator_id') and connection.operator_id == operator_id:
                        await connection.send_json(sound_payload)
                        break
                except WebSocketDisconnect:
                    self.disconnect(connection, tenant_id, "operator")

    async def register_operator_connection(self, websocket: WebSocket, tenant_id: str, operator_id: str):
        """Registra conexão de operador com ID específico"""
        
        # Adicionar ID do operador à conexão WebSocket
        websocket.operator_id = operator_id
        
        # Registrar operador no serviço de notificações se ainda não estiver
        if not notification_service.get_operator_config(operator_id):
            notification_service.register_operator(operator_id, tenant_id)
        
        # Conectar normalmente
        await self.connect(websocket, tenant_id, "operator")
        
        # Enviar som de início de turno
        await self.send_sound_notification(
            tenant_id, 
            operator_id, 
            NotificationEvent.SHIFT_START
        )

    async def unregister_operator_connection(self, websocket: WebSocket, tenant_id: str, operator_id: str):
        """Remove registro de conexão de operador"""
        
        # Enviar som de fim de turno
        await self.send_sound_notification(
            tenant_id, 
            operator_id, 
            NotificationEvent.SHIFT_END
        )
        
        # Desconectar
        self.disconnect(websocket, tenant_id, "operator")

# Instância global do gerenciador
manager = ConnectionManager() 