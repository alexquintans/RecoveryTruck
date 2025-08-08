from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from services.websocket import manager
from security import verify_token
from models import Operator
from database import get_db
from sqlalchemy.orm import Session
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/test")
async def websocket_test(websocket: WebSocket):
    """Endpoint WebSocket de teste simples"""
    print(f"🔍 DEBUG - Teste WebSocket recebido")
    await websocket.accept()
    print(f"🔍 DEBUG - Teste WebSocket aceito")
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"🔍 DEBUG - Teste recebeu: {data}")
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print(f"🔍 DEBUG - Teste desconectado")
    except Exception as e:
        print(f"🔍 DEBUG - Teste erro: {e}")

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):
    """Endpoint WebSocket para atualizações em tempo real"""
    
    print(f"🔍 DEBUG - WebSocket endpoint recebido")
    print(f"🔍 DEBUG - Headers: {websocket.headers}")
    print(f"🔍 DEBUG - Query params: {websocket.query_params}")
    print(f"🔍 DEBUG - URL: {websocket.url}")
    
    try:
        # Aceitar a conexão primeiro - CRÍTICO para resolver 403
        await websocket.accept()
        print(f"🔍 DEBUG - WebSocket aceito com sucesso!")
        
        # Extrair parâmetros da query string
        tenant_id = websocket.query_params.get("tenant_id")
        client_type = websocket.query_params.get("client_type")
        token = websocket.query_params.get("token")
        
        print(f"🔍 DEBUG - tenant_id: {tenant_id}")
        print(f"🔍 DEBUG - client_type: {client_type}")
        print(f"🔍 DEBUG - token: {token[:20] if token else 'None'}...")
        
        # Validações básicas
        if not tenant_id:
            print(f"❌ ERRO: tenant_id não fornecido")
            await websocket.close(code=4000, reason="Missing tenant_id")
            return
            
        if not client_type:
            print(f"❌ ERRO: client_type não fornecido")
            await websocket.close(code=4000, reason="Missing client_type")
            return
        
        # Valida o tipo de cliente
        if client_type not in ["operator", "totem", "display"]:
            print(f"❌ ERRO: client_type inválido: {client_type}")
            await websocket.close(code=4000, reason="Invalid client type")
            return

        # Validação de token para operadores
        if client_type == "operator" and token:
            try:
                # Verificar token JWT
                payload = verify_token(token)
                operator_id = payload.get("sub")
                print(f"🔍 DEBUG - Token válido para operador: {operator_id}")
            except Exception as e:
                print(f"❌ ERRO: Token inválido: {e}")
                await websocket.close(code=4001, reason="Invalid token")
                return
        elif client_type == "operator" and not token:
            print(f"⚠️ AVISO: Operador sem token - permitindo conexão para teste")
        
        # Conecta o cliente
        print(f"🔍 DEBUG - Conectando cliente {client_type} para tenant {tenant_id}")
        await manager.connect(websocket, tenant_id, client_type)
        print(f"🔍 DEBUG - Cliente conectado com sucesso!")
        
        # Enviar mensagem de confirmação
        welcome_message = {
            "type": "connection_established",
            "data": {
                "tenant_id": tenant_id,
                "client_type": client_type,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
        await websocket.send_json(welcome_message)
        print(f"🔍 DEBUG - Mensagem de boas-vindas enviada")
        
        try:
            # Loop principal para receber mensagens
            while True:
                try:
                    # Aguardar mensagem do cliente
                    data = await websocket.receive_text()
                    print(f"🔍 DEBUG - Mensagem recebida: {data}")
                    
                    # Tentar parsear como JSON
                    try:
                        parsed_data = json.loads(data)
                        print(f"🔍 DEBUG - Dados parseados: {parsed_data}")
                    except json.JSONDecodeError:
                        print(f"🔍 DEBUG - Dados não são JSON válido, tratando como texto")
                        parsed_data = {"type": "text", "data": data}
                    
                    # Processar mensagem baseada no tipo
                    if parsed_data.get("type") == "ping":
                        response = {"type": "pong", "data": {"timestamp": "2024-01-01T00:00:00Z"}}
                        await websocket.send_json(response)
                        print(f"🔍 DEBUG - Pong enviado")
                    else:
                        # Echo da mensagem recebida
                        response = {"type": "echo", "data": parsed_data}
                        await websocket.send_json(response)
                        print(f"🔍 DEBUG - Echo enviado")
                    
                except WebSocketDisconnect:
                    print(f"🔍 DEBUG - Cliente desconectado")
                    break
                except Exception as e:
                    print(f"❌ ERRO ao processar mensagem: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ ERRO no loop principal: {e}")
        finally:
            # Desconectar cliente
            print(f"🔍 DEBUG - Desconectando cliente")
            manager.disconnect(websocket, tenant_id, client_type)
            
    except Exception as e:
        print(f"❌ ERRO geral no endpoint WebSocket: {e}")
        import traceback
        traceback.print_exc()
        # Tentar fechar a conexão se ainda estiver aberta
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass 