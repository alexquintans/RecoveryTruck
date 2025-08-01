#!/usr/bin/env python3
"""
Script de teste para WebSocket simples
"""

import asyncio
import websockets
import json
import sys

async def test_simple_websocket():
    """Testa o endpoint WebSocket simples"""
    
    ws_url = "ws://recoverytruck-production.up.railway.app/ws/test"
    
    print(f"🔍 Testando WebSocket simples: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket simples conectado com sucesso!")
            
            # Enviar mensagem de teste
            test_message = "Hello WebSocket!"
            await websocket.send(test_message)
            print(f"📤 Mensagem enviada: {test_message}")
            
            # Aguardar resposta
            response = await websocket.recv()
            print(f"📥 Resposta recebida: {response}")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Erro de status: {e}")
        return False
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Conexão fechada: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False
    
    return True

async def main():
    """Função principal"""
    print("🧪 Testando WebSocket simples...")
    
    success = await test_simple_websocket()
    
    if success:
        print("✅ Teste simples passou!")
        return 0
    else:
        print("❌ Teste simples falhou!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 