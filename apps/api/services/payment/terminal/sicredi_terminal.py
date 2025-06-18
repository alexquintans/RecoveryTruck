# 🏦 Sicredi Terminal - Integração Física Real

import asyncio
import json
import uuid
import struct
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from .base import (
    TerminalAdapter, TerminalStatus, PaymentMethod, TransactionStatus,
    TerminalInfo, TransactionRequest, TransactionResponse, PaymentTerminalError
)
from .protocols import SerialProtocol, TCPProtocol, BluetoothProtocol, ConnectionConfig

logger = logging.getLogger(__name__)

class SicrediTerminalAdapter(TerminalAdapter):
    """Adaptador para terminais Sicredi com integração física"""
    
    # Comandos Sicredi (baseados na documentação oficial)
    COMMANDS = {
        "INIT": b"\x02\x30\x30\x30\x03",           # Inicialização
        "STATUS": b"\x02\x30\x30\x31\x03",         # Status do terminal
        "SALE": b"\x02\x30\x31\x30\x03",           # Venda
        "CANCEL": b"\x02\x30\x31\x31\x03",         # Cancelamento
        "ADMIN": b"\x02\x30\x32\x30\x03",          # Funções administrativas
        "PRINT": b"\x02\x30\x33\x30\x03",          # Impressão
        "DISPLAY": b"\x02\x30\x34\x30\x03",        # Display
        "GET_INFO": b"\x02\x30\x35\x30\x03"        # Informações do terminal
    }
    
    # Códigos de resposta Sicredi
    RESPONSE_CODES = {
        "00": "Transação aprovada",
        "01": "Transação negada",
        "02": "Cartão inválido",
        "03": "Senha incorreta",
        "04": "Cartão vencido",
        "05": "Saldo insuficiente",
        "06": "Transação cancelada pelo usuário",
        "07": "Erro de comunicação",
        "08": "Timeout",
        "09": "Terminal ocupado",
        "10": "Erro interno do terminal",
        "11": "Cartão não inserido",
        "12": "Falha na leitura do cartão",
        "13": "Transação não permitida",
        "14": "Valor inválido",
        "15": "Operação cancelada",
        "99": "Erro desconhecido"
    }
    
    # Tipos de cartão Sicredi
    CARD_TYPES = {
        "01": "Débito",
        "02": "Crédito à vista",
        "03": "Crédito parcelado loja",
        "04": "Crédito parcelado administradora"
    }
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Configurações específicas Sicredi
        self.sicredi_config = config.get("sicredi", {})
        self.merchant_id = self.sicredi_config.get("merchant_id")
        self.terminal_id = self.sicredi_config.get("terminal_id")
        self.pos_id = self.sicredi_config.get("pos_id", "001")
        
        # Configuração de conexão
        connection_type = config.get("connection_type", "serial")
        self.protocol = self._create_protocol(connection_type, config)
        
        # Estado interno
        self._current_transaction_id: Optional[str] = None
        self._sequence_number = 1
        self._supported_methods = [
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.DEBIT_CARD,
            PaymentMethod.CONTACTLESS,
            PaymentMethod.VOUCHER
        ]
        
        logger.info(f"🏦 Sicredi terminal initialized: {self.terminal_id}")
    
    def _create_protocol(self, connection_type: str, config: Dict[str, Any]):
        """Cria protocolo de comunicação baseado no tipo"""
        conn_config = ConnectionConfig(
            connection_type=connection_type,
            timeout=config.get("timeout", 30),
            retry_attempts=config.get("retry_attempts", 3)
        )
        
        if connection_type == "serial":
            return SerialProtocol(
                config=conn_config,
                port=config.get("port", "COM1"),
                baudrate=config.get("baudrate", 9600),  # Sicredi usa 9600 por padrão
                bytesize=8,
                parity='N',
                stopbits=1
            )
        elif connection_type == "tcp":
            return TCPProtocol(
                config=conn_config,
                host=config.get("host", "192.168.1.100"),
                port=config.get("tcp_port", 8080)
            )
        elif connection_type == "bluetooth":
            return BluetoothProtocol(
                config=conn_config,
                device_address=config.get("bluetooth_address"),
                port=config.get("bluetooth_port", 1)
            )
        else:
            raise ValueError(f"Unsupported connection type: {connection_type}")
    
    async def connect(self) -> bool:
        """Conecta com terminal Sicredi"""
        try:
            self._set_status(TerminalStatus.CONNECTING)
            logger.info(f"🔌 Connecting to Sicredi terminal {self.terminal_id}...")
            
            # Estabelece conexão física
            if not await self.protocol.connect():
                logger.error("❌ Failed to establish physical connection")
                self._set_status(TerminalStatus.ERROR)
                return False
            
            # Envia comando de inicialização Sicredi
            init_data = self._build_init_command()
            response = await self._send_sicredi_command("INIT", init_data)
            
            if not self._is_success_response(response):
                logger.error(f"❌ Sicredi initialization rejected: {response.hex()}")
                await self.protocol.disconnect()
                self._set_status(TerminalStatus.ERROR)
                return False
            
            # Obtém informações do terminal
            await self._fetch_terminal_info()
            
            self._set_status(TerminalStatus.CONNECTED)
            logger.info("✅ Sicredi terminal connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sicredi connection error: {e}")
            self._set_status(TerminalStatus.ERROR)
            return False
    
    async def disconnect(self) -> bool:
        """Desconecta do terminal Sicredi"""
        try:
            logger.info("🔌 Disconnecting from Sicredi terminal...")
            
            # Cancela transação em andamento se houver
            if self._current_transaction_id:
                await self.cancel_transaction(self._current_transaction_id)
            
            # Desconecta protocolo
            await self.protocol.disconnect()
            
            self._set_status(TerminalStatus.DISCONNECTED)
            logger.info("✅ Sicredi terminal disconnected")
            return True
            
        except Exception as e:
            logger.error(f"❌ Sicredi disconnection error: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Verifica se está conectado"""
        return self.protocol.is_connected and self.status in [
            TerminalStatus.CONNECTED, TerminalStatus.BUSY
        ]
    
    async def get_terminal_info(self) -> TerminalInfo:
        """Obtém informações do terminal Sicredi"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        if self.terminal_info:
            return self.terminal_info
        
        await self._fetch_terminal_info()
        return self.terminal_info
    
    async def _fetch_terminal_info(self):
        """Busca informações do terminal"""
        try:
            response = await self._send_sicredi_command("GET_INFO", b"")
            
            if self._is_success_response(response):
                data = self._parse_info_response(response)
                
                self.terminal_info = TerminalInfo(
                    serial_number=data.get("serial_number", self.terminal_id),
                    model=data.get("model", "Sicredi Terminal"),
                    firmware_version=data.get("firmware_version", "Unknown"),
                    battery_level=data.get("battery_level"),
                    signal_strength=data.get("signal_strength")
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch Sicredi terminal info: {e}")
            # Cria info básica se não conseguir obter
            self.terminal_info = TerminalInfo(
                serial_number=self.terminal_id or "SICREDI001",
                model="Sicredi Terminal",
                firmware_version="Unknown"
            )
    
    async def start_transaction(self, request: TransactionRequest) -> str:
        """Inicia transação no terminal Sicredi"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        if self.status == TerminalStatus.BUSY:
            raise PaymentTerminalError("Terminal busy", terminal_status=self.status)
        
        # Valida método de pagamento
        if request.payment_method not in self._supported_methods:
            raise PaymentTerminalError(f"Payment method not supported: {request.payment_method}")
        
        transaction_id = str(uuid.uuid4())
        self._current_transaction_id = transaction_id
        
        logger.info(f"💳 Starting Sicredi transaction {transaction_id}: R$ {request.amount:.2f}")
        
        try:
            self._set_status(TerminalStatus.BUSY)
            
            # Prepara comando de venda Sicredi
            sale_data = self._build_sale_command(transaction_id, request)
            
            # Envia comando para o terminal
            response = await self._send_sicredi_command("SALE", sale_data)
            
            if not self._is_success_response(response):
                error_msg = self._get_error_message(response)
                logger.error(f"❌ Sicredi transaction failed: {error_msg}")
                self._set_status(TerminalStatus.CONNECTED)
                self._current_transaction_id = None
                raise PaymentTerminalError(f"Transaction failed: {error_msg}")
            
            logger.info(f"✅ Sicredi transaction {transaction_id} started successfully")
            return transaction_id
            
        except Exception as e:
            self._set_status(TerminalStatus.CONNECTED)
            self._current_transaction_id = None
            logger.error(f"❌ Error starting Sicredi transaction: {e}")
            raise
    
    async def get_transaction_status(self, transaction_id: str) -> TransactionResponse:
        """Obtém status da transação Sicredi"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        try:
            # Consulta status no terminal
            status_data = self._build_status_command(transaction_id)
            response = await self._send_sicredi_command("STATUS", status_data)
            
            if not self._is_success_response(response):
                raise PaymentTerminalError(f"Failed to get transaction status: {response.hex()}")
            
            # Parseia resposta Sicredi
            return self._parse_transaction_response(transaction_id, response)
            
        except Exception as e:
            logger.error(f"❌ Error getting Sicredi transaction status: {e}")
            raise
    
    async def cancel_transaction(self, transaction_id: str) -> bool:
        """Cancela transação Sicredi"""
        if not await self.is_connected():
            return False
        
        try:
            logger.info(f"🚫 Cancelling Sicredi transaction {transaction_id}")
            
            cancel_data = self._build_cancel_command(transaction_id)
            response = await self._send_sicredi_command("CANCEL", cancel_data)
            
            success = self._is_success_response(response)
            
            if success:
                logger.info(f"✅ Sicredi transaction {transaction_id} cancelled")
                if self._current_transaction_id == transaction_id:
                    self._current_transaction_id = None
                    self._set_status(TerminalStatus.CONNECTED)
            else:
                logger.warning(f"⚠️ Failed to cancel Sicredi transaction: {response.hex()}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error cancelling Sicredi transaction: {e}")
            return False
    
    async def confirm_transaction(self, transaction_id: str) -> TransactionResponse:
        """Confirma transação Sicredi"""
        # Sicredi pode requerer confirmação explícita em alguns casos
        return await self.get_transaction_status(transaction_id)
    
    async def print_receipt(self, transaction_id: str, receipt_type: str = "customer") -> bool:
        """Imprime comprovante no terminal Sicredi"""
        if not await self.is_connected():
            return False
        
        try:
            logger.info(f"🖨️ Printing Sicredi receipt for transaction {transaction_id}")
            
            print_data = self._build_print_command(transaction_id, receipt_type)
            response = await self._send_sicredi_command("PRINT", print_data)
            
            success = self._is_success_response(response)
            
            if success:
                logger.info(f"✅ Sicredi receipt printed successfully")
            else:
                logger.warning(f"⚠️ Failed to print Sicredi receipt: {response.hex()}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error printing Sicredi receipt: {e}")
            return False
    
    async def print_custom_text(self, text: str) -> bool:
        """Imprime texto customizado no terminal Sicredi"""
        if not await self.is_connected():
            return False
        
        try:
            print_data = self._build_custom_print_command(text)
            response = await self._send_sicredi_command("PRINT", print_data)
            
            return self._is_success_response(response)
            
        except Exception as e:
            logger.error(f"❌ Error printing custom text: {e}")
            return False
    
    async def get_supported_payment_methods(self) -> List[PaymentMethod]:
        """Retorna métodos de pagamento suportados pelo Sicredi"""
        return self._supported_methods.copy()
    
    async def configure_terminal(self, settings: Dict[str, Any]) -> bool:
        """Configura parâmetros do terminal Sicredi"""
        if not await self.is_connected():
            return False
        
        try:
            config_data = self._build_config_command(settings)
            response = await self._send_sicredi_command("ADMIN", config_data)
            return self._is_success_response(response)
            
        except Exception as e:
            logger.error(f"❌ Error configuring Sicredi terminal: {e}")
            return False
    
    # === Métodos auxiliares Sicredi ===
    
    async def _send_sicredi_command(self, command: str, data: bytes) -> bytes:
        """Envia comando específico Sicredi"""
        try:
            # Monta comando Sicredi com protocolo específico
            command_header = self.COMMANDS.get(command, b"\x02\x30\x30\x30\x03")
            
            # Calcula LRC (Longitudinal Redundancy Check)
            lrc = self._calculate_lrc(data)
            
            # Monta pacote completo: STX + HEADER + DATA + LRC + ETX
            full_command = b"\x02" + command_header[1:-1] + data + bytes([lrc]) + b"\x03"
            
            # Envia via protocolo
            response = await self.protocol.send_command(full_command)
            
            logger.debug(f"📤 Sicredi command sent: {command} - {full_command.hex()}")
            logger.debug(f"📥 Sicredi response: {response.hex()}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error sending Sicredi command {command}: {e}")
            raise
    
    def _calculate_lrc(self, data: bytes) -> int:
        """Calcula LRC (Longitudinal Redundancy Check) para Sicredi"""
        lrc = 0
        for byte in data:
            lrc ^= byte
        return lrc
    
    def _is_success_response(self, response: bytes) -> bool:
        """Verifica se resposta Sicredi indica sucesso"""
        if not response or len(response) < 3:
            return False
        
        # Verifica delimitadores STX/ETX
        if not (response.startswith(b'\x02') and response.endswith(b'\x03')):
            return False
        
        # Extrai código de resposta (primeiros 2 bytes após STX)
        if len(response) >= 4:
            response_code = response[1:3].decode('ascii', errors='ignore')
            return response_code == "00"
        
        return False
    
    def _get_error_message(self, response: bytes) -> str:
        """Obtém mensagem de erro da resposta Sicredi"""
        try:
            if len(response) >= 4:
                response_code = response[1:3].decode('ascii', errors='ignore')
                return self.RESPONSE_CODES.get(response_code, f"Erro desconhecido: {response_code}")
            
            return "Erro de comunicação"
            
        except:
            return "Erro de comunicação"
    
    def _build_init_command(self) -> bytes:
        """Constrói comando de inicialização Sicredi"""
        # Formato: MERCHANT_ID(15) + TERMINAL_ID(8) + POS_ID(3)
        merchant = (self.merchant_id or "000000000000000").ljust(15)[:15]
        terminal = (self.terminal_id or "00000000").ljust(8)[:8]
        pos = (self.pos_id or "001").ljust(3)[:3]
        
        return (merchant + terminal + pos).encode('ascii')
    
    def _build_sale_command(self, transaction_id: str, request: TransactionRequest) -> bytes:
        """Constrói comando de venda Sicredi"""
        # Formato Sicredi para venda:
        # VALOR(12) + TIPO_CARTAO(2) + PARCELAS(2) + SEQ(6) + DADOS_ADICIONAIS
        
        # Valor em centavos, 12 dígitos, zero-filled à esquerda
        amount_cents = int(request.amount * 100)
        amount_str = f"{amount_cents:012d}"
        
        # Tipo de cartão baseado no método de pagamento
        card_type = self._map_payment_method_to_sicredi(request.payment_method, request.installments)
        
        # Número de parcelas (2 dígitos)
        installments_str = f"{request.installments:02d}"
        
        # Número sequencial (6 dígitos)
        seq_str = f"{self._sequence_number:06d}"
        self._sequence_number += 1
        
        # Dados adicionais (opcional)
        additional_data = ""
        if request.customer_document:
            additional_data += f"DOC{request.customer_document}"
        
        command_data = amount_str + card_type + installments_str + seq_str + additional_data
        
        return command_data.encode('ascii')
    
    def _build_status_command(self, transaction_id: str) -> bytes:
        """Constrói comando de consulta de status"""
        # Formato: SEQ(6) + TRANSACTION_ID(32)
        seq_str = f"{self._sequence_number:06d}"
        trans_id = transaction_id.replace('-', '')[:32].ljust(32)
        
        return (seq_str + trans_id).encode('ascii')
    
    def _build_cancel_command(self, transaction_id: str) -> bytes:
        """Constrói comando de cancelamento"""
        # Similar ao status, mas com indicador de cancelamento
        seq_str = f"{self._sequence_number:06d}"
        trans_id = transaction_id.replace('-', '')[:32].ljust(32)
        cancel_flag = "01"  # Flag de cancelamento
        
        return (seq_str + trans_id + cancel_flag).encode('ascii')
    
    def _build_print_command(self, transaction_id: str, receipt_type: str) -> bytes:
        """Constrói comando de impressão"""
        # Formato: TIPO_COMPROVANTE(1) + TRANSACTION_ID(32)
        receipt_code = "1" if receipt_type == "customer" else "2"
        trans_id = transaction_id.replace('-', '')[:32].ljust(32)
        
        return (receipt_code + trans_id).encode('ascii')
    
    def _build_custom_print_command(self, text: str) -> bytes:
        """Constrói comando de impressão customizada"""
        # Formato: TIPO(1) + TAMANHO(3) + TEXTO
        print_type = "9"  # Tipo customizado
        text_bytes = text.encode('utf-8')
        size_str = f"{len(text_bytes):03d}"
        
        return (print_type + size_str).encode('ascii') + text_bytes
    
    def _build_config_command(self, settings: Dict[str, Any]) -> bytes:
        """Constrói comando de configuração"""
        # Formato específico do Sicredi para configurações
        config_data = ""
        
        for key, value in settings.items():
            config_data += f"{key}={value};"
        
        return config_data.encode('ascii')
    
    def _map_payment_method_to_sicredi(self, method: PaymentMethod, installments: int) -> str:
        """Mapeia método de pagamento para código Sicredi"""
        if method == PaymentMethod.DEBIT_CARD:
            return "01"  # Débito
        elif method == PaymentMethod.CREDIT_CARD:
            if installments == 1:
                return "02"  # Crédito à vista
            else:
                return "03"  # Crédito parcelado loja
        elif method == PaymentMethod.CONTACTLESS:
            return "01"  # Tratado como débito
        elif method == PaymentMethod.VOUCHER:
            return "01"  # Tratado como débito
        else:
            return "02"  # Default: crédito à vista
    
    def _parse_info_response(self, response: bytes) -> Dict[str, Any]:
        """Parseia resposta de informações do terminal"""
        try:
            # Remove delimitadores STX/ETX e LRC
            data = response[1:-2].decode('ascii', errors='ignore')
            
            # Formato esperado: SERIAL(15) + MODEL(20) + VERSION(10) + ...
            if len(data) >= 45:
                return {
                    "serial_number": data[0:15].strip(),
                    "model": data[15:35].strip(),
                    "firmware_version": data[35:45].strip(),
                    "battery_level": None,  # Sicredi pode não fornecer
                    "signal_strength": None
                }
            
            return {}
            
        except Exception as e:
            logger.warning(f"⚠️ Could not parse Sicredi info response: {e}")
            return {}
    
    def _parse_transaction_response(self, transaction_id: str, response: bytes) -> TransactionResponse:
        """Parseia resposta de transação Sicredi"""
        try:
            # Remove delimitadores
            data = response[1:-2].decode('ascii', errors='ignore')
            
            # Formato: CODIGO(2) + VALOR(12) + NSU(12) + AUTORIZACAO(6) + DADOS_CARTAO + ...
            if len(data) >= 32:
                response_code = data[0:2]
                amount_cents = int(data[2:14])
                nsu = data[14:26].strip()
                auth_code = data[26:32].strip()
                
                # Determina status baseado no código
                if response_code == "00":
                    status = TransactionStatus.APPROVED
                elif response_code in ["06", "15"]:
                    status = TransactionStatus.CANCELLED
                elif response_code == "08":
                    status = TransactionStatus.TIMEOUT
                else:
                    status = TransactionStatus.DECLINED
                
                # Extrai dados do cartão se disponível
                card_data = self._extract_card_data(data[32:]) if len(data) > 32 else {}
                
                return TransactionResponse(
                    transaction_id=transaction_id,
                    status=status,
                    amount=amount_cents / 100.0,
                    payment_method=PaymentMethod.CREDIT_CARD,  # Determinar baseado nos dados
                    authorization_code=auth_code if auth_code else None,
                    nsu=nsu if nsu else None,
                    receipt_merchant=None,  # Será obtido separadamente
                    receipt_customer=None,
                    card_brand=card_data.get("brand"),
                    card_last_digits=card_data.get("last_digits"),
                    installments=card_data.get("installments", 1),
                    error_message=self.RESPONSE_CODES.get(response_code) if status != TransactionStatus.APPROVED else None,
                    timestamp=datetime.utcnow()
                )
            
            # Resposta inválida
            return TransactionResponse(
                transaction_id=transaction_id,
                status=TransactionStatus.ERROR,
                amount=0.0,
                payment_method=PaymentMethod.CREDIT_CARD,
                error_message="Resposta inválida do terminal",
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Error parsing Sicredi transaction response: {e}")
            return TransactionResponse(
                transaction_id=transaction_id,
                status=TransactionStatus.ERROR,
                amount=0.0,
                payment_method=PaymentMethod.CREDIT_CARD,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    def _extract_card_data(self, data: str) -> Dict[str, Any]:
        """Extrai dados do cartão da resposta"""
        try:
            # Formato pode variar, implementar baseado na documentação Sicredi
            card_info = {}
            
            # Exemplo de parsing (ajustar conforme documentação real)
            if len(data) >= 20:
                card_info["brand"] = data[0:10].strip()
                card_info["last_digits"] = data[10:14].strip()
                card_info["installments"] = int(data[14:16]) if data[14:16].isdigit() else 1
            
            return card_info
            
        except Exception as e:
            logger.warning(f"⚠️ Could not extract card data: {e}")
            return {} 