# 🎯 Estados e Transições do Sistema Totem

from enum import Enum
from typing import Dict, List, Set

class TicketStatus(str, Enum):
    """Estados possíveis de um ticket no sistema"""
    
    # Estados iniciais
    PAID = "paid"                    # Pago, aguardando impressão
    PRINTING = "printing"            # Sendo impresso
    PRINT_ERROR = "print_error"      # Erro na impressão
    
    # Estados da fila
    IN_QUEUE = "in_queue"           # Na fila do operador (impresso com sucesso)
    CALLED = "called"               # Chamado pelo operador
    
    # Estados de atendimento
    IN_PROGRESS = "in_progress"     # Em atendimento
    COMPLETED = "completed"         # Concluído
    
    # Estados especiais
    CANCELLED = "cancelled"         # Cancelado
    EXPIRED = "expired"             # Expirado (não compareceu)

class PaymentSessionStatus(str, Enum):
    """Estados possíveis de uma sessão de pagamento"""
    
    PENDING = "pending"             # Aguardando pagamento
    PAID = "paid"                   # Pagamento confirmado
    FAILED = "failed"               # Pagamento falhou
    EXPIRED = "expired"             # Sessão expirou
    CANCELLED = "cancelled"         # Cancelada

class QueuePriority(str, Enum):
    """Prioridades na fila de atendimento"""
    
    HIGH = "high"                   # Alta prioridade (problemas, reimpressões)
    NORMAL = "normal"               # Prioridade normal
    LOW = "low"                     # Baixa prioridade (expirados reativados)

class QueueSortOrder(str, Enum):
    """Ordenações possíveis da fila"""
    
    FIFO = "fifo"                   # First In, First Out (padrão)
    PRIORITY = "priority"           # Por prioridade
    SERVICE = "service"             # Por tipo de serviço
    WAITING_TIME = "waiting_time"   # Por tempo de espera

# 🔄 Transições válidas entre estados
TICKET_TRANSITIONS: Dict[TicketStatus, Set[TicketStatus]] = {
    TicketStatus.PAID: {
        TicketStatus.PRINTING,
        TicketStatus.PRINT_ERROR,
        TicketStatus.CANCELLED
    },
    TicketStatus.PRINTING: {
        TicketStatus.IN_QUEUE,
        TicketStatus.PRINT_ERROR,
        TicketStatus.CANCELLED
    },
    TicketStatus.PRINT_ERROR: {
        TicketStatus.PRINTING,      # Tentar reimprimir
        TicketStatus.IN_QUEUE,      # Pular impressão e ir para fila
        TicketStatus.CANCELLED
    },
    TicketStatus.IN_QUEUE: {
        TicketStatus.CALLED,
        TicketStatus.EXPIRED,
        TicketStatus.CANCELLED
    },
    TicketStatus.CALLED: {
        TicketStatus.IN_PROGRESS,
        TicketStatus.IN_QUEUE,      # Voltar para fila se não compareceu
        TicketStatus.EXPIRED,
        TicketStatus.CANCELLED
    },
    TicketStatus.IN_PROGRESS: {
        TicketStatus.COMPLETED,
        TicketStatus.CANCELLED
    },
    TicketStatus.COMPLETED: set(),  # Estado final
    TicketStatus.CANCELLED: set(),  # Estado final
    TicketStatus.EXPIRED: {
        TicketStatus.CALLED,        # Pode ser reativado
        TicketStatus.CANCELLED
    }
}

# 📊 Categorias de estados para filtros e dashboards
TICKET_STATE_CATEGORIES = {
    "pending_service": {TicketStatus.PAID, TicketStatus.PRINTING, TicketStatus.PRINT_ERROR},
    "waiting": {TicketStatus.IN_QUEUE},
    "active": {TicketStatus.CALLED, TicketStatus.IN_PROGRESS},
    "finished": {TicketStatus.COMPLETED, TicketStatus.CANCELLED, TicketStatus.EXPIRED}
}

# 🎯 Configurações da fila
QUEUE_CONFIG = {
    "max_waiting_time_minutes": 60,        # Tempo máximo na fila antes de expirar
    "priority_boost_minutes": 30,          # Tempo para boost de prioridade
    "service_parallel_limit": 3,           # Máximo de tickets simultâneos por serviço
    "operator_concurrent_limit": 2,        # Máximo de tickets por operador
    "auto_expire_enabled": True,           # Auto-expirar tickets antigos
    "priority_enabled": True               # Sistema de prioridades ativo
}

# 🏆 Regras de priorização
PRIORITY_RULES = {
    # Tickets com erro de impressão têm alta prioridade
    TicketStatus.PRINT_ERROR: QueuePriority.HIGH,
    
    # Tickets reativados de expirados têm baixa prioridade
    "reactivated_expired": QueuePriority.LOW,
    
    # Tickets normais
    TicketStatus.IN_QUEUE: QueuePriority.NORMAL
}

