import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao Python path para importações
current_dir = str(Path(__file__).parent)
sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import asyncio
import traceback

# Lista de routers disponíveis para carregar
AVAILABLE_ROUTERS = [
    "auth", "tickets", "services", "payment_sessions", 
    "metrics", "websocket", "terminals", "operation", 
    "operator_config", "webhooks", "notifications", "customers"
]

# Dicionário para rastrear routers carregados
loaded_routers = {}
router_errors = {}

# Tentar importar cada router individualmente
for router_name in AVAILABLE_ROUTERS:
    try:
        module = __import__(f"routers.{router_name}", fromlist=[router_name])
        loaded_routers[router_name] = getattr(module, 'router')
        print(f"✅ Router {router_name} carregado com sucesso")
    except Exception as e:
        router_errors[router_name] = str(e)
        print(f"⚠️ Erro ao carregar router {router_name}: {e}")

# Tentar importar dependências do banco
try:
    from database import engine, Base, get_db
    DATABASE_AVAILABLE = True
    print("✅ Database importado com sucesso")
except ImportError as e:
    print(f"⚠️ Database não pôde ser importado: {e}")
    DATABASE_AVAILABLE = False

# Configuração da aplicação
app = FastAPI(
    title="🏪 Sistema de Totem - API Completa",
    description="""
    ## API Completa do Sistema de Autoatendimento
    
    Esta API fornece todos os endpoints necessários para o funcionamento do sistema de totem:
    
    ### 🔐 Autenticação
    - Login e registro de operadores
    - Gerenciamento de tokens JWT
    
    ### 🎫 Gestão de Tickets  
    - Criação, consulta e atualização de tickets
    - Sistema de fila inteligente
    - Controle de status e prioridades
    
    ### 💳 Pagamentos
    - Sessões de pagamento
    - Integração com múltiplos provedores
    - Webhooks para confirmação
    
    ### 🖥️ Terminais
    - Configuração de terminais de pagamento
    - Gerenciamento de equipamentos
    
    ### 📊 Métricas e Monitoramento
    - Métricas do sistema
    - Logs e auditoria
    
    ### 🔔 Notificações
    - Sistema de notificações sonoras
    - Configurações por operador
    
    ### 🌐 WebSockets
    - Comunicação em tempo real
    - Atualizações da fila
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "authentication", "description": "🔐 Autenticação e autorização"},
        {"name": "tickets", "description": "🎫 Gestão de tickets e fila"},
        {"name": "services", "description": "🛠️ Serviços disponíveis"},
        {"name": "payments", "description": "💳 Sessões de pagamento"},
        {"name": "webhooks", "description": "🔗 Webhooks de pagamento"},
        {"name": "terminals", "description": "🖥️ Terminais de pagamento"},
        {"name": "metrics", "description": "📊 Métricas e monitoramento"},
        {"name": "websocket", "description": "🌐 Comunicação em tempo real"},
        {"name": "operation", "description": "⚙️ Operação do sistema"},
        {"name": "operator-config", "description": "👤 Configurações de operador"},
        {"name": "notifications", "description": "🔔 Sistema de notificações"},
        {"name": "customers", "description": "👤 Gestão de clientes"}
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens para desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers carregados
# Os routers já têm seus próprios prefixes definidos, não precisamos duplicar
router_configs = {
    "auth": {"prefix": "/auth", "tags": ["authentication"]},
    "tickets": {"prefix": "/tickets", "tags": ["tickets"]},
    "services": {"prefix": "/services", "tags": ["services"]},
    "payment_sessions": {"prefix": "/payment_sessions", "tags": ["payments"]},
    "webhooks": {"prefix": "/webhooks", "tags": ["webhooks"]},
    "terminals": {"prefix": "/terminals", "tags": ["terminals"]},
    "metrics": {"prefix": "/metrics", "tags": ["metrics"]},
    "websocket": {"prefix": "/ws", "tags": ["websocket"]},
    "operation": {"prefix": "/operation", "tags": ["operation"]},
    "operator_config": {"prefix": "/operator", "tags": ["operator-config"]},
    "notifications": {"prefix": "/notifications", "tags": ["notifications"]},
    "customers": {"prefix": "/customers", "tags": ["customers"]}
}

# Incluir routers na aplicação
for router_name, router in loaded_routers.items():
    config = router_configs.get(router_name, {"prefix": f"/{router_name}", "tags": [router_name]})
    try:
        app.include_router(router, prefix=config["prefix"], tags=config["tags"])
        print(f"✅ Router {router_name} registrado em {config['prefix']}")
    except Exception as e:
        print(f"❌ Erro ao registrar router {router_name}: {e}")

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação"""
    print("🚀 Iniciando Sistema de Totem API...")
    print("📄 Arquivos carregados no sys.modules:")
    for name, module in sys.modules.items():
        if module and hasattr(module, "__file__") and module.__file__:
            if "models" in module.__file__:
                print(f"   {name}: {module.__file__}")
    
    print(f"📊 Status dos Routers:")
    print(f"   ✅ Carregados: {len(loaded_routers)}")
    print(f"   ❌ Com erro: {len(router_errors)}")
    
    for name in loaded_routers:
        print(f"   ✅ {name}")
    
    for name, error in router_errors.items():
        print(f"   ❌ {name}: {error}")
    
    # Criar tabelas do banco se disponível
    # if DATABASE_AVAILABLE:
    #     try:
    #         Base.metadata.create_all(bind=engine)
    #         print("✅ Tabelas do banco de dados criadas/verificadas")
    #     except Exception as e:
    #         print(f"⚠️ Erro ao criar tabelas: {e}")
    
    print("✅ API inicializada com sucesso!")

@app.get("/", summary="🏪 Página inicial", description="Endpoint raiz da API do Sistema de Totem")
async def root():
    """Endpoint raiz com informações do sistema."""
    return {
        "message": "🏪 Sistema de Totem - API Completa",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc", 
        "health": "/health",
        "status": "running",
        "description": "API para sistema de autoatendimento com pagamento integrado",
        "features": {
            "routers_loaded": len(loaded_routers),
            "routers_with_errors": len(router_errors),
            "database_connected": DATABASE_AVAILABLE,
            "available_modules": list(loaded_routers.keys())
        }
    }

@app.get("/health", summary="🏥 Health check", description="Verificação de saúde da API")
async def health_check():
    """Health check endpoint com informações detalhadas."""
    
    status = "healthy"
    details = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": "docker-development",
        "components": {
            "api": "✅ Running",
            "routers": f"✅ {len(loaded_routers)}/{len(AVAILABLE_ROUTERS)} loaded",
            "database": "✅ Available" if DATABASE_AVAILABLE else "⚠️ Not available"
        },
        "loaded_routers": list(loaded_routers.keys()),
        "router_errors": router_errors
    }
    
    # Verificar conexão com banco se disponível
    if DATABASE_AVAILABLE:
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            details["components"]["database"] = "✅ Connected and responsive"
        except Exception as e:
            details["components"]["database"] = f"❌ Connection error: {str(e)}"
            status = "degraded"
    
    if router_errors:
        status = "degraded"
    
    return {
        "status": status,
        **details
    }

