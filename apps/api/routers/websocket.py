from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from ..services.websocket import manager
from ..services.auth import get_current_operator
from ..models.operator import Operator
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.websocket("/ws/{tenant_id}/{client_type}")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str,
    client_type: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Endpoint WebSocket para atualizações em tempo real"""
    
    # Valida o tipo de cliente
    if client_type not in ["operator", "totem"]:
        await websocket.close(code=4000, reason="Invalid client type")
        return

    # Para operadores, valida o token
    if client_type == "operator" and token:
        try:
            operator = await get_current_operator(token, db)
            if operator.tenant_id != tenant_id:
                await websocket.close(code=4001, reason="Invalid tenant")
                return
        except HTTPException:
            await websocket.close(code=4002, reason="Invalid token")
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