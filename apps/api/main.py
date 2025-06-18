from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import asyncio

from routers import auth, tickets, services, payment_sessions, metrics, websocket, terminals
from database import engine, Base
from config.telemetry import setup_telemetry
from services.logging import setup_logging
from services.offline import offline_manager
from services.printer import printer_manager
from services.payment.terminal_manager import terminal_manager
from .config.settings import settings
from .middleware.rate_limit import rate_limit_middleware

# Configura o logging
setup_logging()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Totem API",
    description="API para sistema de autoatendimento com pagamento integrado",
    version="0.2.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura o OpenTelemetry
setup_telemetry(app)

# Adiciona o middleware de rate limiting
app.middleware("http")(rate_limit_middleware)

# Register routers
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(services.router)
app.include_router(payment_sessions.router)
app.include_router(metrics.router)
app.include_router(websocket.router)
app.include_router(terminals.router)

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação"""
    # Configurar impressora padrão
    await setup_default_printer()
    
    # Configurar terminais de pagamento
    await setup_default_terminals()
    
    # Inicia a tarefa de sincronização offline
    await offline_manager.start_sync_task()
    
    # Inicia a tarefa de impressão
    await printer_manager.start_print_task()

async def setup_default_printer():
    """Configura a impressora padrão baseada em variáveis de ambiente"""
    printer_config = {
        "type": os.getenv("PRINTER_TYPE", "usb"),
        "vendor_id": int(os.getenv("PRINTER_VENDOR_ID", "0x0483"), 16),
        "product_id": int(os.getenv("PRINTER_PRODUCT_ID", "0x5740"), 16),
        "host": os.getenv("PRINTER_HOST", "192.168.1.100"),
        "port": int(os.getenv("PRINTER_PORT", "9100")),
        "serial_port": os.getenv("PRINTER_SERIAL_PORT", "/dev/ttyUSB0"),
        "baudrate": int(os.getenv("PRINTER_BAUDRATE", "9600"))
    }
    
    try:
        printer_manager.add_printer("default", printer_config)
        print(f"✅ Impressora padrão configurada: {printer_config['type']}")
    except Exception as e:
        print(f"⚠️ Erro ao configurar impressora: {e}")
        # Configurar impressora "mock" para desenvolvimento
        printer_manager.add_printer("default", {"type": "mock"})
        print("✅ Impressora mock configurada para desenvolvimento")

async def setup_default_terminals():
    """Configura terminais de pagamento baseado em variáveis de ambiente"""
    terminal_type = os.getenv("TERMINAL_TYPE", "mock")
    
    # Configuração padrão para desenvolvimento
    default_configs = {
        "default": {
            "terminal": {
                "type": terminal_type,
                "connection_type": os.getenv("TERMINAL_CONNECTION", "serial"),
                "port": os.getenv("TERMINAL_PORT", "COM1"),
                "baudrate": int(os.getenv("TERMINAL_BAUDRATE", "115200" if terminal_type == "stone" else "9600")),
                "timeout": int(os.getenv("TERMINAL_TIMEOUT", "30")),
                "simulate_delays": os.getenv("TERMINAL_SIMULATE_DELAYS", "true").lower() == "true",
                "failure_rate": float(os.getenv("TERMINAL_FAILURE_RATE", "0.1")),
            }
        }
    }
    
    # Configurações específicas por tipo de terminal
    if terminal_type == "stone":
        default_configs["default"]["terminal"]["stone"] = {
            "merchant_id": os.getenv("STONE_MERCHANT_ID", "123456789"),
            "terminal_id": os.getenv("STONE_TERMINAL_ID", "TERM001")
        }
    elif terminal_type == "sicredi":
        default_configs["default"]["terminal"]["sicredi"] = {
            "merchant_id": os.getenv("SICREDI_MERCHANT_ID", "123456789012345"),
            "terminal_id": os.getenv("SICREDI_TERMINAL_ID", "RECOVERY1"),
            "pos_id": os.getenv("SICREDI_POS_ID", "001")
        }
        # Sicredi usa baudrate 9600 por padrão
        default_configs["default"]["terminal"]["baudrate"] = int(os.getenv("TERMINAL_BAUDRATE", "9600"))
    
    try:
        await terminal_manager.initialize(default_configs)
        print(f"✅ Terminal Manager inicializado: {terminal_type}")
        print(f"   - Tipo: {terminal_type}")
        print(f"   - Conexão: {default_configs['default']['terminal']['connection_type']}")
        print(f"   - Porta: {default_configs['default']['terminal']['port']}")
        print(f"   - Baudrate: {default_configs['default']['terminal']['baudrate']}")
    except Exception as e:
        print(f"⚠️ Erro ao inicializar Terminal Manager: {e}")
        # Configurar apenas terminal mock para desenvolvimento
        mock_config = {
            "default": {
                "terminal": {
                    "type": "mock",
                    "simulate_delays": False,
                    "failure_rate": 0.0
                }
            }
        }
        await terminal_manager.initialize(mock_config)
        print("✅ Terminal Manager inicializado com configuração mock")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no encerramento da aplicação"""
    # Para a tarefa de sincronização offline
    await offline_manager.stop_sync_task()
    
    # Para a tarefa de impressão
    await printer_manager.stop_print_task()
    
    # Encerra o Terminal Manager
    await terminal_manager.shutdown()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Verificar status da impressora
    printer_status = "✅ Ready" if "default" in printer_manager.printers else "❌ Not configured"
    queue_size = printer_manager.print_queue.qsize()
    
    # Verificar status dos terminais
    terminal_stats = terminal_manager.get_statistics()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.2.0",
        "flow": "payment_session -> payment_confirmed -> ticket_created -> ticket_printed -> queue",
        "printer": {
            "status": printer_status,
            "queue_size": queue_size,
            "configured_printers": list(printer_manager.printers.keys())
        },
        "terminals": {
            "total": terminal_stats["total_terminals"],
            "connected": terminal_stats["connected"],
            "busy": terminal_stats["busy"],
            "error": terminal_stats["error"],
            "monitoring": terminal_stats["monitoring_active"]
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    ) 