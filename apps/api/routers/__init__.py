# Routers do sistema de totem
from . import auth
from . import tickets
from . import customers
from . import metrics
from . import operator_config
from . import payment_sessions
from . import websocket
from . import services
from . import webhooks
from . import terminals
from . import operation
from . import notifications

__all__ = [
    "auth",
    "tickets", 
    "customers",
    "metrics",
    "operator_config",
    "payment_sessions",
    "websocket",
    "services",
    "webhooks",
    "terminals",
    "operation",
    "notifications"
] 