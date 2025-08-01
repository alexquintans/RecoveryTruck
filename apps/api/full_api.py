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
from fastapi.websockets import WebSocket, WebSocketDisconnect

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
        # NÃO FALHAR - apenas continuar

# Importação direta do router websocket para garantir que está disponível
try:
    from routers import websocket
    print("✅ Router websocket importado diretamente")
    # Garantir que o router websocket está na lista de routers carregados
    if "websocket" not in loaded_routers:
        loaded_routers["websocket"] = websocket.router
        print("✅ Router websocket adicionado manualmente")
except Exception as e:
    print(f"⚠️ Erro ao importar router websocket diretamente: {e}")
    router_errors["websocket"] = str(e)
    # NÃO FALHAR - apenas continuar

# Tentar importar dependências do banco
try:
    from database import engine, Base, get_db
    DATABASE_AVAILABLE = True
    print("✅ Database importado com sucesso")
except ImportError as e:
    print(f"⚠️ Database não pôde ser importado: {e}")
    DATABASE_AVAILABLE = False
    # NÃO FALHAR - apenas continuar

# Configuração da aplicação - VERSÃO SIMPLIFICADA PARA TESTE
app = FastAPI(
    title="🏪 Sistema de Totem - API Completa",
    description="API para sistema de autoatendimento com pagamento integrado",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - DEVE VIR ANTES DOS ROUTERS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens para desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Headers específicos para WebSocket
    expose_headers=["*"],
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
    "websocket": {"prefix": "", "tags": ["websocket"]},  # Sem prefixo para evitar /ws/ws
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
        print(f"✅ Router {router_name} registrado com sucesso")
    except Exception as e:
        print(f"⚠️ Erro ao registrar router {router_name}: {e}")
        # NÃO FALHAR - apenas continuar

# Endpoint WebSocket de teste direto na aplicação principal
@app.websocket("/ws-test")
async def websocket_test_direct(websocket: WebSocket):
    """Endpoint WebSocket de teste direto na aplicação principal"""
    print(f"🔍 DEBUG - Teste WebSocket direto recebido")
    print(f"🔍 DEBUG - Headers: {websocket.headers}")
    print(f"🔍 DEBUG - URL: {websocket.url}")
    print(f"🔍 DEBUG - Client: {websocket.client}")
    
    try:
        await websocket.accept()
        print(f"🔍 DEBUG - Teste WebSocket direto aceito com sucesso!")
        
        while True:
            data = await websocket.receive_text()
            print(f"🔍 DEBUG - Teste direto recebeu: {data}")
            await websocket.send_text(f"Echo direto: {data}")
    except WebSocketDisconnect:
        print(f"🔍 DEBUG - Teste direto desconectado")
    except Exception as e:
        print(f"🔍 DEBUG - Teste direto erro: {e}")
        import traceback
        traceback.print_exc()

# Endpoint WebSocket simples para teste - SEM router
@app.websocket("/ws")
async def websocket_simple_direct(websocket: WebSocket):
    """Endpoint WebSocket simples direto na aplicação para teste"""
    print(f"🔍 DEBUG - WebSocket simples direto recebido")
    print(f"🔍 DEBUG - Headers: {websocket.headers}")
    print(f"🔍 DEBUG - URL: {websocket.url}")
    print(f"🔍 DEBUG - Query params: {websocket.query_params}")
    
    try:
        await websocket.accept()
        print(f"🔍 DEBUG - WebSocket simples direto aceito com sucesso!")
        
        # Extrair parâmetros da query string
        tenant_id = websocket.query_params.get("tenant_id")
        client_type = websocket.query_params.get("client_type")
        
        print(f"🔍 DEBUG - tenant_id: {tenant_id}")
        print(f"🔍 DEBUG - client_type: {client_type}")
        
        while True:
            data = await websocket.receive_text()
            print(f"🔍 DEBUG - WebSocket simples direto recebeu: {data}")
            await websocket.send_text(f"Echo simples direto: {data}")
    except WebSocketDisconnect:
        print(f"🔍 DEBUG - WebSocket simples direto desconectado")
    except Exception as e:
        print(f"🔍 DEBUG - WebSocket simples direto erro: {e}")
        import traceback
        traceback.print_exc()



@app.on_event("startup")
async def startup_event():
    """Evento de startup com delay para garantir inicialização completa."""
    import time
    import subprocess
    import os
    
    print("🚀 Iniciando API completa...")
    print("🔄 VERSÃO: 2025-07-31 18:40 - DEBUG MIGRATIONS")
    
    # Debug: verificar variáveis de ambiente
    print(f"🔍 DEBUG - ENVIRONMENT: {os.getenv('ENVIRONMENT')}")
    print(f"🔍 DEBUG - DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT_SET'}")
    
    # Executar migrations sempre que DATABASE_URL estiver disponível
    if os.getenv("DATABASE_URL"):
        try:
            print("🗄️ Executando migrations do banco de dados...")
            # Definir variável de ambiente para o Alembic
            env = os.environ.copy()
            env['DATABASE_URL'] = os.getenv('DATABASE_URL', '')
            
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd="apps/api",
                capture_output=True,
                text=True,
                env=env
            )
            if result.returncode == 0:
                print("✅ Migrations executadas com sucesso!")
                print(f"📝 Output: {result.stdout}")
            else:
                print(f"⚠️ Erro nas migrations: {result.stderr}")
                print(f"📝 Output: {result.stdout}")
        except Exception as e:
            print(f"⚠️ Erro ao executar migrations: {e}")
    else:
        print("⚠️ DATABASE_URL não encontrada, pulando migrations")
    
    time.sleep(3)  # Aguarda 3 segundos para garantir inicialização
    print("✅ API completa pronta!")
    
    # Log dos routers carregados
    print(f"📊 Routers carregados: {len(loaded_routers)}/{len(AVAILABLE_ROUTERS)}")
    for router_name in loaded_routers:
        print(f"  ✅ {router_name}")
    
    if router_errors:
        print("⚠️ Routers com erro:")
        for router_name, error in router_errors.items():
            print(f"  ❌ {router_name}: {error}")

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

