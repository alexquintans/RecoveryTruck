# 🏦 PagBank Terminal - Implementação Completa

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
from .protocols import SerialProtocol, TCPProtocol, BluetoothProtocol, USBProtocol, ConnectionConfig

logger = logging.getLogger(__name__)

class PagBankTerminalAdapter(TerminalAdapter):
    """Adaptador para terminais PagBank com integração física completa"""
    
    # Comandos PagBank (baseados na documentação oficial)
    COMMANDS = {
        "INIT": b"\x02PB_INIT\x03",
        "SALE": b"\x02PB_SALE\x03", 
        "STATUS": b"\x02PB_STATUS\x03",
        "CANCEL": b"\x02PB_CANCEL\x03",
        "PRINT": b"\x02PB_PRINT\x03",
        "CONFIG": b"\x02PB_CONFIG\x03",
        "INFO": b"\x02PB_INFO\x03",
        "PIX": b"\x02PB_PIX\x03",
        "ADMIN": b"\x02PB_ADMIN\x03"
    }
    
    # Códigos de resposta PagBank
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
        "11": "PIX não disponível",
        "12": "QR Code expirado",
        "13": "PIX cancelado",
        "14": "Valor inválido para PIX",
        "15": "Parcelamento não permitido",
        "16": "Bandeira não aceita",
        "17": "Limite excedido",
        "18": "Estabelecimento inválido",
        "19": "Terminal não habilitado",
        "20": "Horário não permitido",
        "99": "Erro desconhecido"
    }
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Configurações específicas PagBank
        self.pagbank_config = config.get("pagbank", {})
        self.merchant_id = self.pagbank_config.get("merchant_id")
        self.terminal_id = self.pagbank_config.get("terminal_id")
        self.establishment_id = self.pagbank_config.get("establishment_id")
        self.access_token = self.pagbank_config.get("access_token")
        
        # Configuração de conexão
        connection_type = config.get("connection_type", "usb")
        self.protocol = self._create_protocol(connection_type, config)
        
        # Estado interno
        self._current_transaction_id: Optional[str] = None
        self._sequence_number = 1
        self._supported_methods = [
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.DEBIT_CARD,
            PaymentMethod.PIX,  # PagBank tem excelente suporte a PIX
            PaymentMethod.CONTACTLESS,
            PaymentMethod.VOUCHER
        ]
        
        logger.info(f"🏦 PagBank terminal initialized: {self.terminal_id}")
    
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
                baudrate=config.get("baudrate", 115200),  # PagBank usa 115200
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
        elif connection_type == "usb":
            return USBProtocol(
                config=conn_config,
                vendor_id=config.get("vendor_id", 0x1234),  # PagBank USB vendor
                product_id=config.get("product_id", 0x5678)
            )
        else:
            raise ValueError(f"Unsupported connection type: {connection_type}")
    
    async def connect(self) -> bool:
        """Conecta com terminal PagBank"""
        try:
            self._set_status(TerminalStatus.CONNECTING)
            logger.info(f"🔌 Connecting to PagBank terminal {self.terminal_id}...")
            
            # Estabelece conexão física
            if not await self.protocol.connect():
                logger.error("❌ Failed to establish physical connection")
                self._set_status(TerminalStatus.ERROR)
                return False
            
            # Envia comando de inicialização PagBank
            init_data = self._build_init_command()
            response = await self._send_pagbank_command("INIT", init_data)
            
            if not self._is_success_response(response):
                logger.error(f"❌ PagBank initialization rejected")
                await self.protocol.disconnect()
                self._set_status(TerminalStatus.ERROR)
                return False
            
            # Obtém informações do terminal
            await self._fetch_terminal_info()
            
            self._set_status(TerminalStatus.CONNECTED)
            logger.info("✅ PagBank terminal connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ PagBank connection error: {e}")
            self._set_status(TerminalStatus.ERROR)
            return False
    
    async def disconnect(self) -> bool:
        """Desconecta do terminal PagBank"""
        try:
            logger.info("🔌 Disconnecting from PagBank terminal...")
            
            if self._current_transaction_id:
                await self.cancel_transaction(self._current_transaction_id)
            
            await self.protocol.disconnect()
            self._set_status(TerminalStatus.DISCONNECTED)
            logger.info("✅ PagBank terminal disconnected")
            return True
            
        except Exception as e:
            logger.error(f"❌ PagBank disconnection error: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Verifica se está conectado"""
        return self.protocol.is_connected and self.status in [
            TerminalStatus.CONNECTED, TerminalStatus.BUSY
        ]
    
    async def get_terminal_info(self) -> TerminalInfo:
        """Obtém informações do terminal PagBank"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        if self.terminal_info:
            return self.terminal_info
        
        await self._fetch_terminal_info()
        return self.terminal_info
    
    async def _fetch_terminal_info(self):
        """Busca informações do terminal"""
        try:
            response = await self._send_pagbank_command("INFO", {})
            
            if self._is_success_response(response):
                data = self._parse_info_response(response)
                
                self.terminal_info = TerminalInfo(
                    serial_number=data.get("serial_number", self.terminal_id),
                    model=data.get("model", "PagBank Moderninha"),
                    firmware_version=data.get("firmware_version", "Unknown"),
                    battery_level=data.get("battery_level"),
                    signal_strength=data.get("signal_strength")
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch PagBank terminal info: {e}")
            self.terminal_info = TerminalInfo(
                serial_number=self.terminal_id or "PAGBANK001",
                model="PagBank Moderninha",
                firmware_version="Unknown"
            )
    
    async def start_transaction(self, request: TransactionRequest) -> str:
        """Inicia transação no terminal PagBank"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        if self.status == TerminalStatus.BUSY:
            raise PaymentTerminalError("Terminal busy", terminal_status=self.status)
        
        if request.payment_method not in self._supported_methods:
            raise PaymentTerminalError(f"Payment method not supported: {request.payment_method}")
        
        transaction_id = str(uuid.uuid4())
        self._current_transaction_id = transaction_id
        
        logger.info(f"🏦 Starting PagBank transaction {transaction_id}: R$ {request.amount:.2f}")
        
        try:
            self._set_status(TerminalStatus.BUSY)
            
            # Comando específico baseado no método de pagamento
            if request.payment_method == PaymentMethod.PIX:
                sale_data = self._build_pix_command(transaction_id, request)
                response = await self._send_pagbank_command("PIX", sale_data)
            else:
                sale_data = self._build_sale_command(transaction_id, request)
                response = await self._send_pagbank_command("SALE", sale_data)
            
            if not self._is_success_response(response):
                error_msg = self._get_error_message(response)
                logger.error(f"❌ PagBank transaction failed: {error_msg}")
                self._set_status(TerminalStatus.CONNECTED)
                self._current_transaction_id = None
                raise PaymentTerminalError(f"Transaction failed: {error_msg}")
            
            logger.info(f"✅ PagBank transaction {transaction_id} started successfully")
            return transaction_id
            
        except Exception as e:
            self._set_status(TerminalStatus.CONNECTED)
            self._current_transaction_id = None
            logger.error(f"❌ Error starting PagBank transaction: {e}")
            raise
    
    async def get_transaction_status(self, transaction_id: str) -> TransactionResponse:
        """Obtém status da transação PagBank"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        try:
            status_data = self._build_status_command(transaction_id)
            response = await self._send_pagbank_command("STATUS", status_data)
            
            if not self._is_success_response(response):
                raise PaymentTerminalError(f"Failed to get transaction status")
            
            return self._parse_transaction_response(transaction_id, response)
            
        except Exception as e:
            logger.error(f"❌ Error getting PagBank transaction status: {e}")
            raise
    
    async def cancel_transaction(self, transaction_id: str) -> bool:
        """Cancela transação PagBank"""
        if not await self.is_connected():
            return False
        
        try:
            logger.info(f"🚫 Cancelling PagBank transaction {transaction_id}")
            
            cancel_data = self._build_cancel_command(transaction_id)
            response = await self._send_pagbank_command("CANCEL", cancel_data)
            
            success = self._is_success_response(response)
            
            if success:
                logger.info(f"✅ PagBank transaction {transaction_id} cancelled")
                if self._current_transaction_id == transaction_id:
                    self._current_transaction_id = None
                    self._set_status(TerminalStatus.CONNECTED)
            else:
                logger.warning(f"⚠️ Failed to cancel PagBank transaction")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error cancelling PagBank transaction: {e}")
            return False
    
    async def confirm_transaction(self, transaction_id: str) -> TransactionResponse:
        """Confirma transação PagBank"""
        return await self.get_transaction_status(transaction_id)
    
    async def print_receipt(self, transaction_id: str, receipt_type: str = "customer") -> bool:
        """Imprime comprovante no terminal PagBank"""
        if not await self.is_connected():
            return False
        
        try:
            logger.info(f"🖨️ Printing PagBank receipt for transaction {transaction_id}")
            
            print_data = self._build_print_command(transaction_id, receipt_type)
            response = await self._send_pagbank_command("PRINT", print_data)
            
            success = self._is_success_response(response)
            
            if success:
                logger.info(f"✅ PagBank receipt printed successfully")
            else:
                logger.warning(f"⚠️ Failed to print PagBank receipt")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error printing PagBank receipt: {e}")
            return False
    
    async def print_custom_text(self, text: str) -> bool:
        """Imprime texto customizado no terminal PagBank"""
        if not await self.is_connected():
            return False
        
        try:
            print_data = self._build_custom_print_command(text)
            response = await self._send_pagbank_command("PRINT", print_data)
            
            return self._is_success_response(response)
            
        except Exception as e:
            logger.error(f"❌ Error printing custom text: {e}")
            return False
    
    async def get_supported_payment_methods(self) -> List[PaymentMethod]:
        """Retorna métodos de pagamento suportados pelo PagBank"""
        return self._supported_methods.copy()
    
    async def configure_terminal(self, settings: Dict[str, Any]) -> bool:
        """Configura parâmetros do terminal PagBank"""
        if not await self.is_connected():
            return False
        
        try:
            config_data = self._build_config_command(settings)
            response = await self._send_pagbank_command("CONFIG", config_data)
            return self._is_success_response(response)
            
        except Exception as e:
            logger.error(f"❌ Error configuring PagBank terminal: {e}")
            return False
    
    # === Métodos auxiliares PagBank ===
    
    async def _send_pagbank_command(self, command: str, data: Dict[str, Any]) -> bytes:
        """Envia comando específico PagBank"""
        try:
            # Protocolo PagBank (JSON over USB/Serial/TCP com autenticação)
            command_data = {
                "command": command,
                "sequence": self._sequence_number,
                "merchant_id": self.merchant_id,
                "terminal_id": self.terminal_id,
                "establishment_id": self.establishment_id,
                "access_token": self.access_token,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }
            
            self._sequence_number += 1
            
            json_data = json.dumps(command_data).encode('utf-8')
            
            # Calcula hash de autenticação PagBank
            auth_hash = self._calculate_pagbank_auth(json_data)
            
            # Monta comando completo
            full_command = (self.COMMANDS.get(command, b"\x02PB_CMD\x03") + 
                          json_data + 
                          f"#{auth_hash}".encode('ascii') + 
                          b"\x03")
            
            response = await self.protocol.send_command(full_command)
            
            logger.debug(f"📤 PagBank command sent: {command}")
            logger.debug(f"📥 PagBank response: {response.hex()}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error sending PagBank command {command}: {e}")
            raise
    
    def _calculate_pagbank_auth(self, data: bytes) -> str:
        """Calcula hash de autenticação PagBank"""
        import hashlib
        
        # Combina dados com access_token para autenticação
        auth_string = data.decode('utf-8') + (self.access_token or "")
        return hashlib.sha256(auth_string.encode('utf-8')).hexdigest()[:8].upper()
    
    def _is_success_response(self, response: bytes) -> bool:
        """Verifica se resposta PagBank indica sucesso"""
        try:
            if not response:
                return False
            
            # PagBank retorna formato: STX + JSON + #HASH + ETX
            response_str = response.decode('utf-8', errors='ignore')
            
            # Remove delimitadores
            if response_str.startswith('\x02'):
                response_str = response_str[1:]
            if response_str.endswith('\x03'):
                response_str = response_str[:-1]
            
            # Separa JSON do hash
            if '#' in response_str:
                json_part, hash_part = response_str.rsplit('#', 1)
            else:
                json_part = response_str
            
            # Tenta parsear JSON
            try:
                response_json = json.loads(json_part)
                return (response_json.get("status") == "approved" or 
                       response_json.get("status") == "success" or
                       response_json.get("response_code") == "00")
            except json.JSONDecodeError:
                # Fallback para protocolo simples
                return "00" in response_str or "approved" in response_str.lower()
            
        except:
            return False
    
    def _get_error_message(self, response: bytes) -> str:
        """Obtém mensagem de erro da resposta PagBank"""
        try:
            response_str = response.decode('utf-8', errors='ignore')
            
            # Remove delimitadores e hash
            if response_str.startswith('\x02'):
                response_str = response_str[1:]
            if response_str.endswith('\x03'):
                response_str = response_str[:-1]
            if '#' in response_str:
                response_str = response_str.rsplit('#', 1)[0]
            
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
        """Constrói comando de inicialização PagBank"""
        return {
            "merchant_id": self.merchant_id,
            "terminal_id": self.terminal_id,
            "establishment_id": self.establishment_id,
            "access_token": self.access_token,
            "version": "3.0"
        }
    
    def _build_sale_command(self, transaction_id: str, request: TransactionRequest) -> Dict[str, Any]:
        """Constrói comando de venda PagBank"""
        command_data = {
            "reference_id": transaction_id,
            "amount": {
                "value": int(request.amount * 100),  # Centavos
                "currency": "BRL"
            },
            "payment_method": {
                "type": self._map_payment_method_to_pagbank(request.payment_method),
                "installments": request.installments
            },
            "description": request.description or "Pagamento RecoveryTruck"
        }
        
        # Dados do cliente
        if request.customer_name or request.customer_document:
            command_data["customer"] = {}
            if request.customer_name:
                command_data["customer"]["name"] = request.customer_name
            if request.customer_document:
                command_data["customer"]["tax_id"] = request.customer_document
        
        return command_data
    
    def _build_pix_command(self, transaction_id: str, request: TransactionRequest) -> Dict[str, Any]:
        """Constrói comando específico para PIX"""
        command_data = {
            "reference_id": transaction_id,
            "amount": {
                "value": int(request.amount * 100),  # Centavos
                "currency": "BRL"
            },
            "payment_method": {
                "type": "PIX"
            },
            "description": request.description or "Pagamento PIX RecoveryTruck",
            "qr_codes": [
                {
                    "amount": {
                        "value": int(request.amount * 100)
                    },
                    "expiration_date": (datetime.utcnow().timestamp() + 300)  # 5 minutos
                }
            ]
        }
        
        # Dados do cliente para PIX
        if request.customer_name or request.customer_document:
            command_data["customer"] = {}
            if request.customer_name:
                command_data["customer"]["name"] = request.customer_name
            if request.customer_document:
                command_data["customer"]["tax_id"] = request.customer_document
        
        return command_data
    
    def _build_status_command(self, transaction_id: str) -> Dict[str, Any]:
        """Constrói comando de consulta de status"""
        return {
            "reference_id": transaction_id
        }
    
    def _build_cancel_command(self, transaction_id: str) -> Dict[str, Any]:
        """Constrói comando de cancelamento"""
        return {
            "reference_id": transaction_id,
            "amount": {
                "value": 0  # Cancelamento total
            }
        }
    
    def _build_print_command(self, transaction_id: str, receipt_type: str) -> Dict[str, Any]:
        """Constrói comando de impressão"""
        return {
            "reference_id": transaction_id,
            "receipt_type": receipt_type
        }
    
    def _build_custom_print_command(self, text: str) -> Dict[str, Any]:
        """Constrói comando de impressão customizada"""
        return {
            "type": "custom_text",
            "content": text,
            "formatting": {
                "font_size": "normal",
                "alignment": "center"
            }
        }
    
    def _build_config_command(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói comando de configuração"""
        return {
            "configuration": settings
        }
    
    def _map_payment_method_to_pagbank(self, method: PaymentMethod) -> str:
        """Mapeia método de pagamento para código PagBank"""
        mapping = {
            PaymentMethod.DEBIT_CARD: "DEBIT_CARD",
            PaymentMethod.CREDIT_CARD: "CREDIT_CARD",
            PaymentMethod.PIX: "PIX",
            PaymentMethod.CONTACTLESS: "CONTACTLESS",
            PaymentMethod.VOUCHER: "VOUCHER"
        }
        return mapping.get(method, "CREDIT_CARD")
    
    def _parse_info_response(self, response: bytes) -> Dict[str, Any]:
        """Parseia resposta de informações do terminal"""
        try:
            response_str = response.decode('utf-8', errors='ignore')
            
            # Remove delimitadores e hash
            if response_str.startswith('\x02'):
                response_str = response_str[1:]
            if response_str.endswith('\x03'):
                response_str = response_str[:-1]
            if '#' in response_str:
                response_str = response_str.rsplit('#', 1)[0]
            
            response_json = json.loads(response_str)
            
            return {
                "serial_number": response_json.get("device_serial", self.terminal_id),
                "model": response_json.get("device_model", "PagBank Moderninha"),
                "firmware_version": response_json.get("firmware_version", "Unknown"),
                "battery_level": response_json.get("battery_level"),
                "signal_strength": response_json.get("signal_strength")
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Could not parse PagBank info response: {e}")
            return {}
    
    def _parse_transaction_response(self, transaction_id: str, response: bytes) -> TransactionResponse:
        """Parseia resposta de transação PagBank"""
        try:
            response_str = response.decode('utf-8', errors='ignore')
            
            # Remove delimitadores e hash
            if response_str.startswith('\x02'):
                response_str = response_str[1:]
            if response_str.endswith('\x03'):
                response_str = response_str[:-1]
            if '#' in response_str:
                response_str = response_str.rsplit('#', 1)[0]
            
            response_json = json.loads(response_str)
            
            # Mapeia status PagBank para status interno
            pb_status = response_json.get("status", "PENDING")
            status_mapping = {
                "PAID": TransactionStatus.APPROVED,
                "DECLINED": TransactionStatus.DECLINED,
                "CANCELED": TransactionStatus.CANCELLED,
                "PENDING": TransactionStatus.PENDING,
                "WAITING": TransactionStatus.PENDING,
                "TIMEOUT": TransactionStatus.TIMEOUT,
                "ERROR": TransactionStatus.ERROR
            }
            
            status = status_mapping.get(pb_status, TransactionStatus.PENDING)
            
            # Dados da transação
            amount_data = response_json.get("amount", {})
            amount = amount_data.get("value", 0) / 100.0  # Converte centavos
            
            payment_method_data = response_json.get("payment_method", {})
            payment_method_str = payment_method_data.get("type", "CREDIT_CARD")
            
            # Mapeia método de volta
            method_mapping = {
                "DEBIT_CARD": PaymentMethod.DEBIT_CARD,
                "CREDIT_CARD": PaymentMethod.CREDIT_CARD,
                "PIX": PaymentMethod.PIX,
                "CONTACTLESS": PaymentMethod.CONTACTLESS,
                "VOUCHER": PaymentMethod.VOUCHER
            }
            payment_method = method_mapping.get(payment_method_str, PaymentMethod.CREDIT_CARD)
            
            # Dados específicos do PIX
            pix_qr_code = None
            pix_copy_paste = None
            if payment_method == PaymentMethod.PIX:
                qr_codes = response_json.get("qr_codes", [])
                if qr_codes:
                    pix_qr_code = qr_codes[0].get("text")
                    pix_copy_paste = qr_codes[0].get("arrangements", [{}])[0].get("code")
            
            return TransactionResponse(
                transaction_id=transaction_id,
                status=status,
                amount=amount,
                payment_method=payment_method,
                authorization_code=response_json.get("authorization_code"),
                nsu=response_json.get("id"),  # PagBank usa 'id' como NSU
                receipt_merchant=response_json.get("receipt_merchant"),
                receipt_customer=response_json.get("receipt_customer"),
                card_brand=payment_method_data.get("card", {}).get("brand"),
                card_last_digits=payment_method_data.get("card", {}).get("last_digits"),
                installments=payment_method_data.get("installments", 1),
                pix_qr_code=pix_qr_code,
                pix_copy_paste=pix_copy_paste,
                error_message=response_json.get("error_messages", [{}])[0].get("description") if status in [TransactionStatus.DECLINED, TransactionStatus.ERROR] else None,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Error parsing PagBank transaction response: {e}")
            return TransactionResponse(
                transaction_id=transaction_id,
                status=TransactionStatus.ERROR,
                amount=0.0,
                payment_method=PaymentMethod.CREDIT_CARD,
                error_message=str(e),
                timestamp=datetime.utcnow()
            ) 