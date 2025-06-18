# 💰 SafraPay Terminal - Implementação Completa

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

class SafraPayTerminalAdapter(TerminalAdapter):
    """Adaptador para terminais SafraPay com integração física completa"""
    
    # Comandos SafraPay (baseados na documentação oficial)
    COMMANDS = {
        "INIT": b"\x02SF_INIT\x03",
        "SALE": b"\x02SF_SALE\x03", 
        "STATUS": b"\x02SF_STATUS\x03",
        "CANCEL": b"\x02SF_CANCEL\x03",
        "PRINT": b"\x02SF_PRINT\x03",
        "CONFIG": b"\x02SF_CONFIG\x03",
        "INFO": b"\x02SF_INFO\x03",
        "ADMIN": b"\x02SF_ADMIN\x03"
    }
    
    # Códigos de resposta SafraPay
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
        "11": "Bandeira não aceita",
        "12": "Valor inválido",
        "13": "Parcelamento não permitido",
        "14": "Limite excedido",
        "15": "Operação não permitida",
        "16": "Falha na autenticação",
        "17": "Terminal não habilitado",
        "99": "Erro desconhecido"
    }
    
    # Tipos de cartão SafraPay
    CARD_TYPES = {
        "01": "Débito",
        "02": "Crédito à vista",
        "03": "Crédito parcelado loja",
        "04": "Crédito parcelado administradora",
        "05": "Voucher alimentação",
        "06": "Voucher refeição"
    }
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Configurações específicas SafraPay
        self.safrapay_config = config.get("safrapay", {})
        self.merchant_id = self.safrapay_config.get("merchant_id")
        self.terminal_id = self.safrapay_config.get("terminal_id")
        self.establishment_code = self.safrapay_config.get("establishment_code")
        self.api_key = self.safrapay_config.get("api_key")
        
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
            PaymentMethod.VOUCHER  # SafraPay tem forte suporte a vouchers
        ]
        
        logger.info(f"💰 SafraPay terminal initialized: {self.terminal_id}")
    
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
                baudrate=config.get("baudrate", 9600),  # SafraPay usa 9600
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
        """Conecta com terminal SafraPay"""
        try:
            self._set_status(TerminalStatus.CONNECTING)
            logger.info(f"🔌 Connecting to SafraPay terminal {self.terminal_id}...")
            
            # Estabelece conexão física
            if not await self.protocol.connect():
                logger.error("❌ Failed to establish physical connection")
                self._set_status(TerminalStatus.ERROR)
                return False
            
            # Envia comando de inicialização SafraPay
            init_data = self._build_init_command()
            response = await self._send_safrapay_command("INIT", init_data)
            
            if not self._is_success_response(response):
                logger.error(f"❌ SafraPay initialization rejected")
                await self.protocol.disconnect()
                self._set_status(TerminalStatus.ERROR)
                return False
            
            # Obtém informações do terminal
            await self._fetch_terminal_info()
            
            self._set_status(TerminalStatus.CONNECTED)
            logger.info("✅ SafraPay terminal connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ SafraPay connection error: {e}")
            self._set_status(TerminalStatus.ERROR)
            return False
    
    async def disconnect(self) -> bool:
        """Desconecta do terminal SafraPay"""
        try:
            logger.info("🔌 Disconnecting from SafraPay terminal...")
            
            if self._current_transaction_id:
                await self.cancel_transaction(self._current_transaction_id)
            
            await self.protocol.disconnect()
            self._set_status(TerminalStatus.DISCONNECTED)
            logger.info("✅ SafraPay terminal disconnected")
            return True
            
        except Exception as e:
            logger.error(f"❌ SafraPay disconnection error: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Verifica se está conectado"""
        return self.protocol.is_connected and self.status in [
            TerminalStatus.CONNECTED, TerminalStatus.BUSY
        ]
    
    async def get_terminal_info(self) -> TerminalInfo:
        """Obtém informações do terminal SafraPay"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        if self.terminal_info:
            return self.terminal_info
        
        await self._fetch_terminal_info()
        return self.terminal_info
    
    async def _fetch_terminal_info(self):
        """Busca informações do terminal"""
        try:
            response = await self._send_safrapay_command("INFO", {})
            
            if self._is_success_response(response):
                data = self._parse_info_response(response)
                
                self.terminal_info = TerminalInfo(
                    serial_number=data.get("serial_number", self.terminal_id),
                    model=data.get("model", "SafraPay Terminal"),
                    firmware_version=data.get("firmware_version", "Unknown"),
                    battery_level=data.get("battery_level"),
                    signal_strength=data.get("signal_strength")
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch SafraPay terminal info: {e}")
            self.terminal_info = TerminalInfo(
                serial_number=self.terminal_id or "SAFRA001",
                model="SafraPay Terminal",
                firmware_version="Unknown"
            )
    
    async def start_transaction(self, request: TransactionRequest) -> str:
        """Inicia transação no terminal SafraPay"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        if self.status == TerminalStatus.BUSY:
            raise PaymentTerminalError("Terminal busy", terminal_status=self.status)
        
        if request.payment_method not in self._supported_methods:
            raise PaymentTerminalError(f"Payment method not supported: {request.payment_method}")
        
        transaction_id = str(uuid.uuid4())
        self._current_transaction_id = transaction_id
        
        logger.info(f"💰 Starting SafraPay transaction {transaction_id}: R$ {request.amount:.2f}")
        
        try:
            self._set_status(TerminalStatus.BUSY)
            
            # Comando específico SafraPay
            sale_data = self._build_sale_command(transaction_id, request)
            response = await self._send_safrapay_command("SALE", sale_data)
            
            if not self._is_success_response(response):
                error_msg = self._get_error_message(response)
                logger.error(f"❌ SafraPay transaction failed: {error_msg}")
                self._set_status(TerminalStatus.CONNECTED)
                self._current_transaction_id = None
                raise PaymentTerminalError(f"Transaction failed: {error_msg}")
            
            logger.info(f"✅ SafraPay transaction {transaction_id} started successfully")
            return transaction_id
            
        except Exception as e:
            self._set_status(TerminalStatus.CONNECTED)
            self._current_transaction_id = None
            logger.error(f"❌ Error starting SafraPay transaction: {e}")
            raise
    
    async def get_transaction_status(self, transaction_id: str) -> TransactionResponse:
        """Obtém status da transação SafraPay"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        try:
            status_data = self._build_status_command(transaction_id)
            response = await self._send_safrapay_command("STATUS", status_data)
            
            if not self._is_success_response(response):
                raise PaymentTerminalError(f"Failed to get transaction status")
            
            return self._parse_transaction_response(transaction_id, response)
            
        except Exception as e:
            logger.error(f"❌ Error getting SafraPay transaction status: {e}")
            raise
    
    async def cancel_transaction(self, transaction_id: str) -> bool:
        """Cancela transação SafraPay"""
        if not await self.is_connected():
            return False
        
        try:
            logger.info(f"🚫 Cancelling SafraPay transaction {transaction_id}")
            
            cancel_data = self._build_cancel_command(transaction_id)
            response = await self._send_safrapay_command("CANCEL", cancel_data)
            
            success = self._is_success_response(response)
            
            if success:
                logger.info(f"✅ SafraPay transaction {transaction_id} cancelled")
                if self._current_transaction_id == transaction_id:
                    self._current_transaction_id = None
                    self._set_status(TerminalStatus.CONNECTED)
            else:
                logger.warning(f"⚠️ Failed to cancel SafraPay transaction")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error cancelling SafraPay transaction: {e}")
            return False
    
    async def confirm_transaction(self, transaction_id: str) -> TransactionResponse:
        """Confirma transação SafraPay"""
        return await self.get_transaction_status(transaction_id)
    
    async def print_receipt(self, transaction_id: str, receipt_type: str = "customer") -> bool:
        """Imprime comprovante no terminal SafraPay"""
        if not await self.is_connected():
            return False
        
        try:
            logger.info(f"🖨️ Printing SafraPay receipt for transaction {transaction_id}")
            
            print_data = self._build_print_command(transaction_id, receipt_type)
            response = await self._send_safrapay_command("PRINT", print_data)
            
            success = self._is_success_response(response)
            
            if success:
                logger.info(f"✅ SafraPay receipt printed successfully")
            else:
                logger.warning(f"⚠️ Failed to print SafraPay receipt")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error printing SafraPay receipt: {e}")
            return False
    
    async def print_custom_text(self, text: str) -> bool:
        """Imprime texto customizado no terminal SafraPay"""
        if not await self.is_connected():
            return False
        
        try:
            print_data = self._build_custom_print_command(text)
            response = await self._send_safrapay_command("PRINT", print_data)
            
            return self._is_success_response(response)
            
        except Exception as e:
            logger.error(f"❌ Error printing custom text: {e}")
            return False
    
    async def get_supported_payment_methods(self) -> List[PaymentMethod]:
        """Retorna métodos de pagamento suportados pelo SafraPay"""
        return self._supported_methods.copy()
    
    async def configure_terminal(self, settings: Dict[str, Any]) -> bool:
        """Configura parâmetros do terminal SafraPay"""
        if not await self.is_connected():
            return False
        
        try:
            config_data = self._build_config_command(settings)
            response = await self._send_safrapay_command("CONFIG", config_data)
            return self._is_success_response(response)
            
        except Exception as e:
            logger.error(f"❌ Error configuring SafraPay terminal: {e}")
            return False
    
    # === Métodos auxiliares SafraPay ===
    
    async def _send_safrapay_command(self, command: str, data: Dict[str, Any]) -> bytes:
        """Envia comando específico SafraPay"""
        try:
            # Protocolo SafraPay (formato proprietário + JSON)
            command_data = {
                "command": command,
                "sequence": self._sequence_number,
                "merchant_id": self.merchant_id,
                "terminal_id": self.terminal_id,
                "establishment_code": self.establishment_code,
                "api_key": self.api_key,
                "timestamp": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
                "data": data
            }
            
            self._sequence_number += 1
            
            # Calcula checksum SafraPay
            json_data = json.dumps(command_data, separators=(',', ':'))
            checksum = self._calculate_safrapay_checksum(json_data.encode('utf-8'))
            
            # Monta comando completo
            full_command = (self.COMMANDS.get(command, b"\x02SF_CMD\x03") + 
                          json_data.encode('utf-8') + 
                          f"|{checksum:04X}".encode('ascii') + 
                          b"\x03")
            
            response = await self.protocol.send_command(full_command)
            
            logger.debug(f"📤 SafraPay command sent: {command}")
            logger.debug(f"📥 SafraPay response: {response.hex()}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error sending SafraPay command {command}: {e}")
            raise
    
    def _calculate_safrapay_checksum(self, data: bytes) -> int:
        """Calcula checksum específico do SafraPay"""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
    
    def _is_success_response(self, response: bytes) -> bool:
        """Verifica se resposta SafraPay indica sucesso"""
        try:
            if not response:
                return False
            
            # SafraPay retorna formato: STX + JSON + |CHECKSUM + ETX
            response_str = response.decode('utf-8', errors='ignore')
            
            # Remove delimitadores
            if response_str.startswith('\x02'):
                response_str = response_str[1:]
            if response_str.endswith('\x03'):
                response_str = response_str[:-1]
            
            # Separa JSON do checksum
            if '|' in response_str:
                json_part, checksum_part = response_str.rsplit('|', 1)
            else:
                json_part = response_str
            
            # Tenta parsear JSON
            try:
                response_json = json.loads(json_part)
                return (response_json.get("status") == "approved" or 
                       response_json.get("response_code") == "00")
            except json.JSONDecodeError:
                # Fallback para protocolo simples
                return "00" in response_str or "approved" in response_str.lower()
            
        except:
            return False
    
    def _get_error_message(self, response: bytes) -> str:
        """Obtém mensagem de erro da resposta SafraPay"""
        try:
            response_str = response.decode('utf-8', errors='ignore')
            
            # Remove delimitadores e checksum
            if response_str.startswith('\x02'):
                response_str = response_str[1:]
            if response_str.endswith('\x03'):
                response_str = response_str[:-1]
            if '|' in response_str:
                response_str = response_str.rsplit('|', 1)[0]
            
            try:
                response_json = json.loads(response_str)
                error_code = response_json.get("response_code", "99")
                error_message = response_json.get("error_message")
                
                if error_message:
                    return error_message
                
                return self.RESPONSE_CODES.get(error_code, f"Erro desconhecido: {error_code}")
            except json.JSONDecodeError:
                # Busca código de erro no texto
                for code, message in self.RESPONSE_CODES.items():
                    if code in response_str:
                        return message
                
                return "Erro de comunicação"
            
        except:
            return "Erro de comunicação"
    
    def _build_init_command(self) -> Dict[str, Any]:
        """Constrói comando de inicialização SafraPay"""
        return {
            "merchant_id": self.merchant_id,
            "terminal_id": self.terminal_id,
            "establishment_code": self.establishment_code,
            "api_key": self.api_key,
            "version": "1.0"
        }
    
    def _build_sale_command(self, transaction_id: str, request: TransactionRequest) -> Dict[str, Any]:
        """Constrói comando de venda SafraPay"""
        command_data = {
            "transaction_id": transaction_id,
            "amount": int(request.amount * 100),  # Centavos
            "card_type": self._map_payment_method_to_safrapay(request.payment_method, request.installments),
            "installments": request.installments,
            "description": request.description or "Pagamento RecoveryTruck"
        }
        
        # Dados adicionais
        if request.customer_name:
            command_data["customer_name"] = request.customer_name
        if request.customer_document:
            command_data["customer_document"] = request.customer_document
        
        return command_data
    
    def _build_status_command(self, transaction_id: str) -> Dict[str, Any]:
        """Constrói comando de consulta de status"""
        return {
            "transaction_id": transaction_id
        }
    
    def _build_cancel_command(self, transaction_id: str) -> Dict[str, Any]:
        """Constrói comando de cancelamento"""
        return {
            "transaction_id": transaction_id,
            "reason": "user_request"
        }
    
    def _build_print_command(self, transaction_id: str, receipt_type: str) -> Dict[str, Any]:
        """Constrói comando de impressão"""
        return {
            "transaction_id": transaction_id,
            "receipt_type": receipt_type,
            "copies": 1
        }
    
    def _build_custom_print_command(self, text: str) -> Dict[str, Any]:
        """Constrói comando de impressão customizada"""
        return {
            "type": "custom",
            "text": text,
            "font_size": "normal",
            "alignment": "center"
        }
    
    def _build_config_command(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói comando de configuração"""
        return {
            "settings": settings
        }
    
    def _map_payment_method_to_safrapay(self, method: PaymentMethod, installments: int) -> str:
        """Mapeia método de pagamento para código SafraPay"""
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
            return "05"  # Voucher alimentação (padrão)
        else:
            return "02"  # Default: crédito à vista
    
    def _parse_info_response(self, response: bytes) -> Dict[str, Any]:
        """Parseia resposta de informações do terminal"""
        try:
            response_str = response.decode('utf-8', errors='ignore')
            
            # Remove delimitadores e checksum
            if response_str.startswith('\x02'):
                response_str = response_str[1:]
            if response_str.endswith('\x03'):
                response_str = response_str[:-1]
            if '|' in response_str:
                response_str = response_str.rsplit('|', 1)[0]
            
            response_json = json.loads(response_str)
            
            return {
                "serial_number": response_json.get("serial_number", self.terminal_id),
                "model": response_json.get("model", "SafraPay Terminal"),
                "firmware_version": response_json.get("firmware_version", "Unknown"),
                "battery_level": response_json.get("battery_level"),
                "signal_strength": response_json.get("signal_strength")
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Could not parse SafraPay info response: {e}")
            return {}
    
    def _parse_transaction_response(self, transaction_id: str, response: bytes) -> TransactionResponse:
        """Parseia resposta de transação SafraPay"""
        try:
            response_str = response.decode('utf-8', errors='ignore')
            
            # Remove delimitadores e checksum
            if response_str.startswith('\x02'):
                response_str = response_str[1:]
            if response_str.endswith('\x03'):
                response_str = response_str[:-1]
            if '|' in response_str:
                response_str = response_str.rsplit('|', 1)[0]
            
            response_json = json.loads(response_str)
            
            # Mapeia status SafraPay para status interno
            response_code = response_json.get("response_code", "99")
            if response_code == "00":
                status = TransactionStatus.APPROVED
            elif response_code == "06":
                status = TransactionStatus.CANCELLED
            elif response_code == "08":
                status = TransactionStatus.TIMEOUT
            else:
                status = TransactionStatus.DECLINED
            
            # Dados da transação
            amount = response_json.get("amount", 0) / 100.0  # Converte centavos
            card_type = response_json.get("card_type", "02")
            
            # Mapeia tipo de cartão de volta para método
            if card_type == "01":
                payment_method = PaymentMethod.DEBIT_CARD
            elif card_type in ["05", "06"]:
                payment_method = PaymentMethod.VOUCHER
            else:
                payment_method = PaymentMethod.CREDIT_CARD
            
            return TransactionResponse(
                transaction_id=transaction_id,
                status=status,
                amount=amount,
                payment_method=payment_method,
                authorization_code=response_json.get("authorization_code"),
                nsu=response_json.get("nsu"),
                receipt_merchant=response_json.get("receipt_merchant"),
                receipt_customer=response_json.get("receipt_customer"),
                card_brand=response_json.get("card_brand"),
                card_last_digits=response_json.get("card_last_digits"),
                installments=response_json.get("installments", 1),
                error_message=self.RESPONSE_CODES.get(response_code) if status != TransactionStatus.APPROVED else None,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Error parsing SafraPay transaction response: {e}")
            return TransactionResponse(
                transaction_id=transaction_id,
                status=TransactionStatus.ERROR,
                amount=0.0,
                payment_method=PaymentMethod.CREDIT_CARD,
                error_message=str(e),
                timestamp=datetime.utcnow()
            ) 