# ⏱️ Tempos de referência (em minutos)
QUEUE_TIMINGS = {
    "normal_waiting": 15,           # Tempo normal de espera
    "warning_waiting": 30,          # Tempo de alerta
    "critical_waiting": 45,         # Tempo crítico
    "auto_expire": 60,              # Auto-expirar após este tempo
    "service_duration": {           # Duração estimada por serviço
        "default": 10,
        "banheira_gelo": 10,
        "bota_compressao": 10
    }
}

# 🎨 Cores para interface (opcional)
TICKET_STATUS_COLORS = {
    TicketStatus.PAID: "#FFA500",           # Laranja
    TicketStatus.PRINTING: "#1E90FF",       # Azul
    TicketStatus.PRINT_ERROR: "#FF6347",    # Vermelho claro
    TicketStatus.IN_QUEUE: "#32CD32",       # Verde
    TicketStatus.CALLED: "#FFD700",         # Dourado
    TicketStatus.IN_PROGRESS: "#9370DB",    # Roxo
    TicketStatus.COMPLETED: "#228B22",      # Verde escuro
    TicketStatus.CANCELLED: "#696969",      # Cinza
    TicketStatus.EXPIRED: "#DC143C"         # Vermelho escuro
}

PRIORITY_COLORS = {
    QueuePriority.HIGH: "#FF4444",          # Vermelho
    QueuePriority.NORMAL: "#44AA44",        # Verde
    QueuePriority.LOW: "#888888"            # Cinza
}

# 📝 Descrições amigáveis
TICKET_STATUS_DESCRIPTIONS = {
    TicketStatus.PAID: "Pagamento confirmado, aguardando impressão",
    TicketStatus.PRINTING: "Comprovante sendo impresso",
    TicketStatus.PRINT_ERROR: "Erro na impressão do comprovante",
    TicketStatus.IN_QUEUE: "Na fila de atendimento",
    TicketStatus.CALLED: "Chamado para atendimento",
    TicketStatus.IN_PROGRESS: "Em atendimento",
    TicketStatus.COMPLETED: "Atendimento concluído",
    TicketStatus.CANCELLED: "Cancelado",
    TicketStatus.EXPIRED: "Expirado por não comparecimento"
}

PRIORITY_DESCRIPTIONS = {
    QueuePriority.HIGH: "Alta prioridade - atender primeiro",
    QueuePriority.NORMAL: "Prioridade normal",
    QueuePriority.LOW: "Baixa prioridade - atender por último"
}

# 🔧 Funções utilitárias
def can_transition(from_status: TicketStatus, to_status: TicketStatus) -> bool:
    """Verifica se uma transição de estado é válida"""
    return to_status in TICKET_TRANSITIONS.get(from_status, set())

def get_valid_transitions(current_status: TicketStatus) -> Set[TicketStatus]:
    """Retorna os estados válidos para transição a partir do estado atual"""
    return TICKET_TRANSITIONS.get(current_status, set())

def get_tickets_by_category(category: str) -> Set[TicketStatus]:
    """Retorna os estados de uma categoria específica"""
    return TICKET_STATE_CATEGORIES.get(category, set())

def is_final_state(status: TicketStatus) -> bool:
    """Verifica se um estado é final (sem transições possíveis)"""
    return len(TICKET_TRANSITIONS.get(status, set())) == 0

def get_status_info(status: TicketStatus) -> Dict:
    """Retorna informações completas sobre um status"""
    return {
        "status": status.value,
        "description": TICKET_STATUS_DESCRIPTIONS.get(status, ""),
        "color": TICKET_STATUS_COLORS.get(status, "#000000"),
        "valid_transitions": [s.value for s in get_valid_transitions(status)],
        "is_final": is_final_state(status)
    }

def calculate_priority(ticket_status: TicketStatus, waiting_minutes: int, print_attempts: int = 0) -> QueuePriority:
    """Calcula a prioridade de um ticket baseado em regras"""
    
    # Tickets com erro de impressão têm alta prioridade
    if ticket_status == TicketStatus.PRINT_ERROR or print_attempts > 1:
        return QueuePriority.HIGH
    
    # Tickets esperando muito tempo ganham prioridade
    if waiting_minutes > QUEUE_TIMINGS["critical_waiting"]:
        return QueuePriority.HIGH
    elif waiting_minutes > QUEUE_TIMINGS["warning_waiting"]:
        return QueuePriority.NORMAL
    
    # Prioridade normal por padrão
    return QueuePriority.NORMAL

def get_waiting_time_status(waiting_minutes: int) -> str:
    """Retorna o status do tempo de espera"""
    if waiting_minutes <= QUEUE_TIMINGS["normal_waiting"]:
        return "normal"
    elif waiting_minutes <= QUEUE_TIMINGS["warning_waiting"]:
        return "warning"
    elif waiting_minutes <= QUEUE_TIMINGS["critical_waiting"]:
        return "critical"
    else:
        return "expired" 