#!/usr/bin/env python3
# 🏦 Exemplo de Integração com Terminal Sicredi

"""
Exemplo prático de como usar o terminal Sicredi no sistema RecoveryTruck.
Este script demonstra todas as funcionalidades disponíveis.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Adiciona o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.api.services.payment.terminal.sicredi_terminal import SicrediTerminalAdapter
from apps.api.services.payment.terminal.base import (
    PaymentMethod, TransactionRequest, PaymentTerminalError
)

class SicrediIntegrationExample:
    """Exemplo de integração com terminal Sicredi"""
    
    def __init__(self):
        self.terminal = None
        self.config = self._get_config()
    
    def _get_config(self) -> Dict[str, Any]:
        """Obtém configuração do terminal"""
        return {
            "type": "sicredi",
            "connection_type": os.getenv("TERMINAL_CONNECTION", "serial"),
            "port": os.getenv("TERMINAL_PORT", "COM1"),
            "baudrate": int(os.getenv("TERMINAL_BAUDRATE", "9600")),
            "timeout": int(os.getenv("TERMINAL_TIMEOUT", "30")),
            "retry_attempts": 3,
            "sicredi": {
                "merchant_id": os.getenv("SICREDI_MERCHANT_ID", "123456789012345"),
                "terminal_id": os.getenv("SICREDI_TERMINAL_ID", "RECOVERY1"),
                "pos_id": os.getenv("SICREDI_POS_ID", "001")
            }
        }
    
    async def initialize_terminal(self):
        """Inicializa o terminal Sicredi"""
        print("🏦 Inicializando Terminal Sicredi...")
        print(f"   - Merchant ID: {self.config['sicredi']['merchant_id']}")
        print(f"   - Terminal ID: {self.config['sicredi']['terminal_id']}")
        print(f"   - Porta: {self.config['port']}")
        print(f"   - Baudrate: {self.config['baudrate']}")
        
        try:
            self.terminal = SicrediTerminalAdapter(self.config)
            print("✅ Terminal Sicredi criado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar terminal: {e}")
            return False
    
    async def connect_terminal(self):
        """Conecta com o terminal"""
        print("\n🔌 Conectando com terminal...")
        
        try:
            connected = await self.terminal.connect()
            if connected:
                print("✅ Terminal conectado com sucesso")
                
                # Obtém informações do terminal
                info = await self.terminal.get_terminal_info()
                print(f"   - Modelo: {info.model}")
                print(f"   - Serial: {info.serial_number}")
                print(f"   - Firmware: {info.firmware_version}")
                
                return True
            else:
                print("❌ Falha na conexão com terminal")
                return False
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    async def test_debit_transaction(self):
        """Testa transação de débito"""
        print("\n💳 Testando Transação de Débito...")
        
        request = TransactionRequest(
            amount=25.50,
            payment_method=PaymentMethod.DEBIT_CARD,
            installments=1,
            description="Banheira de Gelo - 30min",
            customer_name="João Silva",
            customer_document="12345678901"
        )
        
        try:
            # Inicia transação
            transaction_id = await self.terminal.start_transaction(request)
            print(f"✅ Transação iniciada: {transaction_id}")
            print("   👤 Aguardando cliente inserir cartão...")
            
            # Simula aguardar processamento
            await asyncio.sleep(2)
            
            # Consulta status
            status = await self.terminal.get_transaction_status(transaction_id)
            print(f"   Status: {status.status.value}")
            print(f"   Valor: R$ {status.amount:.2f}")
            
            if status.authorization_code:
                print(f"   Autorização: {status.authorization_code}")
            if status.nsu:
                print(f"   NSU: {status.nsu}")
            if status.card_brand:
                print(f"   Bandeira: {status.card_brand}")
            if status.card_last_digits:
                print(f"   Final do cartão: ****{status.card_last_digits}")
            
            # Imprime comprovante se aprovada
            if status.status.value == "approved":
                print("🖨️ Imprimindo comprovante...")
                printed = await self.terminal.print_receipt(transaction_id, "customer")
                if printed:
                    print("✅ Comprovante impresso")
                else:
                    print("⚠️ Erro na impressão")
            
            return transaction_id
            
        except PaymentTerminalError as e:
            print(f"❌ Erro na transação: {e}")
            return None
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return None
    
    async def test_credit_transaction(self):
        """Testa transação de crédito à vista"""
        print("\n💳 Testando Transação de Crédito à Vista...")
        
        request = TransactionRequest(
            amount=50.00,
            payment_method=PaymentMethod.CREDIT_CARD,
            installments=1,
            description="Bota de Compressão - 45min",
            customer_name="Maria Santos"
        )
        
        try:
            transaction_id = await self.terminal.start_transaction(request)
            print(f"✅ Transação iniciada: {transaction_id}")
            print("   👤 Aguardando cliente inserir cartão...")
            
            await asyncio.sleep(2)
            
            status = await self.terminal.get_transaction_status(transaction_id)
            print(f"   Status: {status.status.value}")
            print(f"   Valor: R$ {status.amount:.2f}")
            
            return transaction_id
            
        except Exception as e:
            print(f"❌ Erro na transação: {e}")
            return None
    
    async def test_installment_transaction(self):
        """Testa transação parcelada"""
        print("\n💳 Testando Transação Parcelada...")
        
        request = TransactionRequest(
            amount=120.00,
            payment_method=PaymentMethod.CREDIT_CARD,
            installments=3,
            description="Pacote Completo - 60min",
            customer_name="Pedro Costa"
        )
        
        try:
            transaction_id = await self.terminal.start_transaction(request)
            print(f"✅ Transação iniciada: {transaction_id}")
            print(f"   💰 Valor: R$ {request.amount:.2f} em {request.installments}x")
            print("   👤 Aguardando cliente inserir cartão...")
            
            await asyncio.sleep(2)
            
            status = await self.terminal.get_transaction_status(transaction_id)
            print(f"   Status: {status.status.value}")
            print(f"   Parcelas: {status.installments}x")
            
            return transaction_id
            
        except Exception as e:
            print(f"❌ Erro na transação: {e}")
            return None
    
    async def test_contactless_transaction(self):
        """Testa transação contactless"""
        print("\n📱 Testando Transação Contactless...")
        
        request = TransactionRequest(
            amount=15.00,
            payment_method=PaymentMethod.CONTACTLESS,
            installments=1,
            description="Serviço Express"
        )
        
        try:
            transaction_id = await self.terminal.start_transaction(request)
            print(f"✅ Transação iniciada: {transaction_id}")
            print("   📱 Aguardando aproximação do cartão/celular...")
            
            await asyncio.sleep(2)
            
            status = await self.terminal.get_transaction_status(transaction_id)
            print(f"   Status: {status.status.value}")
            
            return transaction_id
            
        except Exception as e:
            print(f"❌ Erro na transação: {e}")
            return None
    
    async def test_transaction_cancellation(self):
        """Testa cancelamento de transação"""
        print("\n🚫 Testando Cancelamento de Transação...")
        
        request = TransactionRequest(
            amount=30.00,
            payment_method=PaymentMethod.DEBIT_CARD,
            installments=1,
            description="Transação para cancelar"
        )
        
        try:
            # Inicia transação
            transaction_id = await self.terminal.start_transaction(request)
            print(f"✅ Transação iniciada: {transaction_id}")
            
            # Simula delay antes do cancelamento
            await asyncio.sleep(1)
            
            # Cancela transação
            cancelled = await self.terminal.cancel_transaction(transaction_id)
            if cancelled:
                print("✅ Transação cancelada com sucesso")
            else:
                print("❌ Falha no cancelamento")
            
            return cancelled
            
        except Exception as e:
            print(f"❌ Erro no cancelamento: {e}")
            return False
    
    async def test_custom_printing(self):
        """Testa impressão customizada"""
        print("\n🖨️ Testando Impressão Customizada...")
        
        custom_text = """
        ================================
             RECOVERY TRUCK
        ================================
        
        Obrigado pela preferência!
        
        Sistema de autoatendimento
        com pagamento integrado
        
        Data: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """
        
        ================================
        """
        
        try:
            printed = await self.terminal.print_custom_text(custom_text)
            if printed:
                print("✅ Texto customizado impresso")
            else:
                print("❌ Erro na impressão customizada")
            
            return printed
            
        except Exception as e:
            print(f"❌ Erro na impressão: {e}")
            return False
    
    async def test_terminal_configuration(self):
        """Testa configuração do terminal"""
        print("\n⚙️ Testando Configuração do Terminal...")
        
        settings = {
            "timeout": 60,
            "auto_print": True,
            "beep_enabled": True
        }
        
        try:
            configured = await self.terminal.configure_terminal(settings)
            if configured:
                print("✅ Terminal configurado com sucesso")
            else:
                print("❌ Erro na configuração")
            
            return configured
            
        except Exception as e:
            print(f"❌ Erro na configuração: {e}")
            return False
    
    async def show_supported_methods(self):
        """Mostra métodos de pagamento suportados"""
        print("\n📋 Métodos de Pagamento Suportados:")
        
        try:
            methods = await self.terminal.get_supported_payment_methods()
            for method in methods:
                print(f"   ✅ {method.value}")
            
        except Exception as e:
            print(f"❌ Erro ao obter métodos: {e}")
    
    async def disconnect_terminal(self):
        """Desconecta do terminal"""
        print("\n🔌 Desconectando terminal...")
        
        try:
            disconnected = await self.terminal.disconnect()
            if disconnected:
                print("✅ Terminal desconectado")
            else:
                print("⚠️ Erro na desconexão")
            
            return disconnected
            
        except Exception as e:
            print(f"❌ Erro na desconexão: {e}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🏦 EXEMPLO DE INTEGRAÇÃO SICREDI")
        print("=" * 50)
        
        # Inicialização
        if not await self.initialize_terminal():
            return
        
        if not await self.connect_terminal():
            return
        
        # Testes de funcionalidades
        await self.show_supported_methods()
        await self.test_terminal_configuration()
        
        # Testes de transações
        await self.test_debit_transaction()
        await self.test_credit_transaction()
        await self.test_installment_transaction()
        await self.test_contactless_transaction()
        
        # Testes de cancelamento e impressão
        await self.test_transaction_cancellation()
        await self.test_custom_printing()
        
        # Finalização
        await self.disconnect_terminal()
        
        print("\n✅ Todos os testes concluídos!")
        print("🏦 Integração Sicredi funcionando perfeitamente!")

async def main():
    """Função principal"""
    print("🚀 Iniciando exemplo de integração Sicredi...")
    
    # Verifica variáveis de ambiente
    required_vars = [
        "SICREDI_MERCHANT_ID",
        "SICREDI_TERMINAL_ID",
        "TERMINAL_PORT"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️ Variáveis de ambiente não configuradas:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Configure as variáveis ou use valores padrão para teste")
        print("   Exemplo:")
        print("   export SICREDI_MERCHANT_ID=123456789012345")
        print("   export SICREDI_TERMINAL_ID=RECOVERY1")
        print("   export TERMINAL_PORT=COM1")
        print()
    
    # Executa exemplo
    example = SicrediIntegrationExample()
    await example.run_all_tests()

if __name__ == "__main__":
    # Executa o exemplo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Exemplo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no exemplo: {e}")
        import traceback
        traceback.print_exc() 