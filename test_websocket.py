#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket():
    """Teste simples de conexão WebSocket"""
    
    # URL do WebSocket do router com parâmetros
    uri = "ws://localhost:8000/ws?tenant_id=38534c9f-accb-4884-9c19-dd37f77d0594&client_type=totem"
    
    print(f"🔍 Testando conexão WebSocket: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket conectado com sucesso!")
            
            # Enviar mensagem de teste
            test_message = {"type": "test", "data": "Hello WebSocket!"}
            await websocket.send(json.dumps(test_message))
            print(f"📤 Mensagem enviada: {test_message}")
            
            # Aguardar resposta
            response = await websocket.recv()
            print(f"📥 Resposta recebida: {response}")
            
    except Exception as e:
        print(f"❌ Erro na conexão WebSocket: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket()) 