@app.get("/test", summary="🧪 Test endpoint", description="Endpoint simples para teste")
async def test_endpoint():
    """Endpoint simples para teste."""
    return {"message": "API is working!", "timestamp": datetime.utcnow().isoformat()}

@app.get("/debug", summary="🔍 Debug endpoint", description="Endpoint para debug das variáveis de ambiente")
async def debug_endpoint():
    """Endpoint para debug das variáveis de ambiente."""
    import os
    return {
        "message": "Debug info",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "NOT_SET"),
        "database_url": "SET" if os.getenv("DATABASE_URL") else "NOT_SET",
        "jwt_secret": "SET" if os.getenv("JWT_SECRET") else "NOT_SET",
        "cors_origins": os.getenv("CORS_ORIGINS", "NOT_SET")
    }

@app.get("/migrate", summary="🗄️ Executar migrations", description="Executar migrations manualmente")
async def migrate_endpoint():
    """Endpoint para executar migrations manualmente."""
    import os
    import subprocess
    
    try:
        print("🗄️ Executando migrations manualmente...")
        
        # Definir variável de ambiente para o Alembic
        env = os.environ.copy()
        env['DATABASE_URL'] = os.getenv('DATABASE_URL', '')
        
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd="apps/api",
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            return {
                "message": "Migrations executadas com sucesso!",
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        else:
            return {
                "message": "Erro ao executar migrations",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
    except Exception as e:
        return {
            "message": f"Erro ao executar migrations: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "error": str(e)
        }

@app.get("/seed", summary="🌱 Inserir dados de seed", description="Inserir tenant e operador de exemplo")
async def seed_endpoint():
    """Endpoint para inserir dados de seed."""
    import os
    import subprocess
    
    try:
        print("🌱 Inserindo dados de seed...")
        
        # Definir variável de ambiente para o psql
        env = os.environ.copy()
        env['DATABASE_URL'] = os.getenv('DATABASE_URL', '')
        
        # Ler o arquivo seed_data.sql
        with open('apps/api/seed_data.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Executar via psql
        result = subprocess.run(
            ["psql", os.getenv('DATABASE_URL', '')],
            input=sql_content,
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            return {
                "message": "Dados de seed inseridos com sucesso!",
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        else:
            return {
                "message": "Erro ao inserir dados de seed",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
    except Exception as e:
        return {
            "message": f"Erro ao inserir dados de seed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "error": str(e)
        }

@app.get("/check-data", summary="🔍 Verificar dados no banco", description="Verificar tenants e operadores no banco")
async def check_data_endpoint():
    """Endpoint para verificar dados no banco."""
    import os
    import subprocess
    
    try:
        print("🔍 Verificando dados no banco...")
        
        # Query para verificar dados
        query = """
        SELECT 'Tenants:' as info;
        SELECT id, name, cnpj, is_active FROM tenants;
        
        SELECT 'Operadores:' as info;
        SELECT id, name, email, tenant_id, is_active FROM operators;
        """
        
        # Definir variável de ambiente para o psql
        env = os.environ.copy()
        env['DATABASE_URL'] = os.getenv('DATABASE_URL', '')
        
        # Executar via psql
        result = subprocess.run(
            ["psql", os.getenv('DATABASE_URL', '')],
            input=query,
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            return {
                "message": "Dados verificados com sucesso!",
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "data": result.stdout,
                "stderr": result.stderr
            }
        else:
            return {
                "message": "Erro ao verificar dados",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "data": result.stdout,
                "stderr": result.stderr
            }
    except Exception as e:
        return {
            "message": f"Erro ao verificar dados: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "error": str(e)
        }

@app.get("/test-auth", summary="🔐 Testar autenticação", description="Testar autenticação diretamente")
async def test_auth_endpoint():
    """Endpoint para testar autenticação diretamente."""
    try:
        from apps.api.auth import authenticate_operator
        from apps.api.database import get_db
        
        # Testar autenticação
        db = next(get_db())
        
        # Tentar autenticar
        result = authenticate_operator(
            db=db,
            email="admin@exemplo.com",
            password="123456"
        )
        
        if result:
            return {
                "message": "Autenticação bem-sucedida!",
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "operator_id": str(result.id),
                "operator_name": result.name,
                "tenant_id": str(result.tenant_id)
            }
        else:
            return {
                "message": "Autenticação falhou",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": "Email ou senha incorretos"
            }
    except Exception as e:
        return {
            "message": f"Erro ao testar autenticação: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "error": str(e)
        }

@app.get("/generate-hash", summary="🔐 Gerar hash correto", description="Gerar hash usando o mesmo método do sistema")
async def generate_hash_endpoint():
    """Endpoint para gerar hash usando o mesmo método do sistema."""
    try:
        from apps.api.security import get_password_hash, verify_password
        
        password = "123456"
        hash_generated = get_password_hash(password)
        
        # Testar verificação
        is_valid = verify_password(password, hash_generated)
        
        return {
            "message": "Hash gerado com sucesso!",
            "timestamp": datetime.utcnow().isoformat(),
            "success": True,
            "password": password,
            "hash_generated": hash_generated,
            "verification_test": is_valid,
            "sql_update": f"""
-- Atualizar hash do operador
UPDATE operators 
SET password_hash = '{hash_generated}'
WHERE email = 'admin@exemplo.com';
"""
        }
    except Exception as e:
        return {
            "message": f"Erro ao gerar hash: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "error": str(e)
        }

@app.post("/update-password-hash", summary="🔐 Atualizar hash da senha", description="Atualizar hash da senha do operador admin")
async def update_password_hash_endpoint():
    """Endpoint para atualizar hash da senha do operador admin."""
    try:
        from apps.api.security import get_password_hash
        from apps.api.database import get_db
        from apps.api.models import Operator
        
        password = "123456"
        hash_generated = get_password_hash(password)
        
        # Atualizar no banco
        db = next(get_db())
        operator = db.query(Operator).filter(Operator.email == "admin@exemplo.com").first()
        
        if not operator:
            return {
                "message": "Operador não encontrado",
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": "Operador admin@exemplo.com não encontrado"
            }
        
        # Atualizar hash
        operator.password_hash = hash_generated
        db.commit()
        
        return {
            "message": "Hash atualizado com sucesso!",
            "timestamp": datetime.utcnow().isoformat(),
            "success": True,
            "operator_email": "admin@exemplo.com",
            "hash_updated": hash_generated,
            "operator_id": str(operator.id)
        }
    except Exception as e:
        return {
            "message": f"Erro ao atualizar hash: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "error": str(e)
        }

@app.get("/health", summary="🏥 Health check", description="Verificação de saúde da API")
async def health_check():
    """Health check endpoint simplificado."""
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": "production",
        "message": "API is running!"
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