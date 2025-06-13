from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio
from ..models.ticket import Ticket
from ..models.payment import Payment

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
            self.operator_connections[tenant_id].remove(websocket)
        elif client_type == "totem":
            self.totem_connections[tenant_id].remove(websocket)
        else:
            self.active_connections[tenant_id].remove(websocket)

    async def broadcast_ticket_update(self, tenant_id: str, ticket: Ticket):
        """Transmite atualização de ticket para todos os clientes do tenant"""
        message = {
            "type": "ticket_update",
            "data": {
                "id": str(ticket.id),
                "number": ticket.ticket_number,
                "status": ticket.status,
                "service_id": str(ticket.service_id),
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat()
            }
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

    async def broadcast_payment_update(self, tenant_id: str, payment: Payment):
        """Transmite atualização de pagamento para todos os clientes do tenant"""
        message = {
            "type": "payment_update",
            "data": {
                "id": str(payment.id),
                "ticket_id": str(payment.ticket_id),
                "status": payment.status,
                "amount": payment.amount,
                "created_at": payment.created_at.isoformat(),
                "updated_at": payment.updated_at.isoformat()
            }
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

    async def send_operator_notification(self, tenant_id: str, message: str):
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
                    await connection.send_json(notification)
                except WebSocketDisconnect:
                    self.disconnect(connection, tenant_id, "operator")

# Instância global do gerenciador de conexões
manager = ConnectionManager() 