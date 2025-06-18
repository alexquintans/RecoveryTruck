# 🔊 Serviço Completo de Notificações Sonoras para Operadores

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SoundType(Enum):
    """Tipos de sons disponíveis"""
    BEEP_SHORT = "beep_short"           # Beep curto padrão
    BEEP_LONG = "beep_long"             # Beep longo
    BEEP_URGENT = "beep_urgent"         # Beep urgente (múltiplos)
    BEEP_SUCCESS = "beep_success"       # Som de sucesso
    BEEP_WARNING = "beep_warning"       # Som de alerta
    BEEP_ERROR = "beep_error"           # Som de erro
    CHIME_SOFT = "chime_soft"           # Campainha suave
    CHIME_LOUD = "chime_loud"           # Campainha alta
    NOTIFICATION = "notification"        # Som de notificação
    CALL_TICKET = "call_ticket"         # Som específico para chamar ticket

class NotificationEvent(Enum):
    """Eventos que podem gerar notificações sonoras"""
    NEW_TICKET_IN_QUEUE = "new_ticket_in_queue"
    TICKET_CALLED = "ticket_called"
    TICKET_URGENT = "ticket_urgent"
    TICKET_TIMEOUT = "ticket_timeout"
    PAYMENT_COMPLETED = "payment_completed"
    SYSTEM_ERROR = "system_error"
    OPERATOR_ASSIGNED = "operator_assigned"
    QUEUE_EMPTY = "queue_empty"
    SHIFT_START = "shift_start"
    SHIFT_END = "shift_end"

@dataclass
class SoundConfig:
    """Configuração de um som específico"""
    sound_type: SoundType
    enabled: bool = True
    volume: float = 0.8                 # 0.0 a 1.0
    repeat_count: int = 1               # Quantas vezes repetir
    repeat_interval: float = 0.5        # Intervalo entre repetições (segundos)
    priority: int = 1                   # Prioridade (1=baixa, 5=alta)

@dataclass
class OperatorNotificationConfig:
    """Configuração completa de notificações para um operador"""
    operator_id: str
    tenant_id: str
    
    # Configurações gerais
    sounds_enabled: bool = True
    master_volume: float = 0.8
    
    # Configurações por evento
    event_sounds: Dict[NotificationEvent, SoundConfig] = field(default_factory=dict)
    
    # Configurações avançadas
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    
    # Filtros
    only_assigned_tickets: bool = False  # Som apenas para tickets atribuídos ao operador
    min_priority_level: int = 1          # Nível mínimo de prioridade para som
    
    def __post_init__(self):
        """Inicializa configurações padrão se não fornecidas"""
        if not self.event_sounds:
            self.event_sounds = self._get_default_event_sounds()
    
    def _get_default_event_sounds(self) -> Dict[NotificationEvent, SoundConfig]:
        """Retorna configurações padrão de sons por evento"""
        return {
            NotificationEvent.NEW_TICKET_IN_QUEUE: SoundConfig(
                sound_type=SoundType.CHIME_SOFT,
                enabled=True,
                volume=0.6,
                priority=2
            ),
            NotificationEvent.TICKET_CALLED: SoundConfig(
                sound_type=SoundType.CALL_TICKET,
                enabled=True,
                volume=0.9,
                repeat_count=2,
                repeat_interval=1.0,
                priority=4
            ),
            NotificationEvent.TICKET_URGENT: SoundConfig(
                sound_type=SoundType.BEEP_URGENT,
                enabled=True,
                volume=1.0,
                repeat_count=3,
                repeat_interval=0.3,
                priority=5
            ),
            NotificationEvent.TICKET_TIMEOUT: SoundConfig(
                sound_type=SoundType.BEEP_WARNING,
                enabled=True,
                volume=0.8,
                repeat_count=2,
                priority=3
            ),
            NotificationEvent.PAYMENT_COMPLETED: SoundConfig(
                sound_type=SoundType.BEEP_SUCCESS,
                enabled=True,
                volume=0.7,
                priority=2
            ),
            NotificationEvent.SYSTEM_ERROR: SoundConfig(
                sound_type=SoundType.BEEP_ERROR,
                enabled=True,
                volume=0.9,
                repeat_count=2,
                priority=4
            ),
            NotificationEvent.OPERATOR_ASSIGNED: SoundConfig(
                sound_type=SoundType.NOTIFICATION,
                enabled=True,
                volume=0.6,
                priority=2
            ),
            NotificationEvent.QUEUE_EMPTY: SoundConfig(
                sound_type=SoundType.CHIME_SOFT,
                enabled=False,  # Desabilitado por padrão
                volume=0.5,
                priority=1
            ),
            NotificationEvent.SHIFT_START: SoundConfig(
                sound_type=SoundType.BEEP_SUCCESS,
                enabled=True,
                volume=0.7,
                priority=2
            ),
            NotificationEvent.SHIFT_END: SoundConfig(
                sound_type=SoundType.BEEP_LONG,
                enabled=True,
                volume=0.7,
                priority=2
            )
        }

