# 🏦 Testes para Terminal Sicredi

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from apps.api.services.payment.terminal.sicredi_terminal import SicrediTerminalAdapter
from apps.api.services.payment.terminal.base import (
    TerminalStatus, PaymentMethod, TransactionStatus,
    TransactionRequest, PaymentTerminalError
)

class TestSicrediTerminalAdapter:
    """Testes para o adaptador de terminal Sicredi"""
    
    @pytest.fixture
    def sicredi_config(self):
        """Configuração padrão para testes"""
        return {
            "type": "sicredi",
            "connection_type": "serial",
            "port": "COM1",
            "baudrate": 9600,
            "timeout": 30,
            "retry_attempts": 3,
            "sicredi": {
                "merchant_id": "123456789012345",
                "terminal_id": "RECOVERY1",
                "pos_id": "001"
            }
        }
    
    @pytest.fixture
    def mock_protocol(self):
        """Mock do protocolo de comunicação"""
        protocol = Mock()
        protocol.connect = AsyncMock(return_value=True)
        protocol.disconnect = AsyncMock(return_value=True)
        protocol.send_command = AsyncMock()
        protocol.is_connected = True
        return protocol
    
    @pytest.fixture
    def sicredi_terminal(self, sicredi_config, mock_protocol):
        """Terminal Sicredi configurado para testes"""
        with patch.object(SicrediTerminalAdapter, '_create_protocol', return_value=mock_protocol):
            terminal = SicrediTerminalAdapter(sicredi_config)
            return terminal
    
    def test_initialization(self, sicredi_config):
        """Testa inicialização do terminal Sicredi"""
        with patch.object(SicrediTerminalAdapter, '_create_protocol'):
            terminal = SicrediTerminalAdapter(sicredi_config)
            
            assert terminal.merchant_id == "123456789012345"
            assert terminal.terminal_id == "RECOVERY1"
            assert terminal.pos_id == "001"
            assert terminal.status == TerminalStatus.DISCONNECTED
            assert PaymentMethod.CREDIT_CARD in terminal._supported_methods
            assert PaymentMethod.DEBIT_CARD in terminal._supported_methods
    
    @pytest.mark.asyncio
    async def test_successful_connection(self, sicredi_terminal, mock_protocol):
        """Testa conexão bem-sucedida"""
        # Mock resposta de inicialização bem-sucedida
        mock_protocol.send_command.return_value = b'\x02\x30\x30\x00\x03'  # Código 00 = sucesso
        
        result = await sicredi_terminal.connect()
        
        assert result is True
        assert sicredi_terminal.status == TerminalStatus.CONNECTED
        mock_protocol.connect.assert_called_once()
        mock_protocol.send_command.assert_called()
    
    @pytest.mark.asyncio
    async def test_connection_failure(self, sicredi_terminal, mock_protocol):
        """Testa falha na conexão"""
        mock_protocol.connect.return_value = False
        
        result = await sicredi_terminal.connect()
        
        assert result is False
        assert sicredi_terminal.status == TerminalStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_initialization_rejected(self, sicredi_terminal, mock_protocol):
        """Testa rejeição na inicialização"""
        # Mock resposta de inicialização rejeitada
        mock_protocol.send_command.return_value = b'\x02\x30\x31\x00\x03'  # Código 01 = negado
        
        result = await sicredi_terminal.connect()
        
        assert result is False
        assert sicredi_terminal.status == TerminalStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_successful_disconnection(self, sicredi_terminal):
        """Testa desconexão bem-sucedida"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        
        result = await sicredi_terminal.disconnect()
        
        assert result is True
        assert sicredi_terminal.status == TerminalStatus.DISCONNECTED
    
    @pytest.mark.asyncio
    async def test_start_debit_transaction(self, sicredi_terminal, mock_protocol):
        """Testa início de transação de débito"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        
        # Mock resposta de transação iniciada
        mock_protocol.send_command.return_value = b'\x02\x30\x30\x00\x03'
        
        request = TransactionRequest(
            amount=25.50,
            payment_method=PaymentMethod.DEBIT_CARD,
            installments=1,
            description="Teste débito"
        )
        
        transaction_id = await sicredi_terminal.start_transaction(request)
        
        assert transaction_id is not None
        assert sicredi_terminal.status == TerminalStatus.BUSY
        assert sicredi_terminal._current_transaction_id == transaction_id
    
    @pytest.mark.asyncio
    async def test_start_credit_transaction_installments(self, sicredi_terminal, mock_protocol):
        """Testa transação de crédito parcelado"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        mock_protocol.send_command.return_value = b'\x02\x30\x30\x00\x03'
        
        request = TransactionRequest(
            amount=100.00,
            payment_method=PaymentMethod.CREDIT_CARD,
            installments=3,
            description="Teste crédito parcelado",
            customer_document="12345678901"
        )
        
        transaction_id = await sicredi_terminal.start_transaction(request)
        
        assert transaction_id is not None
        # Verifica se o comando foi construído corretamente
        call_args = mock_protocol.send_command.call_args[0][0]
        # Deve conter valor em centavos (10000), tipo 03 (parcelado), 03 parcelas
        assert b'000000010000' in call_args  # Valor R$ 100,00 = 10000 centavos
    
    @pytest.mark.asyncio
    async def test_transaction_not_connected(self, sicredi_terminal):
        """Testa transação com terminal desconectado"""
        request = TransactionRequest(
            amount=25.50,
            payment_method=PaymentMethod.DEBIT_CARD,
            installments=1
        )
        
        with pytest.raises(PaymentTerminalError, match="Terminal not connected"):
            await sicredi_terminal.start_transaction(request)
    
    @pytest.mark.asyncio
    async def test_transaction_terminal_busy(self, sicredi_terminal):
        """Testa transação com terminal ocupado"""
        sicredi_terminal._set_status(TerminalStatus.BUSY)
        
        request = TransactionRequest(
            amount=25.50,
            payment_method=PaymentMethod.DEBIT_CARD,
            installments=1
        )
        
        with pytest.raises(PaymentTerminalError, match="Terminal busy"):
            await sicredi_terminal.start_transaction(request)
    
    @pytest.mark.asyncio
    async def test_unsupported_payment_method(self, sicredi_terminal):
        """Testa método de pagamento não suportado"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        
        request = TransactionRequest(
            amount=25.50,
            payment_method=PaymentMethod.PIX,  # Não suportado pelo Sicredi
            installments=1
        )
        
        with pytest.raises(PaymentTerminalError, match="Payment method not supported"):
            await sicredi_terminal.start_transaction(request)
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_approved(self, sicredi_terminal, mock_protocol):
        """Testa consulta de status - transação aprovada"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        
        # Mock resposta de transação aprovada
        # Formato: CODIGO(2) + VALOR(12) + NSU(12) + AUTORIZACAO(6) + ...
        response_data = "00" + "000000002550" + "123456789012" + "654321" + "VISA1234"
        mock_protocol.send_command.return_value = b'\x02' + response_data.encode() + b'\x03'
        
        transaction_id = "test-transaction-id"
        result = await sicredi_terminal.get_transaction_status(transaction_id)
        
        assert result.transaction_id == transaction_id
        assert result.status == TransactionStatus.APPROVED
        assert result.amount == 25.50
        assert result.authorization_code == "654321"
        assert result.nsu == "123456789012"
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_declined(self, sicredi_terminal, mock_protocol):
        """Testa consulta de status - transação negada"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        
        # Mock resposta de transação negada (código 01)
        response_data = "01" + "000000002550" + "000000000000" + "000000"
        mock_protocol.send_command.return_value = b'\x02' + response_data.encode() + b'\x03'
        
        transaction_id = "test-transaction-id"
        result = await sicredi_terminal.get_transaction_status(transaction_id)
        
        assert result.status == TransactionStatus.DECLINED
        assert result.error_message == "Transação negada"
    
    @pytest.mark.asyncio
    async def test_get_transaction_status_cancelled(self, sicredi_terminal, mock_protocol):
        """Testa consulta de status - transação cancelada"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        
        # Mock resposta de transação cancelada (código 06)
        response_data = "06" + "000000002550" + "000000000000" + "000000"
        mock_protocol.send_command.return_value = b'\x02' + response_data.encode() + b'\x03'
        
        transaction_id = "test-transaction-id"
        result = await sicredi_terminal.get_transaction_status(transaction_id)
        
        assert result.status == TransactionStatus.CANCELLED
        assert result.error_message == "Transação cancelada pelo usuário"
    
    @pytest.mark.asyncio
    async def test_cancel_transaction_success(self, sicredi_terminal, mock_protocol):
        """Testa cancelamento bem-sucedido"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        sicredi_terminal._current_transaction_id = "test-transaction"
        
        # Mock resposta de cancelamento bem-sucedido
        mock_protocol.send_command.return_value = b'\x02\x30\x30\x00\x03'
        
        result = await sicredi_terminal.cancel_transaction("test-transaction")
        
        assert result is True
        assert sicredi_terminal._current_transaction_id is None
        assert sicredi_terminal.status == TerminalStatus.CONNECTED
    
    @pytest.mark.asyncio
    async def test_cancel_transaction_failure(self, sicredi_terminal, mock_protocol):
        """Testa falha no cancelamento"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        
        # Mock resposta de cancelamento rejeitado
        mock_protocol.send_command.return_value = b'\x02\x30\x31\x00\x03'
        
        result = await sicredi_terminal.cancel_transaction("test-transaction")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_print_receipt_success(self, sicredi_terminal, mock_protocol):
        """Testa impressão de comprovante bem-sucedida"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        
        # Mock resposta de impressão bem-sucedida
        mock_protocol.send_command.return_value = b'\x02\x30\x30\x00\x03'
        
        result = await sicredi_terminal.print_receipt("test-transaction", "customer")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_print_custom_text(self, sicredi_terminal, mock_protocol):
        """Testa impressão de texto customizado"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        mock_protocol.send_command.return_value = b'\x02\x30\x30\x00\x03'
        
        result = await sicredi_terminal.print_custom_text("Texto de teste")
        
        assert result is True
    
    def test_lrc_calculation(self, sicredi_terminal):
        """Testa cálculo do LRC (Longitudinal Redundancy Check)"""
        data = b"TEST"
        lrc = sicredi_terminal._calculate_lrc(data)
        
        # LRC é XOR de todos os bytes
        expected_lrc = ord('T') ^ ord('E') ^ ord('S') ^ ord('T')
        assert lrc == expected_lrc
    
    def test_is_success_response(self, sicredi_terminal):
        """Testa verificação de resposta de sucesso"""
        # Resposta de sucesso (código 00)
        success_response = b'\x02\x30\x30\x00\x03'
        assert sicredi_terminal._is_success_response(success_response) is True
        
        # Resposta de erro (código 01)
        error_response = b'\x02\x30\x31\x00\x03'
        assert sicredi_terminal._is_success_response(error_response) is False
        
        # Resposta inválida
        invalid_response = b'\x02\x03'
        assert sicredi_terminal._is_success_response(invalid_response) is False
    
    def test_get_error_message(self, sicredi_terminal):
        """Testa obtenção de mensagem de erro"""
        # Código de erro conhecido
        error_response = b'\x02\x30\x31\x00\x03'  # Código 01
        message = sicredi_terminal._get_error_message(error_response)
        assert message == "Transação negada"
        
        # Código de erro desconhecido
        unknown_response = b'\x02\x39\x39\x00\x03'  # Código 99
        message = sicredi_terminal._get_error_message(unknown_response)
        assert message == "Erro desconhecido"
    
    def test_map_payment_method_to_sicredi(self, sicredi_terminal):
        """Testa mapeamento de métodos de pagamento para códigos Sicredi"""
        # Débito
        code = sicredi_terminal._map_payment_method_to_sicredi(PaymentMethod.DEBIT_CARD, 1)
        assert code == "01"
        
        # Crédito à vista
        code = sicredi_terminal._map_payment_method_to_sicredi(PaymentMethod.CREDIT_CARD, 1)
        assert code == "02"
        
        # Crédito parcelado
        code = sicredi_terminal._map_payment_method_to_sicredi(PaymentMethod.CREDIT_CARD, 3)
        assert code == "03"
        
        # Contactless (tratado como débito)
        code = sicredi_terminal._map_payment_method_to_sicredi(PaymentMethod.CONTACTLESS, 1)
        assert code == "01"
    
    def test_build_sale_command(self, sicredi_terminal):
        """Testa construção do comando de venda"""
        request = TransactionRequest(
            amount=25.50,
            payment_method=PaymentMethod.CREDIT_CARD,
            installments=3,
            customer_document="12345678901"
        )
        
        command_data = sicredi_terminal._build_sale_command("test-id", request)
        command_str = command_data.decode('ascii')
        
        # Verifica valor (R$ 25,50 = 2550 centavos)
        assert command_str.startswith("000000002550")
        
        # Verifica tipo de cartão (03 = crédito parcelado)
        assert "03" in command_str
        
        # Verifica parcelas (03)
        assert "03" in command_str
        
        # Verifica documento do cliente
        assert "DOC12345678901" in command_str
    
    @pytest.mark.asyncio
    async def test_get_supported_payment_methods(self, sicredi_terminal):
        """Testa obtenção de métodos de pagamento suportados"""
        methods = await sicredi_terminal.get_supported_payment_methods()
        
        assert PaymentMethod.CREDIT_CARD in methods
        assert PaymentMethod.DEBIT_CARD in methods
        assert PaymentMethod.CONTACTLESS in methods
        assert PaymentMethod.VOUCHER in methods
        assert PaymentMethod.PIX not in methods  # Não suportado
    
    @pytest.mark.asyncio
    async def test_configure_terminal(self, sicredi_terminal, mock_protocol):
        """Testa configuração do terminal"""
        sicredi_terminal._set_status(TerminalStatus.CONNECTED)
        mock_protocol.send_command.return_value = b'\x02\x30\x30\x00\x03'
        
        settings = {
            "timeout": 60,
            "auto_print": True
        }
        
        result = await sicredi_terminal.configure_terminal(settings)
        assert result is True
    
    def test_parse_info_response(self, sicredi_terminal):
        """Testa parsing da resposta de informações"""
        # Mock resposta com informações do terminal
        info_data = "RECOVERY1      Sicredi Terminal   1.0.0     "
        response = b'\x02' + info_data.encode() + b'\x03'
        
        parsed_info = sicredi_terminal._parse_info_response(response)
        
        assert parsed_info["serial_number"] == "RECOVERY1"
        assert parsed_info["model"] == "Sicredi Terminal"
        assert parsed_info["firmware_version"] == "1.0.0"

class TestSicrediIntegration:
    """Testes de integração para terminal Sicredi"""
    
    @pytest.mark.asyncio
    async def test_full_transaction_flow(self):
        """Testa fluxo completo de transação"""
        config = {
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
        
        with patch.object(SicrediTerminalAdapter, '_create_protocol') as mock_create:
            mock_protocol = Mock()
            mock_protocol.connect = AsyncMock(return_value=True)
            mock_protocol.disconnect = AsyncMock(return_value=True)
            mock_protocol.is_connected = True
            mock_create.return_value = mock_protocol
            
            terminal = SicrediTerminalAdapter(config)
            
            # 1. Conectar
            mock_protocol.send_command.return_value = b'\x02\x30\x30\x00\x03'
            connected = await terminal.connect()
            assert connected is True
            
            # 2. Iniciar transação
            request = TransactionRequest(
                amount=50.00,
                payment_method=PaymentMethod.CREDIT_CARD,
                installments=2
            )
            
            transaction_id = await terminal.start_transaction(request)
            assert transaction_id is not None
            
            # 3. Consultar status (aprovada)
            approved_response = "00" + "000000005000" + "123456789012" + "654321"
            mock_protocol.send_command.return_value = b'\x02' + approved_response.encode() + b'\x03'
            
            status = await terminal.get_transaction_status(transaction_id)
            assert status.status == TransactionStatus.APPROVED
            assert status.amount == 50.00
            
            # 4. Imprimir comprovante
            result = await terminal.print_receipt(transaction_id, "customer")
            assert result is True
            
            # 5. Desconectar
            disconnected = await terminal.disconnect()
            assert disconnected is True

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"]) 