@app.get("/info", summary="ℹ️ Informações da API", description="Informações detalhadas sobre a API e recursos")
async def api_info():
    """Informações sobre a API e seus recursos."""
    
    available_endpoints = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            available_endpoints.append({
                "path": route.path,
                "methods": sorted(list(route.methods) - {"HEAD", "OPTIONS"}),
                "name": getattr(route, 'name', 'unknown'),
                "summary": getattr(route, 'summary', ''),
                "tags": getattr(route, 'tags', [])
            })
    
    return {
        "api_name": "🏪 Sistema de Totem",
        "version": "1.0.0",
        "description": "API completa para sistema de autoatendimento com pagamento integrado",
        "environment": "docker-development",
        "features": {
            "authentication": "auth" in loaded_routers,
            "ticket_management": "tickets" in loaded_routers,
            "payment_processing": "payment_sessions" in loaded_routers,
            "payment_webhooks": "webhooks" in loaded_routers,
            "terminal_management": "terminals" in loaded_routers,
            "metrics_collection": "metrics" in loaded_routers,
            "websocket_support": "websocket" in loaded_routers,
            "operator_configuration": "operator_config" in loaded_routers,
            "notifications": "notifications" in loaded_routers,
            "service_management": "services" in loaded_routers,
            "operation_controls": "operation" in loaded_routers,
            "customer_management": "customers" in loaded_routers
        },
        "endpoints_count": len([e for e in available_endpoints if e["methods"]]),
        "routers": {
            "loaded": len(loaded_routers),
            "total": len(AVAILABLE_ROUTERS),
            "success_rate": f"{len(loaded_routers)/len(AVAILABLE_ROUTERS)*100:.1f}%"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler com logging detalhado."""
    print(f"❌ Global exception: {type(exc).__name__}: {str(exc)}")
    print(f"📍 Path: {request.url.path}")
    print(f"🔍 Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
            "message": str(exc),
            "path": str(request.url.path)
        }
    )

@app.get("/routes", summary="🗺️ Rotas disponíveis", description="Lista todas as rotas disponíveis na API")
async def list_routes():
    """Lista todas as rotas disponíveis com detalhes."""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = sorted(list(route.methods) - {"HEAD", "OPTIONS"})
            if methods:  # Só incluir rotas com métodos HTTP válidos
                routes.append({
                    "path": route.path,
                    "methods": methods,
                    "name": getattr(route, 'name', 'unknown'),
                    "summary": getattr(route, 'summary', ''),
                    "description": getattr(route, 'description', ''),
                    "tags": getattr(route, 'tags', [])
                })
    
    # Agrupar por tags
    routes_by_tag = {}
    for route in routes:
        tags = route.get('tags', ['untagged'])
        for tag in tags:
            if tag not in routes_by_tag:
                routes_by_tag[tag] = []
            routes_by_tag[tag].append(route)
    
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x['path']),
        "by_tag": routes_by_tag,
        "routers_status": {
            "loaded": list(loaded_routers.keys()),
            "errors": router_errors
        }
    } 