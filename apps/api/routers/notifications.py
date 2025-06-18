# 🔊 Router para Configurações de Notificações Sonoras

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from database import get_db
from auth import get_current_operator
from models import Operator
from services.notification_service import (
    notification_service, 
    NotificationEvent, 
    SoundType,
    OperatorNotificationConfig
)
from services.websocket import manager

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

# === Schemas ===

class SoundConfigSchema(BaseModel):
    """Schema para configuração de som"""
    sound_type: str = Field(..., description="Tipo de som")
    enabled: bool = Field(True, description="Som habilitado")
    volume: float = Field(0.8, ge=0.0, le=1.0, description="Volume (0.0 a 1.0)")
    repeat_count: int = Field(1, ge=1, le=10, description="Número de repetições")
    repeat_interval: float = Field(0.5, ge=0.1, le=5.0, description="Intervalo entre repetições")
    priority: int = Field(1, ge=1, le=5, description="Prioridade (1=baixa, 5=alta)")

class NotificationConfigSchema(BaseModel):
    """Schema para configuração completa de notificações"""
    sounds_enabled: bool = Field(True, description="Sons habilitados globalmente")
    master_volume: float = Field(0.8, ge=0.0, le=1.0, description="Volume master")
    quiet_hours_enabled: bool = Field(False, description="Horário silencioso habilitado")
    quiet_hours_start: str = Field("22:00", description="Início do horário silencioso")
    quiet_hours_end: str = Field("08:00", description="Fim do horário silencioso")
    only_assigned_tickets: bool = Field(False, description="Som apenas para tickets atribuídos")
    min_priority_level: int = Field(1, ge=1, le=5, description="Nível mínimo de prioridade")
    event_sounds: Optional[Dict[str, SoundConfigSchema]] = Field(None, description="Configurações por evento")

class TestSoundRequest(BaseModel):
    """Schema para teste de som"""
    sound_type: str = Field(..., description="Tipo de som para testar")
    volume: float = Field(0.8, ge=0.0, le=1.0, description="Volume do teste")
    repeat_count: int = Field(1, ge=1, le=3, description="Repetições do teste")

# === Endpoints ===

@router.get("/config")
async def get_notification_config(
    current_operator: Operator = Depends(get_current_operator)
):
    """Obtém configuração de notificações do operador atual"""
    
    operator_config = notification_service.get_operator_config(str(current_operator.id))
    
    if not operator_config:
        # Registrar operador se não existir
        operator_config = notification_service.register_operator(
            str(current_operator.id), 
            str(current_operator.tenant_id)
        )
    
    # Exportar configuração
    config_data = notification_service.export_operator_config(str(current_operator.id))
    
    return {
        "operator_id": str(current_operator.id),
        "operator_name": current_operator.name,
        "tenant_id": str(current_operator.tenant_id),
        "config": config_data
    }

@router.put("/config")
async def update_notification_config(
    config_update: NotificationConfigSchema,
    current_operator: Operator = Depends(get_current_operator)
):
    """Atualiza configuração de notificações do operador"""
    
    operator_id = str(current_operator.id)
    
    # Converter schema para dict
    config_dict = config_update.dict(exclude_unset=True)
    
    # Converter event_sounds se fornecido
    if config_update.event_sounds:
        config_dict["event_sounds"] = {
            event: sound_config.dict()
            for event, sound_config in config_update.event_sounds.items()
        }
    
    # Atualizar configuração
    success = notification_service.update_operator_config(operator_id, config_dict)
    
    if not success:
        # Registrar operador se não existir
        notification_service.register_operator(
            operator_id, 
            str(current_operator.tenant_id), 
            config_dict
        )
    
    return {
        "message": "Configuração de notificações atualizada com sucesso",
        "operator_id": operator_id,
        "updated_config": notification_service.export_operator_config(operator_id)
    }

@router.get("/sounds")
async def get_available_sounds():
    """Lista todos os tipos de sons disponíveis"""
    
    sounds = notification_service.get_available_sounds()
    
    return {
        "sounds": sounds,
        "categories": {
            "beeps": [s for s, data in sounds.items() if data["category"] == "beeps"],
            "chimes": [s for s, data in sounds.items() if data["category"] == "chimes"],
            "notifications": [s for s, data in sounds.items() if data["category"] == "notifications"]
        }
    }

@router.get("/events")
async def get_notification_events():
    """Lista todos os eventos que podem gerar notificações"""
    
    events = {}
    for event in NotificationEvent:
        events[event.value] = {
            "name": event.value.replace("_", " ").title(),
            "description": _get_event_description(event)
        }
    
    return {"events": events}