class OperatorNotificationService:
    """🔊 Serviço de notificações sonoras para operadores"""
    
    def __init__(self):
        self._operator_configs: Dict[str, OperatorNotificationConfig] = {}
        self._tenant_configs: Dict[str, Dict[str, Any]] = {}
        logger.info("🔊 OperatorNotificationService initialized")
    
    def register_operator(self, operator_id: str, tenant_id: str, config: Optional[Dict[str, Any]] = None) -> OperatorNotificationConfig:
        """Registra um operador no serviço de notificações"""
        
        logger.info(f"🔊 Registering operator {operator_id} for notifications")
        
        # Criar configuração do operador
        operator_config = OperatorNotificationConfig(
            operator_id=operator_id,
            tenant_id=tenant_id
        )
        
        # Aplicar configurações customizadas se fornecidas
        if config:
            self._apply_custom_config(operator_config, config)
        
        # Armazenar configuração
        self._operator_configs[operator_id] = operator_config
        
        logger.info(f"✅ Operator {operator_id} registered for notifications")
        return operator_config
    
    def _apply_custom_config(self, operator_config: OperatorNotificationConfig, config: Dict[str, Any]):
        """Aplica configurações customizadas ao operador"""
        
        if "sounds_enabled" in config:
            operator_config.sounds_enabled = config["sounds_enabled"]
        
        if "master_volume" in config:
            operator_config.master_volume = max(0.0, min(1.0, config["master_volume"]))
        
        if "quiet_hours_enabled" in config:
            operator_config.quiet_hours_enabled = config["quiet_hours_enabled"]
        
        if "quiet_hours_start" in config:
            operator_config.quiet_hours_start = config["quiet_hours_start"]
        
        if "quiet_hours_end" in config:
            operator_config.quiet_hours_end = config["quiet_hours_end"]
        
        if "only_assigned_tickets" in config:
            operator_config.only_assigned_tickets = config["only_assigned_tickets"]
        
        if "min_priority_level" in config:
            operator_config.min_priority_level = config["min_priority_level"]
        
        # Configurações específicas por evento
        if "event_sounds" in config:
            for event_name, sound_config in config["event_sounds"].items():
                try:
                    event = NotificationEvent(event_name)
                    sound_type = SoundType(sound_config.get("sound_type", "beep_short"))
                    
                    operator_config.event_sounds[event] = SoundConfig(
                        sound_type=sound_type,
                        enabled=sound_config.get("enabled", True),
                        volume=max(0.0, min(1.0, sound_config.get("volume", 0.8))),
                        repeat_count=max(1, sound_config.get("repeat_count", 1)),
                        repeat_interval=max(0.1, sound_config.get("repeat_interval", 0.5)),
                        priority=max(1, min(5, sound_config.get("priority", 1)))
                    )
                except (ValueError, KeyError) as e:
                    logger.warning(f"⚠️ Invalid sound config for event {event_name}: {e}")
    
    def get_operator_config(self, operator_id: str) -> Optional[OperatorNotificationConfig]:
        """Obtém configuração de um operador"""
        return self._operator_configs.get(operator_id)
    
    def update_operator_config(self, operator_id: str, config_updates: Dict[str, Any]) -> bool:
        """Atualiza configuração de um operador"""
        
        if operator_id not in self._operator_configs:
            logger.warning(f"⚠️ Operator {operator_id} not registered for notifications")
            return False
        
        operator_config = self._operator_configs[operator_id]
        self._apply_custom_config(operator_config, config_updates)
        
        logger.info(f"✅ Updated notification config for operator {operator_id}")
        return True
    
    def should_play_sound(self, operator_id: str, event: NotificationEvent, ticket_data: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[SoundConfig]]:
        """Verifica se deve reproduzir som para um evento específico"""
        
        operator_config = self._operator_configs.get(operator_id)
        if not operator_config:
            return False, None
        
        # Verificar se sons estão habilitados globalmente
        if not operator_config.sounds_enabled:
            return False, None
        
        # Verificar horário silencioso
        if operator_config.quiet_hours_enabled and self._is_quiet_hours(operator_config):
            return False, None
        
        # Verificar se evento tem configuração de som
        if event not in operator_config.event_sounds:
            return False, None
        
        sound_config = operator_config.event_sounds[event]
        
        # Verificar se som está habilitado para este evento
        if not sound_config.enabled:
            return False, None
        
        # Verificar prioridade mínima
        if sound_config.priority < operator_config.min_priority_level:
            return False, None
        
        # Verificar filtros específicos de ticket
        if ticket_data and operator_config.only_assigned_tickets:
            assigned_operator = ticket_data.get("assigned_operator_id")
            if assigned_operator != operator_id:
                return False, None
        
        return True, sound_config
    
    def _is_quiet_hours(self, config: OperatorNotificationConfig) -> bool:
        """Verifica se está no horário silencioso"""
        try:
            now = datetime.now().time()
            start_time = datetime.strptime(config.quiet_hours_start, "%H:%M").time()
            end_time = datetime.strptime(config.quiet_hours_end, "%H:%M").time()
            
            if start_time <= end_time:
                # Mesmo dia (ex: 08:00 às 22:00)
                return start_time <= now <= end_time
            else:
                # Atravessa meia-noite (ex: 22:00 às 08:00)
                return now >= start_time or now <= end_time
        except Exception as e:
            logger.error(f"❌ Error checking quiet hours: {e}")
            return False
    
    def create_notification_payload(self, operator_id: str, event: NotificationEvent, ticket_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Cria payload de notificação sonora para envio via WebSocket"""
        
        should_play, sound_config = self.should_play_sound(operator_id, event, ticket_data)
        
        if not should_play or not sound_config:
            return None
        
        operator_config = self._operator_configs[operator_id]
        
        # Calcular volume final (master_volume * sound_volume)
        final_volume = operator_config.master_volume * sound_config.volume
        
        payload = {
            "type": "sound_notification",
            "event": event.value,
            "sound": {
                "type": sound_config.sound_type.value,
                "volume": final_volume,
                "repeat_count": sound_config.repeat_count,
                "repeat_interval": sound_config.repeat_interval,
                "priority": sound_config.priority
            },
            "timestamp": datetime.now().isoformat(),
            "operator_id": operator_id
        }
        
        # Adicionar dados do ticket se fornecidos
        if ticket_data:
            payload["ticket"] = ticket_data
        
        logger.info(f"🔊 Created sound notification for operator {operator_id}: {event.value}")
        return payload
    
    def get_available_sounds(self) -> Dict[str, Dict[str, Any]]:
        """Retorna lista de sons disponíveis com descrições"""
        return {
            sound_type.value: {
                "name": sound_type.value.replace("_", " ").title(),
                "description": self._get_sound_description(sound_type),
                "category": self._get_sound_category(sound_type)
            }
            for sound_type in SoundType
        }
    
    def _get_sound_description(self, sound_type: SoundType) -> str:
        """Retorna descrição de um tipo de som"""
        descriptions = {
            SoundType.BEEP_SHORT: "Beep curto e discreto",
            SoundType.BEEP_LONG: "Beep longo e suave",
            SoundType.BEEP_URGENT: "Beep urgente com múltiplas repetições",
            SoundType.BEEP_SUCCESS: "Som de sucesso/confirmação",
            SoundType.BEEP_WARNING: "Som de alerta/atenção",
            SoundType.BEEP_ERROR: "Som de erro/problema",
            SoundType.CHIME_SOFT: "Campainha suave e agradável",
            SoundType.CHIME_LOUD: "Campainha alta e clara",
            SoundType.NOTIFICATION: "Som de notificação padrão",
            SoundType.CALL_TICKET: "Som específico para chamada de ticket"
        }
        return descriptions.get(sound_type, "Som personalizado")
    
    def _get_sound_category(self, sound_type: SoundType) -> str:
        """Retorna categoria de um tipo de som"""
        if sound_type.value.startswith("beep"):
            return "beeps"
        elif sound_type.value.startswith("chime"):
            return "chimes"
        else:
            return "notifications"
    
    def export_operator_config(self, operator_id: str) -> Optional[Dict[str, Any]]:
        """Exporta configuração de um operador para JSON"""
        
        config = self._operator_configs.get(operator_id)
        if not config:
            return None
        
        return {
            "operator_id": config.operator_id,
            "tenant_id": config.tenant_id,
            "sounds_enabled": config.sounds_enabled,
            "master_volume": config.master_volume,
            "quiet_hours_enabled": config.quiet_hours_enabled,
            "quiet_hours_start": config.quiet_hours_start,
            "quiet_hours_end": config.quiet_hours_end,
            "only_assigned_tickets": config.only_assigned_tickets,
            "min_priority_level": config.min_priority_level,
            "event_sounds": {
                event.value: {
                    "sound_type": sound_config.sound_type.value,
                    "enabled": sound_config.enabled,
                    "volume": sound_config.volume,
                    "repeat_count": sound_config.repeat_count,
                    "repeat_interval": sound_config.repeat_interval,
                    "priority": sound_config.priority
                }
                for event, sound_config in config.event_sounds.items()
            }
        }

# Instância global do serviço
notification_service = OperatorNotificationService() 