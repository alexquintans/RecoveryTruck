#!/usr/bin/env python3
"""
Script de teste simples para WebSocket
"""

import asyncio
import websockets
import json

async def test_websocket_simple():
    """Testa a conexão WebSocket simples"""
    
    # URL do WebSocket de teste simples
    ws_url = "ws://localhost:8001/ws-test"
    
    print(f"🔍 Testando WebSocket simples: {ws_url}")
    
    try:
        # Conectar ao WebSocket
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket simples conectado com sucesso!")
            
            # Enviar mensagem de teste
            test_message = {
                "type": "test",
                "data": {
                    "message": "Teste de conexão WebSocket simples",
                    "timestamp": "2024-01-01T00:00:00"
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print("📤 Mensagem enviada:", test_message)
            
            # Aguardar resposta
            response = await websocket.recv()
            print("📥 Resposta recebida:", response)
            
    except websockets.exceptions.ConnectionClosed:
        print("❌ Conexão fechada - servidor não está rodando ou porta incorreta")
        return False
    except websockets.exceptions.InvalidURI:
        print("❌ URI inválida")
        return False
    except Exception as e:
        print(f"❌ Erro na conexão WebSocket simples: {e}")
        return False
    
    return True

async def main():
    """Função principal"""
    print("🚀 Iniciando teste de WebSocket simples...")
    
    success = await test_websocket_simple()
    
    print("\n" + "="*50)
    print("RESULTADO FINAL")
    print("="*50)
    print(f"Teste Simples: {'✅ SUCESSO' if success else '❌ FALHOU'}")
    
    if success:
        print("🎉 Teste passou!")
        return 0
    else:
        print("⚠️ Teste falhou!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    import sys
    sys.exit(exit_code) 