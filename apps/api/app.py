from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import asyncio

# Importações para telemetria e métricas
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge
from config.telemetry import setup_telemetry
from services.logging import setup_logging, StructuredLogger

# Configuração simples para desenvolvimento Docker
app = FastAPI(
    title="Totem API",
    description="API para sistema de autoatendimento com pagamento integrado",
    version="0.2.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://recovery-truck-panel-client.vercel.app",
        "https://recovery-truck-totem-client.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:4173",
        "*"  # Permitir todas as origens para desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Configurar logging estruturado
setup_logging()
logger = StructuredLogger("totem-api")

# Configurar telemetria (OpenTelemetry + Jaeger)
# setup_telemetry(app)

# Configurar métricas Prometheus
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Métricas Prometheus customizadas
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'websocket_active_connections',
    'Conexões WebSocket ativas',
    ['tenant_id']
)

# Importar middleware de métricas
# from middleware.metrics import MetricsMiddleware

# Adicionar middleware de métricas
# app.add_middleware(MetricsMiddleware)

# Importar routers
from routers import tickets, auth, customers, metrics, operator_config, payment_sessions, websocket, ticket_service_progress
from database import get_db

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(operator_config.router, prefix="/operator", tags=["operator"])
app.include_router(payment_sessions.router, prefix="/payment-sessions", tags=["payments"])
app.include_router(websocket.router, prefix="", tags=["websocket"])  # Sem prefixo para evitar /ws/ws
app.include_router(ticket_service_progress.router, prefix="/api", tags=["ticket-service-progress"])

# Endpoint WebSocket de teste
from fastapi import WebSocket

@app.websocket("/ws-test")
async def websocket_test(websocket: WebSocket):
    """Endpoint WebSocket de teste"""
    print(f"🔍 DEBUG - Teste WebSocket recebido")
    await websocket.accept()
    print(f"🔍 DEBUG - Teste WebSocket aceito")
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"🔍 DEBUG - Teste recebeu: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"🔍 DEBUG - Teste erro: {e}")

@app.websocket("/ws-simple")
async def websocket_simple(websocket: WebSocket):
    """Endpoint WebSocket simples para teste"""
    print(f"🔍 DEBUG - WebSocket simples recebido")
    await websocket.accept()
    print(f"🔍 DEBUG - WebSocket simples aceito")
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"🔍 DEBUG - WebSocket simples recebeu: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"🔍 DEBUG - WebSocket simples erro: {e}")

@app.websocket("/ws")
async def websocket_main(websocket: WebSocket):
    """Endpoint WebSocket principal simplificado"""
    print(f"🔍 DEBUG - WebSocket principal recebido")
    print(f"🔍 DEBUG - Query params: {websocket.query_params}")
    print(f"🔍 DEBUG - Headers: {websocket.headers}")
    print(f"🔍 DEBUG - URL: {websocket.url}")
    
    try:
        await websocket.accept()
        print(f"🔍 DEBUG - WebSocket principal aceito!")
        
        # Loop principal para receber mensagens
        while True:
            try:
                # Aguardar mensagem do cliente
                data = await websocket.receive_text()
                print(f"🔍 DEBUG - Mensagem recebida: {data}")
                
                # Processar mensagem (se necessário)
                # Por enquanto, apenas ecoar de volta
                await websocket.send_text(f"Echo: {data}")
                
            except Exception as e:
                print(f"❌ ERRO ao processar mensagem: {e}")
                break
                
    except Exception as e:
        print(f"❌ ERRO geral no endpoint WebSocket: {e}")
        import traceback
        traceback.print_exc()
        # Tentar fechar a conexão se ainda estiver aberta
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass

@app.websocket("/websocket")
async def websocket_alternative(websocket: WebSocket):
    """Endpoint WebSocket alternativo"""
    print(f"🔍 DEBUG - WebSocket alternativo recebido")
    await websocket.accept()
    print(f"🔍 DEBUG - WebSocket alternativo aceito!")
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"🔍 DEBUG - Mensagem recebida: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"🔍 DEBUG - Erro: {e}")

@app.websocket("/ws-new")
async def websocket_new(websocket: WebSocket):
    """Endpoint WebSocket novo"""
    print(f"🔍 DEBUG - WebSocket novo recebido")
    await websocket.accept()
    print(f"🔍 DEBUG - WebSocket novo aceito!")
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"🔍 DEBUG - Mensagem recebida: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"🔍 DEBUG - Erro: {e}")



@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Verificar conectividade com banco de dados
        from database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.2.0",
            "message": "Totem API funcionando!",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": "connected",
            "telemetry": "enabled"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Totem API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Global exception: {str(exc)}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    ) 