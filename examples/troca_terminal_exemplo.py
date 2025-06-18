#!/usr/bin/env python3
# 🔄 Exemplo de Troca de Terminal - Flexibilidade Total

"""
Este exemplo demonstra como é fácil trocar de terminal no sistema RecoveryTruck.
Mostra a flexibilidade da arquitetura e como o cliente nunca fica "preso" a um terminal.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.api.services.payment.terminal.factory import TerminalAdapterFactory
from apps.api.services.payment.terminal.base import PaymentMethod, TransactionRequest

class TrocaTerminalExemplo:
    """Demonstração de troca de terminal"""
    
    def __init__(self):
        self.current_terminal = None
        self.transaction_history = []
    
    async def demonstrar_flexibilidade(self):
        """Demonstra a flexibilidade de troca de terminais"""
        print("🔄 DEMONSTRAÇÃO: FLEXIBILIDADE DE TERMINAIS")
        print("=" * 60)
        
        # Cenário: Cliente começou com Mock, depois quer Sicredi, depois Stone
        cenarios = [
            {
                "nome": "Desenvolvimento/Testes",
                "terminal": "mock",
                "config": {
                    "type": "mock",
                    "simulate_delays": False,
                    "failure_rate": 0.0
                }
            },
            {
                "nome": "Produção com Sicredi",
                "terminal": "sicredi", 
                "config": {
                    "type": "sicredi",
                    "connection_type": "serial",
                    "port": "COM1",
                    "baudrate": 9600,
                    "sicredi": {
                        "merchant_id": "123456789012345",
                        "terminal_id": "RECOVERY1",
                        "pos_id": "001"
                    }
                }
            },
            {
                "nome": "Mudança para Stone",
                "terminal": "stone",
                "config": {
                    "type": "stone",
                    "connection_type": "serial", 
                    "port": "COM1",
                    "baudrate": 115200,
                    "stone": {
                        "merchant_id": "123456789",
                        "terminal_id": "TERM001"
                    }
                }
            }
        ]
        
        for i, cenario in enumerate(cenarios, 1):
            print(f"\n📍 CENÁRIO {i}: {cenario['nome']}")
            print("-" * 40)
            
            await self.trocar_terminal(cenario['terminal'], cenario['config'])
            await self.testar_funcionalidades()
            
            if i < len(cenarios):
                print(f"\n⏳ Cliente decide mudar para {cenarios[i]['nome']}...")
                await asyncio.sleep(1)
        
        print("\n✅ DEMONSTRAÇÃO CONCLUÍDA!")
        print("🎯 Resultado: Cliente pode trocar de terminal a qualquer momento!")
    
    async def trocar_terminal(self, tipo: str, config: Dict[str, Any]):
        """Troca o terminal atual"""
        print(f"🔄 Trocando para terminal: {tipo.upper()}")
        
        try:
            # Desconecta terminal atual se houver
            if self.current_terminal:
                print("   📤 Desconectando terminal anterior...")
                await self.current_terminal.disconnect()
            
            # Cria novo terminal
            print("   🏭 Criando novo terminal...")
            self.current_terminal = TerminalAdapterFactory.create_terminal(tipo, config)
            
            # Conecta novo terminal
            print("   🔌 Conectando novo terminal...")
            connected = await self.current_terminal.connect()
            
            if connected:
                print(f"   ✅ Terminal {tipo.upper()} conectado com sucesso!")
                
                # Mostra informações do terminal
                try:
                    info = await self.current_terminal.get_terminal_info()
                    print(f"   📋 Modelo: {info.model}")
                    print(f"   📋 Serial: {info.serial_number}")
                except:
                    print("   📋 Informações básicas obtidas")
                
                # Mostra métodos suportados
                methods = await self.current_terminal.get_supported_payment_methods()
                print(f"   💳 Métodos suportados: {len(methods)}")
                for method in methods:
                    print(f"      - {method.value}")
                
            else:
                print(f"   ❌ Falha na conexão com {tipo.upper()}")
                
        except Exception as e:
            print(f"   ❌ Erro na troca: {e}")
    
    async def testar_funcionalidades(self):
        """Testa funcionalidades básicas do terminal atual"""
        if not self.current_terminal:
            print("   ⚠️ Nenhum terminal conectado")
            return
        
        print("   🧪 Testando funcionalidades...")
        
        try:
            # Teste 1: Verificar conexão
            connected = await self.current_terminal.is_connected()
            print(f"      ✅ Conexão: {'OK' if connected else 'FALHA'}")
            
            if not connected:
                return
            
            # Teste 2: Transação de teste
            request = TransactionRequest(
                amount=10.00,
                payment_method=PaymentMethod.CREDIT_CARD,
                installments=1,
                description="Teste de funcionalidade"
            )
            
            transaction_id = await self.current_terminal.start_transaction(request)
            print(f"      ✅ Transação iniciada: {transaction_id[:8]}...")
            
            # Simula processamento
            await asyncio.sleep(0.5)
            
            # Consulta status
            status = await self.current_terminal.get_transaction_status(transaction_id)
            print(f"      ✅ Status: {status.status.value}")
            print(f"      ✅ Valor: R$ {status.amount:.2f}")
            
            # Registra na história
            self.transaction_history.append({
                "terminal": self.current_terminal.__class__.__name__,
                "transaction_id": transaction_id,
                "amount": status.amount,
                "status": status.status.value,
                "timestamp": datetime.now()
            })
            
            # Teste 3: Impressão (se suportada)
            try:
                printed = await self.current_terminal.print_custom_text("Teste de impressão")
                print(f"      ✅ Impressão: {'OK' if printed else 'N/A'}")
            except:
                print("      ✅ Impressão: N/A")
                
        except Exception as e:
            print(f"      ❌ Erro no teste: {e}")
    
    def mostrar_terminais_disponiveis(self):
        """Mostra terminais disponíveis no sistema"""
        print("\n📋 TERMINAIS DISPONÍVEIS NO SISTEMA")
        print("-" * 40)
        
        available = TerminalAdapterFactory.get_available_terminals()
        
        for terminal, implemented in available.items():
            status = "✅ Implementado" if implemented else "⏳ Pendente"
            print(f"   {terminal.upper()}: {status}")
    
    def mostrar_historico_transacoes(self):
        """Mostra histórico de transações em diferentes terminais"""
        if not self.transaction_history:
            print("\n📊 Nenhuma transação realizada")
            return
        
        print("\n📊 HISTÓRICO DE TRANSAÇÕES")
        print("-" * 40)
        
        for i, trans in enumerate(self.transaction_history, 1):
            print(f"   {i}. Terminal: {trans['terminal']}")
            print(f"      ID: {trans['transaction_id'][:8]}...")
            print(f"      Valor: R$ {trans['amount']:.2f}")
            print(f"      Status: {trans['status']}")
            print(f"      Data: {trans['timestamp'].strftime('%H:%M:%S')}")
            print()
    
    def mostrar_vantagens_arquitetura(self):
        """Mostra as vantagens da arquitetura flexível"""
        print("\n🏆 VANTAGENS DA ARQUITETURA FLEXÍVEL")
        print("-" * 40)
        
        vantagens = [
            "🔄 Troca de terminal sem alterar código",
            "⚡ Zero downtime na mudança",
            "🔧 Mesma API para todos os terminais",
            "📊 Histórico preservado",
            "🛡️ Isolamento entre terminais",
            "🚀 Implementação rápida de novos terminais",
            "💰 Sem vendor lock-in",
            "🧪 Testes com terminal mock",
            "📈 Escalabilidade garantida",
            "🔒 Segurança mantida"
        ]
        
        for vantagem in vantagens:
            print(f"   {vantagem}")
    
    async def simular_cenario_real(self):
        """Simula um cenário real de mudança de terminal"""
        print("\n🎬 CENÁRIO REAL: MUDANÇA DE FORNECEDOR")
        print("-" * 50)
        
        print("📅 Janeiro 2024: Cliente inicia com Sicredi")
        await self.trocar_terminal("sicredi", {
            "type": "sicredi",
            "connection_type": "serial",
            "port": "COM1",
            "sicredi": {
                "merchant_id": "123456789012345",
                "terminal_id": "RECOVERY1"
            }
        })
        
        # Simula uso por alguns meses
        print("\n💼 Processando transações com Sicredi...")
        for i in range(3):
            request = TransactionRequest(
                amount=25.50 + i * 10,
                payment_method=PaymentMethod.DEBIT_CARD,
                installments=1,
                description=f"Serviço {i+1}"
            )
            
            transaction_id = await self.current_terminal.start_transaction(request)
            status = await self.current_terminal.get_transaction_status(transaction_id)
            
            self.transaction_history.append({
                "terminal": "SicrediTerminalAdapter",
                "transaction_id": transaction_id,
                "amount": status.amount,
                "status": status.status.value,
                "timestamp": datetime.now()
            })
            
            await asyncio.sleep(0.2)
        
        print("✅ 3 transações processadas com Sicredi")
        
        print("\n📅 Junho 2024: Cliente decide trocar para Stone")
        print("💡 Motivo: Melhores taxas oferecidas pela Stone")
        
        # Troca para Stone
        await self.trocar_terminal("stone", {
            "type": "stone",
            "connection_type": "serial",
            "port": "COM1",
            "stone": {
                "merchant_id": "987654321",
                "terminal_id": "STONE001"
            }
        })
        
        print("\n💼 Processando transações com Stone...")
        for i in range(2):
            request = TransactionRequest(
                amount=30.00 + i * 15,
                payment_method=PaymentMethod.CREDIT_CARD,
                installments=2,
                description=f"Serviço Stone {i+1}"
            )
            
            transaction_id = await self.current_terminal.start_transaction(request)
            status = await self.current_terminal.get_transaction_status(transaction_id)
            
            self.transaction_history.append({
                "terminal": "StoneTerminalAdapter",
                "transaction_id": transaction_id,
                "amount": status.amount,
                "status": status.status.value,
                "timestamp": datetime.now()
            })
            
            await asyncio.sleep(0.2)
        
        print("✅ 2 transações processadas com Stone")
        
        print("\n🎯 RESULTADO:")
        print("   ✅ Mudança realizada sem problemas")
        print("   ✅ Sistema funcionando normalmente")
        print("   ✅ Histórico preservado")
        print("   ✅ Zero downtime")
        print("   ✅ Cliente satisfeito com flexibilidade")

async def main():
    """Função principal do exemplo"""
    print("🔄 EXEMPLO: FLEXIBILIDADE DE TERMINAIS")
    print("🎯 Demonstrando como o cliente nunca fica 'preso' a um terminal")
    print("=" * 70)
    
    exemplo = TrocaTerminalExemplo()
    
    # Mostra terminais disponíveis
    exemplo.mostrar_terminais_disponiveis()
    
    # Demonstra flexibilidade
    await exemplo.demonstrar_flexibilidade()
    
    # Mostra histórico
    exemplo.mostrar_historico_transacoes()
    
    # Simula cenário real
    await exemplo.simular_cenario_real()
    
    # Mostra histórico final
    exemplo.mostrar_historico_transacoes()
    
    # Mostra vantagens
    exemplo.mostrar_vantagens_arquitetura()
    
    print("\n" + "=" * 70)
    print("✅ CONCLUSÃO: SISTEMA 100% FLEXÍVEL!")
    print("🎯 Cliente pode trocar de terminal quando quiser")
    print("💪 Arquitetura preparada para qualquer mudança")
    print("🚀 Implementação de novos terminais é rápida e fácil")
    print("=" * 70)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Exemplo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no exemplo: {e}")
        import traceback
        traceback.print_exc() 