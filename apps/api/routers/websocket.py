from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from services.websocket import manager
from security import verify_token
from models import Operator
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

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
    
    try:
        # Aceitar a conexão primeiro - CRÍTICO para resolver 403
        await websocket.accept()
        
        # Extrair parâmetros da query string
        tenant_id = websocket.query_params.get("tenant_id")
        client_type = websocket.query_params.get("client_type")
        token = websocket.query_params.get("token")
        
        # Validações básicas
        if not tenant_id or not client_type:
            await websocket.close(code=4000, reason="Missing tenant_id or client_type")
            return
        
        # Valida o tipo de cliente
        if client_type not in ["operator", "totem", "display"]:
            await websocket.close(code=4000, reason="Invalid client type")
            return

        # TEMPORÁRIO: Pular validação de token para testar
        
        # Conecta o cliente
        await manager.connect(websocket, tenant_id, client_type)
        
        try:
            # Loop principal para receber mensagens
            while True:
                try:
                    # Aguardar mensagem do cliente
                    data = await websocket.receive_text()
                    
                    # Processar mensagem (se necessário)
                    # Por enquanto, apenas ecoar de volta
                    await websocket.send_text(f"Echo: {data}")
                    
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    print(f"❌ ERRO ao processar mensagem: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ ERRO no loop principal: {e}")
        finally:
            # Desconectar cliente
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