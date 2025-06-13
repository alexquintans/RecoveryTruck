from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import asyncio

from routers import auth, tickets, services, payments, metrics, websocket
from database import engine, Base
from config.telemetry import setup_telemetry
from services.logging import setup_logging
from services.offline import offline_manager
from services.printer import printer_manager
from .config.settings import settings
from .middleware.rate_limit import rate_limit_middleware

# Configura o logging
setup_logging()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Totem API",
    description="API para sistema de autoatendimento com pagamento integrado",
    version="0.1.0"
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
app.include_router(payments.router)
app.include_router(metrics.router)
app.include_router(websocket.router)

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação"""
    # Inicia a tarefa de sincronização offline
    await offline_manager.start_sync_task()
    
    # Inicia a tarefa de impressão
    await printer_manager.start_print_task()

@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no encerramento da aplicação"""
    # Para a tarefa de sincronização offline
    await offline_manager.stop_sync_task()
    
    # Para a tarefa de impressão
    await printer_manager.stop_print_task()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
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