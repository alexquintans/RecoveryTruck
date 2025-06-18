#!/usr/bin/env python3
# 🧪 Teste de Importação do Sistema de Terminais

import sys
import asyncio
from datetime import datetime

def test_imports():
    """Testa importações básicas"""
    print("🔍 Testando importações...")
    
    try:
        from apps.api.services.payment.terminal import (
            TerminalAdapter, TerminalStatus, PaymentMethod, TransactionStatus,
            MockTerminalAdapter, TerminalAdapterFactory
        )
        print("✅ Importações básicas: OK")
        
        from apps.api.services.payment.terminal_manager import TerminalManager
        print("✅ Terminal Manager: OK")
        
        return True
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

async def test_mock_terminal():
    """Testa terminal mock básico"""
    print("\n🧪 Testando terminal mock...")
    
    try:
        from apps.api.services.payment.terminal import (
            MockTerminalAdapter, PaymentMethod, TransactionRequest
        )
        
        # Cria terminal mock
        config = {
            "type": "mock",
            "simulate_delays": False,
            "failure_rate": 0.0
        }
        
        terminal = MockTerminalAdapter(config)
        print("✅ Terminal mock criado")
        
        # Testa conexão
        connected = await terminal.connect()
        if connected:
            print("✅ Conexão: OK")
        else:
            print("❌ Conexão: FALHOU")
            return False
        
        # Testa informações do terminal
        info = await terminal.get_terminal_info()
        print(f"✅ Info: {info.model} - {info.serial_number}")
        
        # Testa transação
        request = TransactionRequest(
            amount=10.0,
            payment_method=PaymentMethod.CREDIT_CARD,
            description="Teste"
        )
        
        transaction_id = await terminal.start_transaction(request)
        print(f"✅ Transação iniciada: {transaction_id}")
        
        # Aguarda um pouco
        await asyncio.sleep(0.1)
        
        # Verifica status
        response = await terminal.get_transaction_status(transaction_id)
        print(f"✅ Status: {response.status.value} - R$ {response.amount:.2f}")
        
        # Desconecta
        await terminal.disconnect()
        print("✅ Desconectado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do terminal: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_terminal_manager():
    """Testa terminal manager"""
    print("\n🎛️ Testando Terminal Manager...")
    
    try:
        from apps.api.services.payment.terminal_manager import TerminalManager
        
        manager = TerminalManager()
        print("✅ Terminal Manager criado")
        
        # Configura terminal mock
        configs = {
            "test_tenant": {
                "terminal": {
                    "type": "mock",
                    "simulate_delays": False,
                    "failure_rate": 0.0
                }
            }
        }
        
        await manager.initialize(configs)
        print("✅ Manager inicializado")
        
        # Verifica estatísticas
        stats = manager.get_statistics()
        print(f"✅ Estatísticas: {stats['total_terminals']} terminais")
        
        # Verifica status
        status = await manager.get_terminal_status("test_tenant")
        if status:
            print(f"✅ Status: {status['status']}")
        
        # Encerra
        await manager.shutdown()
        print("✅ Manager encerrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do manager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_factory():
    """Testa factory de terminais"""
    print("\n🏭 Testando Terminal Factory...")
    
    try:
        from apps.api.services.payment.terminal import TerminalAdapterFactory
        
        # Lista terminais disponíveis
        available = TerminalAdapterFactory.get_available_terminals()
        print(f"✅ Terminais disponíveis: {list(available.keys())}")
        
        # Cria terminal mock
        config = {"type": "mock"}
        terminal = TerminalAdapterFactory.create_terminal("mock", config)
        print(f"✅ Terminal criado: {terminal.__class__.__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da factory: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Função principal"""
    print("🏧 TESTE DO SISTEMA DE TERMINAIS FÍSICOS")
    print("=" * 50)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Testa importações
    if not test_imports():
        print("\n❌ FALHA: Importações básicas falharam")
        sys.exit(1)
    
    # Testa factory
    if not test_factory():
        print("\n❌ FALHA: Factory falhou")
        sys.exit(1)
    
    # Testa terminal mock
    if not await test_mock_terminal():
        print("\n❌ FALHA: Terminal mock falhou")
        sys.exit(1)
    
    # Testa terminal manager
    if not await test_terminal_manager():
        print("\n❌ FALHA: Terminal manager falhou")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 TODOS OS TESTES PASSARAM!")
    print("✅ Sistema de Terminais Físicos está funcionando corretamente")
    print(f"⏰ Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main()) 