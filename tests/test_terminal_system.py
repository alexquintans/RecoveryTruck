# 🧪 Testes do Sistema de Terminais Físicos

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from apps.api.services.payment.terminal import (
    TerminalAdapter, TerminalStatus, PaymentMethod, TransactionStatus,
    TransactionRequest, TransactionResponse, PaymentTerminalError,
    MockTerminalAdapter, TerminalAdapterFactory
)
from apps.api.services.payment.terminal_manager import TerminalManager

class TestMockTerminal:
    """Testes do terminal mock"""
    
    @pytest.fixture
    async def mock_terminal(self):
        config = {
            "type": "mock",
            "simulate_delays": False,
            "failure_rate": 0.0,
            "serial_number": "TEST001"
        }
        terminal = MockTerminalAdapter(config)
        yield terminal
        await terminal.disconnect()
    
    @pytest.mark.asyncio
    async def test_connection(self, mock_terminal):
        """Testa conexão do terminal mock"""
        # Inicialmente desconectado
        assert mock_terminal.status == TerminalStatus.DISCONNECTED
        assert not await mock_terminal.is_connected()
        
        # Conecta
        success = await mock_terminal.connect()
        assert success
        assert mock_terminal.status == TerminalStatus.CONNECTED
        assert await mock_terminal.is_connected()
        
        # Desconecta
        success = await mock_terminal.disconnect()
        assert success
        assert mock_terminal.status == TerminalStatus.DISCONNECTED
    
    @pytest.mark.asyncio
    async def test_terminal_info(self, mock_terminal):
        """Testa obtenção de informações do terminal"""
        await mock_terminal.connect()
        
        info = await mock_terminal.get_terminal_info()
        assert info.serial_number == "TEST001"
        assert info.model == "MockTerminal v1.0"
        assert info.firmware_version == "1.0.0"
        assert info.battery_level is not None
        assert info.signal_strength is not None
    
    @pytest.mark.asyncio
    async def test_successful_transaction(self, mock_terminal):
        """Testa transação bem-sucedida"""
        await mock_terminal.connect()
        
        request = TransactionRequest(
            amount=10.0,
            payment_method=PaymentMethod.CREDIT_CARD,
            description="Teste",
            customer_name="Cliente Teste"
        )
        
        # Inicia transação
        transaction_id = await mock_terminal.start_transaction(request)
        assert transaction_id is not None
        assert mock_terminal.status == TerminalStatus.BUSY
        
        # Aguarda processamento (mock é rápido sem delays)
        await asyncio.sleep(0.1)
        
        # Verifica status
        response = await mock_terminal.get_transaction_status(transaction_id)
        assert response.transaction_id == transaction_id
        assert response.status == TransactionStatus.APPROVED
        assert response.amount == 10.0
        assert response.payment_method == PaymentMethod.CREDIT_CARD
        assert response.authorization_code is not None
        assert response.nsu is not None
    
    @pytest.mark.asyncio
    async def test_declined_transaction(self, mock_terminal):
        """Testa transação negada (R$ 1,00 sempre nega)"""
        await mock_terminal.connect()
        
        request = TransactionRequest(
            amount=1.0,  # Valor especial que sempre nega
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        transaction_id = await mock_terminal.start_transaction(request)
        await asyncio.sleep(0.1)
        
        response = await mock_terminal.get_transaction_status(transaction_id)
        assert response.status == TransactionStatus.DECLINED
        assert response.error_message is not None
    
    @pytest.mark.asyncio
    async def test_timeout_transaction(self, mock_terminal):
        """Testa transação com timeout (R$ 2,00 sempre timeout)"""
        await mock_terminal.connect()
        
        request = TransactionRequest(
            amount=2.0,  # Valor especial que sempre timeout
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        transaction_id = await mock_terminal.start_transaction(request)
        await asyncio.sleep(0.1)
        
        response = await mock_terminal.get_transaction_status(transaction_id)
        assert response.status == TransactionStatus.TIMEOUT
        assert response.error_message == "Timeout na transação"
    
    @pytest.mark.asyncio
    async def test_cancel_transaction(self, mock_terminal):
        """Testa cancelamento de transação"""
        await mock_terminal.connect()
        
        request = TransactionRequest(
            amount=10.0,
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        transaction_id = await mock_terminal.start_transaction(request)
        
        # Cancela imediatamente
        success = await mock_terminal.cancel_transaction(transaction_id)
        assert success
        
        response = await mock_terminal.get_transaction_status(transaction_id)
        assert response.status == TransactionStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_print_receipt(self, mock_terminal):
        """Testa impressão de comprovante"""
        await mock_terminal.connect()
        
        request = TransactionRequest(
            amount=10.0,
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        transaction_id = await mock_terminal.start_transaction(request)
        await asyncio.sleep(0.1)  # Aguarda aprovação
        
        # Imprime comprovante do cliente
        success = await mock_terminal.print_receipt(transaction_id, "customer")
        assert success
        
        # Imprime comprovante do lojista
        success = await mock_terminal.print_receipt(transaction_id, "merchant")
        assert success
    
    @pytest.mark.asyncio
    async def test_print_custom_text(self, mock_terminal):
        """Testa impressão de texto customizado"""
        await mock_terminal.connect()
        
        success = await mock_terminal.print_custom_text("Texto de teste")
        assert success
    
    @pytest.mark.asyncio
    async def test_supported_payment_methods(self, mock_terminal):
        """Testa métodos de pagamento suportados"""
        await mock_terminal.connect()
        
        methods = await mock_terminal.get_supported_payment_methods()
        assert PaymentMethod.CREDIT_CARD in methods
        assert PaymentMethod.DEBIT_CARD in methods
        assert PaymentMethod.PIX in methods
        assert PaymentMethod.CONTACTLESS in methods
    
    @pytest.mark.asyncio
    async def test_configure_terminal(self, mock_terminal):
        """Testa configuração do terminal"""
        await mock_terminal.connect()
        
        settings = {
            "failure_rate": 0.2,
            "transaction_delay": 1.0,
            "simulate_delays": True
        }
        
        success = await mock_terminal.configure_terminal(settings)
        assert success
        assert mock_terminal.failure_rate == 0.2
        assert mock_terminal.transaction_delay == 1.0
        assert mock_terminal.simulate_delays == True
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_terminal):
        """Testa verificação de saúde"""
        # Terminal desconectado
        health = await mock_terminal.health_check()
        assert health["status"] == TerminalStatus.DISCONNECTED.value
        assert not health["connected"]
        
        # Terminal conectado
        await mock_terminal.connect()
        health = await mock_terminal.health_check()
        assert health["status"] == TerminalStatus.CONNECTED.value
        assert health["connected"]
        assert health["terminal_info"] is not None

class TestTerminalFactory:
    """Testes da factory de terminais"""
    
    def test_create_mock_terminal(self):
        """Testa criação de terminal mock"""
        config = {"type": "mock"}
        terminal = TerminalAdapterFactory.create_terminal("mock", config)
        
        assert isinstance(terminal, MockTerminalAdapter)
        assert terminal.config["type"] == "mock"
    
    def test_invalid_terminal_type(self):
        """Testa tipo de terminal inválido"""
        with pytest.raises(ValueError, match="not supported"):
            TerminalAdapterFactory.create_terminal("invalid", {})
    
    def test_get_available_terminals(self):
        """Testa listagem de terminais disponíveis"""
        available = TerminalAdapterFactory.get_available_terminals()
        
        assert "mock" in available
        assert available["mock"] == True  # Mock está implementado
        assert "stone" in available
    
    def test_create_from_tenant_config(self):
        """Testa criação baseada em configuração de tenant"""
        tenant_config = {
            "terminal": {
                "type": "mock",
                "simulate_delays": False
            }
        }
        
        terminal = TerminalAdapterFactory.create_from_tenant_config("test_tenant", tenant_config)
        
        assert terminal is not None
        assert isinstance(terminal, MockTerminalAdapter)
        assert terminal.config["tenant_id"] == "test_tenant"

class TestTerminalManager:
    """Testes do gerenciador de terminais"""
    
    @pytest.fixture
    async def terminal_manager(self):
        manager = TerminalManager()
        yield manager
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_initialize_terminals(self, terminal_manager):
        """Testa inicialização de terminais"""
        configs = {
            "tenant1": {
                "terminal": {
                    "type": "mock",
                    "simulate_delays": False
                }
            },
            "tenant2": {
                "terminal": {
                    "type": "mock",
                    "simulate_delays": False
                }
            }
        }
        
        await terminal_manager.initialize(configs)
        
        assert len(terminal_manager._terminals) == 2
        assert "tenant1" in terminal_manager._terminals
        assert "tenant2" in terminal_manager._terminals
    
    @pytest.mark.asyncio
    async def test_add_remove_terminal(self, terminal_manager):
        """Testa adição e remoção de terminal"""
        config = {
            "terminal": {
                "type": "mock",
                "simulate_delays": False
            }
        }
        
        # Adiciona terminal
        success = await terminal_manager.add_terminal("test_tenant", config)
        assert success
        
        terminal = terminal_manager.get_terminal("test_tenant")
        assert terminal is not None
        
        # Remove terminal
        success = await terminal_manager.remove_terminal("test_tenant")
        assert success
        
        terminal = terminal_manager.get_terminal("test_tenant")
        assert terminal is None
    
    @pytest.mark.asyncio
    async def test_terminal_status(self, terminal_manager):
        """Testa obtenção de status do terminal"""
        config = {
            "terminal": {
                "type": "mock",
                "simulate_delays": False
            }
        }
        
        await terminal_manager.add_terminal("test_tenant", config)
        
        status = await terminal_manager.get_terminal_status("test_tenant")
        assert status is not None
        assert status["tenant_id"] == "test_tenant"
        assert status["terminal_type"] == "mock"
        assert status["status"] in ["connected", "connecting"]
    
    @pytest.mark.asyncio
    async def test_list_terminals(self, terminal_manager):
        """Testa listagem de terminais"""
        configs = {
            "tenant1": {"terminal": {"type": "mock", "simulate_delays": False}},
            "tenant2": {"terminal": {"type": "mock", "simulate_delays": False}}
        }
        
        await terminal_manager.initialize(configs)
        
        terminals = await terminal_manager.list_terminals()
        assert len(terminals) == 2
        
        tenant_ids = [t["tenant_id"] for t in terminals]
        assert "tenant1" in tenant_ids
        assert "tenant2" in tenant_ids
    
    @pytest.mark.asyncio
    async def test_start_transaction(self, terminal_manager):
        """Testa início de transação via manager"""
        config = {
            "terminal": {
                "type": "mock",
                "simulate_delays": False
            }
        }
        
        await terminal_manager.add_terminal("test_tenant", config)
        
        request = TransactionRequest(
            amount=10.0,
            payment_method=PaymentMethod.CREDIT_CARD,
            description="Teste via manager"
        )
        
        transaction_id = await terminal_manager.start_transaction("test_tenant", request)
        assert transaction_id is not None
        
        # Verifica status
        await asyncio.sleep(0.1)
        response = await terminal_manager.get_transaction_status("test_tenant", transaction_id)
        assert response.status == TransactionStatus.APPROVED
    
    @pytest.mark.asyncio
    async def test_terminal_not_found(self, terminal_manager):
        """Testa erro quando terminal não existe"""
        request = TransactionRequest(
            amount=10.0,
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        with pytest.raises(PaymentTerminalError, match="No terminal found"):
            await terminal_manager.start_transaction("nonexistent", request)
    
    @pytest.mark.asyncio
    async def test_statistics(self, terminal_manager):
        """Testa estatísticas do manager"""
        configs = {
            "tenant1": {"terminal": {"type": "mock", "simulate_delays": False}},
            "tenant2": {"terminal": {"type": "mock", "simulate_delays": False}}
        }
        
        await terminal_manager.initialize(configs)
        
        stats = terminal_manager.get_statistics()
        assert stats["total_terminals"] == 2
        assert stats["connected"] >= 0
        assert stats["monitoring_active"] == True
    
    @pytest.mark.asyncio
    async def test_connect_disconnect_terminal(self, terminal_manager):
        """Testa conexão/desconexão via manager"""
        config = {
            "terminal": {
                "type": "mock",
                "simulate_delays": False
            }
        }
        
        await terminal_manager.add_terminal("test_tenant", config)
        
        # Desconecta
        success = await terminal_manager.disconnect_terminal("test_tenant")
        assert success
        
        # Reconecta
        success = await terminal_manager.connect_terminal("test_tenant")
        assert success
    
    @pytest.mark.asyncio
    async def test_reset_terminal(self, terminal_manager):
        """Testa reset de terminal via manager"""
        config = {
            "terminal": {
                "type": "mock",
                "simulate_delays": False
            }
        }
        
        await terminal_manager.add_terminal("test_tenant", config)
        
        success = await terminal_manager.reset_terminal("test_tenant")
        assert success

class TestTransactionModels:
    """Testes dos modelos de transação"""
    
    def test_transaction_request(self):
        """Testa criação de TransactionRequest"""
        request = TransactionRequest(
            amount=25.50,
            payment_method=PaymentMethod.CREDIT_CARD,
            installments=2,
            description="Teste",
            customer_name="João",
            customer_document="12345678901"
        )
        
        assert request.amount == 25.50
        assert request.payment_method == PaymentMethod.CREDIT_CARD
        assert request.installments == 2
        assert request.description == "Teste"
        assert request.customer_name == "João"
        assert request.customer_document == "12345678901"
    
    def test_transaction_response(self):
        """Testa criação de TransactionResponse"""
        response = TransactionResponse(
            transaction_id="test-123",
            status=TransactionStatus.APPROVED,
            amount=25.50,
            payment_method=PaymentMethod.CREDIT_CARD,
            authorization_code="AUTH123",
            nsu="1234567"
        )
        
        assert response.transaction_id == "test-123"
        assert response.status == TransactionStatus.APPROVED
        assert response.amount == 25.50
        assert response.authorization_code == "AUTH123"
        assert response.nsu == "1234567"
        assert response.timestamp is not None

# Fixtures globais
@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para testes assíncronos"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    # Executa testes
    pytest.main([__file__, "-v", "--asyncio-mode=auto"]) 