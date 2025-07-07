from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from services.websocket import manager
from security import verify_token
from models import Operator
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str = None,
    client_type: str = None,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Endpoint WebSocket para atualizações em tempo real"""
    
    # Extrair parâmetros da query string
    query_params = websocket.query_params
    tenant_id = tenant_id or query_params.get("tenant_id")
    client_type = client_type or query_params.get("client_type")
    token = token or query_params.get("token")
    
    # Validações básicas
    if not tenant_id or not client_type:
        await websocket.close(code=4000, reason="Missing tenant_id or client_type")
        return
    
    # Valida o tipo de cliente
    if client_type not in ["operator", "totem", "display"]:
        await websocket.close(code=4000, reason="Invalid client type")
        return

    # Para operadores, valida o token
    if client_type == "operator" and token:
        try:
            print(f"🔍 Validando token para tenant_id: {tenant_id}")
            print(f"🔍 Token recebido: {token[:50]}...")
            
            # Verificar token diretamente
            payload = verify_token(token)
            if not payload:
                print(f"❌ Token inválido para tenant_id: {tenant_id}")
                await websocket.close(code=4002, reason="Invalid token")
                return
            
            print(f"✅ Token válido, payload: {payload}")
            
            operator_id = payload.get("sub")
            if not operator_id:
                print(f"❌ Token sem operator_id para tenant_id: {tenant_id}")
                await websocket.close(code=4002, reason="Invalid token payload")
                return
            
            print(f"🔍 Buscando operador com ID: {operator_id}")
            
            # Buscar operador no banco
            operator = db.query(Operator).filter(Operator.id == operator_id).first()
            if not operator:
                print(f"❌ Operador não encontrado: {operator_id}")
                await websocket.close(code=4002, reason="Operator not found")
                return
            
            print(f"✅ Operador encontrado: {operator.name}, tenant_id: {operator.tenant_id}")
            
            if not operator.is_active:
                print(f"❌ Operador inativo: {operator_id}")
                await websocket.close(code=4003, reason="Inactive operator")
                return
            
            # Verificar se o tenant_id do operador corresponde ao tenant_id da conexão
            if str(operator.tenant_id) != tenant_id:
                print(f"❌ Tenant mismatch: operador.tenant_id={operator.tenant_id}, conexão.tenant_id={tenant_id}")
                await websocket.close(code=4001, reason="Invalid tenant")
                return
                
            print(f"✅ Validação completa bem-sucedida para operador: {operator.name}")
                
        except Exception as e:
            print(f"❌ Erro na validação do token: {str(e)}")
            await websocket.close(code=4002, reason=f"Token validation error: {str(e)}")
            return

    # Conecta o cliente
    await manager.connect(websocket, tenant_id, client_type)
    
    try:
        while True:
            # Mantém a conexão aberta
            data = await websocket.receive_text()
            
            # Aqui você pode implementar lógica adicional para mensagens do cliente
            # Por exemplo, solicitar atualização da fila, etc.
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, tenant_id, client_type)
    except Exception as e:
        # Log do erro
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket, tenant_id, client_type) 