def _get_event_description(event: NotificationEvent) -> str:
    """Retorna descrição de um evento"""
    descriptions = {
        NotificationEvent.NEW_TICKET_IN_QUEUE: "Novo ticket adicionado à fila",
        NotificationEvent.TICKET_CALLED: "Ticket chamado para atendimento",
        NotificationEvent.TICKET_URGENT: "Ticket com prioridade urgente",
        NotificationEvent.TICKET_TIMEOUT: "Ticket expirado por timeout",
        NotificationEvent.PAYMENT_COMPLETED: "Pagamento concluído com sucesso",
        NotificationEvent.SYSTEM_ERROR: "Erro no sistema",
        NotificationEvent.OPERATOR_ASSIGNED: "Ticket atribuído ao operador",
        NotificationEvent.QUEUE_EMPTY: "Fila vazia",
        NotificationEvent.SHIFT_START: "Início do turno",
        NotificationEvent.SHIFT_END: "Fim do turno"
    }
    return descriptions.get(event, "Evento de notificação")

@router.post("/test")
async def test_sound(
    test_request: TestSoundRequest,
    current_operator: Operator = Depends(get_current_operator)
):
    """Testa um som específico"""
    
    operator_id = str(current_operator.id)
    tenant_id = str(current_operator.tenant_id)
    
    # Verificar se o tipo de som é válido
    try:
        sound_type = SoundType(test_request.sound_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de som inválido: {test_request.sound_type}"
        )
    
    # Criar payload de teste
    test_payload = {
        "type": "sound_notification",
        "event": "test_sound",
        "sound": {
            "type": test_request.sound_type,
            "volume": test_request.volume,
            "repeat_count": test_request.repeat_count,
            "repeat_interval": 0.5,
            "priority": 3
        },
        "timestamp": "2024-01-01T00:00:00",
        "operator_id": operator_id,
        "test": True
    }
    
    # Enviar via WebSocket
    if tenant_id in manager.operator_connections:
        for connection in manager.operator_connections[tenant_id]:
            if hasattr(connection, 'operator_id') and connection.operator_id == operator_id:
                try:
                    await connection.send_json(test_payload)
                    break
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Erro ao enviar teste de som: {e}"
                    )
    
    return {
        "message": f"Som de teste '{test_request.sound_type}' enviado",
        "sound_type": test_request.sound_type,
        "volume": test_request.volume,
        "repeat_count": test_request.repeat_count
    }

@router.post("/trigger/{event}")
async def trigger_notification_event(
    event: str,
    current_operator: Operator = Depends(get_current_operator)
):
    """Dispara manualmente um evento de notificação para teste"""
    
    try:
        notification_event = NotificationEvent(event)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Evento inválido: {event}"
        )
    
    operator_id = str(current_operator.id)
    tenant_id = str(current_operator.tenant_id)
    
    # Dados de teste do ticket
    test_ticket_data = {
        "id": "test-ticket-id",
        "ticket_number": 999,
        "customer_name": "Cliente Teste",
        "status": "test",
        "service_name": "Teste de Som"
    }
    
    # Enviar notificação
    await manager.send_sound_notification(
        tenant_id, 
        operator_id, 
        notification_event, 
        test_ticket_data
    )
    
    return {
        "message": f"Evento '{event}' disparado para teste",
        "event": event,
        "operator_id": operator_id
    }

@router.get("/status")
async def get_notification_status(
    current_operator: Operator = Depends(get_current_operator)
):
    """Obtém status das notificações do operador"""
    
    operator_id = str(current_operator.id)
    tenant_id = str(current_operator.tenant_id)
    
    # Verificar se operador está registrado
    config = notification_service.get_operator_config(operator_id)
    is_registered = config is not None
    
    # Verificar se está conectado via WebSocket
    is_connected = False
    if tenant_id in manager.operator_connections:
        for connection in manager.operator_connections[tenant_id]:
            if hasattr(connection, 'operator_id') and connection.operator_id == operator_id:
                is_connected = True
                break
    
    # Verificar horário silencioso
    is_quiet_hours = False
    if config and config.quiet_hours_enabled:
        is_quiet_hours = notification_service._is_quiet_hours(config)
    
    return {
        "operator_id": operator_id,
        "operator_name": current_operator.name,
        "is_registered": is_registered,
        "is_connected": is_connected,
        "sounds_enabled": config.sounds_enabled if config else False,
        "is_quiet_hours": is_quiet_hours,
        "master_volume": config.master_volume if config else 0.8,
        "connection_count": len(manager.operator_connections.get(tenant_id, set()))
    }

@router.delete("/config")
async def reset_notification_config(
    current_operator: Operator = Depends(get_current_operator)
):
    """Reseta configuração de notificações para padrão"""
    
    operator_id = str(current_operator.id)
    tenant_id = str(current_operator.tenant_id)
    
    # Registrar novamente com configurações padrão
    notification_service.register_operator(operator_id, tenant_id)
    
    return {
        "message": "Configuração de notificações resetada para padrão",
        "operator_id": operator_id,
        "default_config": notification_service.export_operator_config(operator_id)
    }
