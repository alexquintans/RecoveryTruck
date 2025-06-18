# 🏧 Stone Terminal - Integração Física Real com PIX

import asyncio
import json
import uuid
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from .base import (
    TerminalAdapter, TerminalStatus, PaymentMethod, TransactionStatus,
    TerminalInfo, TransactionRequest, TransactionResponse, PaymentTerminalError
)
from .protocols import SerialProtocol, TCPProtocol, BluetoothProtocol, ConnectionConfig

logger = logging.getLogger(__name__)

class StoneTerminalAdapter(TerminalAdapter):
    """Adaptador para terminais Stone com integração física e PIX"""
    
    # Comandos Stone (baseados na documentação oficial)
    COMMANDS = {
        "CONNECT": b"\x02CONNECT\x03",
        "STATUS": b"\x02STATUS\x03",
        "TRANSACTION": b"\x02TRANSACTION",
        "CANCEL": b"\x02CANCEL",
        "PRINT": b"\x02PRINT",
        "CONFIG": b"\x02CONFIG",
        # 🆕 Comandos PIX Stone
        "PIX_GENERATE": b"\x02PIX_GENERATE",
        "PIX_STATUS": b"\x02PIX_STATUS",
        "PIX_CANCEL": b"\x02PIX_CANCEL",
        "PIX_DISPLAY": b"\x02PIX_DISPLAY"
    }
    
    # Códigos de resposta Stone
    RESPONSE_CODES = {
        "00": "Aprovada",
        "01": "Transação negada",
        "02": "Cartão inválido",
        "03": "Senha incorreta",
        "04": "Cartão vencido",
        "05": "Saldo insuficiente",
        "06": "Transação cancelada",
        "07": "Erro de comunicação",
        "08": "Timeout",
        "09": "Terminal ocupado",
        "10": "Erro interno",
        # 🆕 Códigos PIX específicos Stone
        "20": "PIX gerado com sucesso",
        "21": "PIX aguardando pagamento",
        "22": "PIX pago",
        "23": "PIX expirado",
        "24": "PIX cancelado",
        "25": "Erro na geração do PIX"
    }
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Configurações específicas Stone
        self.stone_config = config.get("stone", {})
        self.merchant_id = self.stone_config.get("merchant_id")
        self.terminal_id = self.stone_config.get("terminal_id")
        
        # 🆕 Configurações PIX Stone
        self.pix_config = self.stone_config.get("pix", {})
        self.pix_key = self.pix_config.get("pix_key")  # Chave PIX do estabelecimento
        self.pix_merchant_name = self.pix_config.get("merchant_name", "Estabelecimento")
        self.pix_merchant_city = self.pix_config.get("merchant_city", "Cidade")
        self.pix_timeout = self.pix_config.get("timeout", 300)  # 5 minutos padrão
        
        # Configuração de conexão
        connection_type = config.get("connection_type", "serial")
        self.protocol = self._create_protocol(connection_type, config)
        
        # Estado interno
        self._current_transaction_id: Optional[str] = None
        self._pix_transactions: Dict[str, Dict[str, Any]] = {}  # 🆕 Cache PIX
        self._supported_methods = [
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.DEBIT_CARD,
            PaymentMethod.CONTACTLESS,
            PaymentMethod.VOUCHER,
            PaymentMethod.PIX  # 🆕 PIX suportado
        ]
        
        logger.info(f"🏧 Stone terminal initialized with PIX: {self.terminal_id}")
    
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
                baudrate=config.get("baudrate", 115200)
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
        """Conecta com terminal Stone"""
        try:
            self._set_status(TerminalStatus.CONNECTING)
            logger.info(f"🔌 Connecting to Stone terminal {self.terminal_id}...")
            
            # Estabelece conexão física
            if not await self.protocol.connect():
                logger.error("❌ Failed to establish physical connection")
                self._set_status(TerminalStatus.ERROR)
                return False
            
            # Envia comando de conexão Stone
            response = await self._send_stone_command("CONNECT", {
                "merchant_id": self.merchant_id,
                "terminal_id": self.terminal_id
            })
            
            if not self._is_success_response(response):
                logger.error(f"❌ Stone connection rejected: {response}")
                await self.protocol.disconnect()
                self._set_status(TerminalStatus.ERROR)
                return False
            
            # Obtém informações do terminal
            await self._fetch_terminal_info()
            
            self._set_status(TerminalStatus.CONNECTED)
            logger.info("✅ Stone terminal connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stone connection error: {e}")
            self._set_status(TerminalStatus.ERROR)
            return False
    
    async def disconnect(self) -> bool:
        """Desconecta do terminal Stone"""
        try:
            logger.info("🔌 Disconnecting from Stone terminal...")
            
            # Cancela transação em andamento se houver
            if self._current_transaction_id:
                await self.cancel_transaction(self._current_transaction_id)
            
            # Desconecta protocolo
            await self.protocol.disconnect()
            
            self._set_status(TerminalStatus.DISCONNECTED)
            logger.info("✅ Stone terminal disconnected")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stone disconnection error: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Verifica se está conectado"""
        return self.protocol.is_connected and self.status in [
            TerminalStatus.CONNECTED, TerminalStatus.BUSY
        ]
    
    async def get_terminal_info(self) -> TerminalInfo:
        """Obtém informações do terminal Stone"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        if self.terminal_info:
            return self.terminal_info
        
        await self._fetch_terminal_info()
        return self.terminal_info
    
    async def _fetch_terminal_info(self):
        """Busca informações do terminal"""
        try:
            response = await self._send_stone_command("STATUS", {})
            
            if self._is_success_response(response):
                data = self._parse_response(response)
                
                self.terminal_info = TerminalInfo(
                    serial_number=data.get("serial_number", self.terminal_id),
                    model=data.get("model", "Stone Terminal"),
                    firmware_version=data.get("firmware_version", "Unknown"),
                    battery_level=data.get("battery_level"),
                    signal_strength=data.get("signal_strength")
                )
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch terminal info: {e}")
            # Cria info básica se não conseguir obter
            self.terminal_info = TerminalInfo(
                serial_number=self.terminal_id or "STONE001",
                model="Stone Terminal",
                firmware_version="Unknown"
            )
    
    async def start_transaction(self, request: TransactionRequest) -> str:
        """Inicia transação no terminal Stone (incluindo PIX)"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        if self.status == TerminalStatus.BUSY:
            raise PaymentTerminalError("Terminal is busy", terminal_status=self.status)
        
        transaction_id = str(uuid.uuid4())
        self._current_transaction_id = transaction_id
        self._set_status(TerminalStatus.BUSY)
        
        try:
            logger.info(f"💳 Starting Stone transaction: {transaction_id}")
            logger.info(f"💰 Amount: R$ {request.amount:.2f}")
            logger.info(f"🔄 Method: {request.payment_method}")
            
            # 🆕 Tratamento específico para PIX
            if request.payment_method == PaymentMethod.PIX:
                return await self._start_pix_transaction(transaction_id, request)
            else:
                return await self._start_card_transaction(transaction_id, request)
                
        except Exception as e:
            logger.error(f"❌ Stone transaction error: {e}")
            self._current_transaction_id = None
            self._set_status(TerminalStatus.CONNECTED)
            raise PaymentTerminalError(f"Transaction failed: {e}")

    async def _start_pix_transaction(self, transaction_id: str, request: TransactionRequest) -> str:
        """🆕 Inicia transação PIX no terminal Stone"""
        try:
            logger.info(f"🔥 Starting PIX transaction: {transaction_id}")
            
            # Valida chave PIX
            if not self.pix_key:
                raise PaymentTerminalError("PIX key not configured")
            
            # Gera dados do PIX
            pix_data = self._generate_pix_data(transaction_id, request)
            
            # Envia comando PIX para terminal
            command_data = {
                "command": "PIX_GENERATE",
                "transaction_id": transaction_id,
                "merchant_id": self.merchant_id,
                "terminal_id": self.terminal_id,
                "pix_key": pix_data["pix_key"],
                "amount": request.amount,
                "description": pix_data["description"],
                "timeout": self.pix_timeout
            }
            
            response = await self._send_stone_command("PIX_GENERATE", command_data)
            
            if not self._is_success_response(response):
                error_msg = self._get_error_message(response)
                raise PaymentTerminalError(f"PIX generation failed: {error_msg}")
            
            # Processa resposta PIX
            pix_response = self._parse_response(response)
            
            # Armazena dados PIX
            self._pix_transactions[transaction_id] = {
                "request": request,
                "pix_data": pix_data,
                "qr_code": pix_response.get("qr_code"),
                "pix_copy_paste": pix_response.get("pix_copy_paste"),
                "expiration": datetime.utcnow() + timedelta(seconds=self.pix_timeout),
                "status": TransactionStatus.PENDING,
                "created_at": datetime.utcnow()
            }
            
            # Exibe QR Code no terminal
            await self._display_pix_qr(transaction_id, pix_response.get("qr_code"))
            
            logger.info(f"✅ PIX transaction started: {transaction_id}")
            logger.info(f"🔗 PIX Copy&Paste: {pix_response.get('pix_copy_paste', '')[:50]}...")
            
            return transaction_id
            
        except Exception as e:
            logger.error(f"❌ PIX transaction error: {e}")
            raise PaymentTerminalError(f"PIX transaction failed: {e}")

    async def _start_card_transaction(self, transaction_id: str, request: TransactionRequest) -> str:
        """Inicia transação com cartão (método original)"""
        command_data = {
            "command": "TRANSACTION",
            "transaction_id": transaction_id,
            "merchant_id": self.merchant_id,
            "terminal_id": self.terminal_id,
            "amount": request.amount,
            "payment_method": self._map_payment_method(request.payment_method),
            "installments": request.installments,
            "description": request.description
        }
        
        response = await self._send_stone_command("TRANSACTION", command_data)
        
        if not self._is_success_response(response):
            error_msg = self._get_error_message(response)
            raise PaymentTerminalError(f"Transaction rejected: {error_msg}")
        
        logger.info(f"✅ Card transaction started: {transaction_id}")
        return transaction_id

    async def get_transaction_status(self, transaction_id: str) -> TransactionResponse:
        """Obtém status da transação (incluindo PIX)"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        # 🆕 Verifica se é transação PIX
        if transaction_id in self._pix_transactions:
            return await self._get_pix_transaction_status(transaction_id)
        else:
            return await self._get_card_transaction_status(transaction_id)

    async def _get_pix_transaction_status(self, transaction_id: str) -> TransactionResponse:
        """🆕 Obtém status da transação PIX"""
        try:
            pix_data = self._pix_transactions.get(transaction_id)
            if not pix_data:
                raise PaymentTerminalError(f"PIX transaction not found: {transaction_id}")
            
            # Verifica expiração
            if datetime.utcnow() > pix_data["expiration"]:
                pix_data["status"] = TransactionStatus.TIMEOUT
                return TransactionResponse(
                    transaction_id=transaction_id,
                    status=TransactionStatus.TIMEOUT,
                    amount=pix_data["request"].amount,
                    payment_method=PaymentMethod.PIX,
                    error_message="PIX expired"
                )
            
            # Consulta status no terminal
            status_data = {
                "command": "PIX_STATUS",
                "transaction_id": transaction_id,
                "merchant_id": self.merchant_id,
                "terminal_id": self.terminal_id
            }
            
            response = await self._send_stone_command("PIX_STATUS", status_data)
            
            if self._is_success_response(response):
                status_response = self._parse_response(response)
                
                # Atualiza status local
                new_status = self._map_pix_status(status_response.get("status"))
                pix_data["status"] = new_status
                
                # Se foi pago, processa confirmação
                if new_status == TransactionStatus.APPROVED:
                    return self._create_pix_success_response(transaction_id, pix_data, status_response)
                elif new_status == TransactionStatus.DECLINED:
                    return self._create_pix_declined_response(transaction_id, pix_data, status_response)
            
            # Retorna status atual
            return TransactionResponse(
                transaction_id=transaction_id,
                status=pix_data["status"],
                amount=pix_data["request"].amount,
                payment_method=PaymentMethod.PIX
            )
            
        except Exception as e:
            logger.error(f"❌ PIX status error: {e}")
            raise PaymentTerminalError(f"Failed to get PIX status: {e}")

    async def _get_card_transaction_status(self, transaction_id: str) -> TransactionResponse:
        """Obtém status da transação com cartão (método original)"""
        try:
            status_data = {
                "command": "STATUS",
                "transaction_id": transaction_id,
                "merchant_id": self.merchant_id,
                "terminal_id": self.terminal_id
            }
            
            response = await self._send_stone_command("STATUS", status_data)
            
            if self._is_success_response(response):
                data = self._parse_response(response)
                return self._map_stone_response(transaction_id, data)
            else:
                error_msg = self._get_error_message(response)
                return TransactionResponse(
                    transaction_id=transaction_id,
                    status=TransactionStatus.ERROR,
                    amount=0.0,
                    payment_method=PaymentMethod.CREDIT_CARD,
                    error_message=error_msg
                )
                
        except Exception as e:
            logger.error(f"❌ Card status error: {e}")
            raise PaymentTerminalError(f"Failed to get transaction status: {e}")

    async def cancel_transaction(self, transaction_id: str) -> bool:
        """Cancela transação (incluindo PIX)"""
        try:
            logger.info(f"🚫 Cancelling transaction: {transaction_id}")
            
            # 🆕 Tratamento específico para PIX
            if transaction_id in self._pix_transactions:
                return await self._cancel_pix_transaction(transaction_id)
            else:
                return await self._cancel_card_transaction(transaction_id)
                
        except Exception as e:
            logger.error(f"❌ Cancel error: {e}")
            return False
        finally:
            if self._current_transaction_id == transaction_id:
                self._current_transaction_id = None
                self._set_status(TerminalStatus.CONNECTED)

    async def _cancel_pix_transaction(self, transaction_id: str) -> bool:
        """🆕 Cancela transação PIX"""
        try:
            pix_data = self._pix_transactions.get(transaction_id)
            if not pix_data:
                logger.warning(f"PIX transaction not found for cancellation: {transaction_id}")
                return True
            
            # Envia comando de cancelamento PIX
            cancel_data = {
                "command": "PIX_CANCEL",
                "transaction_id": transaction_id,
                "merchant_id": self.merchant_id,
                "terminal_id": self.terminal_id
            }
            
            response = await self._send_stone_command("PIX_CANCEL", cancel_data)
            
            # Atualiza status local
            pix_data["status"] = TransactionStatus.CANCELLED
            
            logger.info(f"✅ PIX transaction cancelled: {transaction_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ PIX cancel error: {e}")
            return False

    async def _cancel_card_transaction(self, transaction_id: str) -> bool:
        """Cancela transação com cartão (método original)"""
        try:
            cancel_data = {
                "command": "CANCEL",
                "transaction_id": transaction_id,
                "merchant_id": self.merchant_id,
                "terminal_id": self.terminal_id
            }
            
            response = await self._send_stone_command("CANCEL", cancel_data)
            
            success = self._is_success_response(response)
            if success:
                logger.info(f"✅ Card transaction cancelled: {transaction_id}")
            else:
                logger.error(f"❌ Card cancellation failed: {self._get_error_message(response)}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Card cancel error: {e}")
            return False

    # 🆕 Métodos PIX específicos

    def _generate_pix_data(self, transaction_id: str, request: TransactionRequest) -> Dict[str, Any]:
        """Gera dados PIX para transação"""
        return {
            "merchant_name": self.pix_merchant_name,
            "merchant_city": self.pix_merchant_city,
            "pix_key": self.pix_key,
            "amount": request.amount,
            "description": request.description or f"Pagamento {transaction_id[:8]}",
            "transaction_id": transaction_id,
            "expiration": self.pix_timeout
        }

    def _map_pix_status(self, status_code: str) -> TransactionStatus:
        """Mapeia status PIX do Stone para TransactionStatus"""
        status_map = {
            "20": TransactionStatus.PENDING,      # PIX gerado
            "21": TransactionStatus.PENDING,      # Aguardando pagamento
            "22": TransactionStatus.APPROVED,     # PIX pago
            "23": TransactionStatus.TIMEOUT,      # PIX expirado
            "24": TransactionStatus.CANCELLED,    # PIX cancelado
            "25": TransactionStatus.ERROR,        # Erro na geração
        }
        
        return status_map.get(status_code, TransactionStatus.ERROR)

    def _create_pix_success_response(self, transaction_id: str, pix_data: Dict[str, Any], status_response: Dict[str, Any]) -> TransactionResponse:
        """Cria resposta de sucesso PIX"""
        return TransactionResponse(
            transaction_id=transaction_id,
            status=TransactionStatus.APPROVED,
            amount=pix_data["request"].amount,
            payment_method=PaymentMethod.PIX,
            authorization_code=status_response.get("payment_id"),
            nsu=transaction_id[:10],
            receipt_customer=self._generate_pix_receipt(transaction_id, pix_data, "customer"),
            receipt_merchant=self._generate_pix_receipt(transaction_id, pix_data, "merchant")
        )

    def _create_pix_declined_response(self, transaction_id: str, pix_data: Dict[str, Any], status_response: Dict[str, Any]) -> TransactionResponse:
        """Cria resposta de PIX negado"""
        return TransactionResponse(
            transaction_id=transaction_id,
            status=TransactionStatus.DECLINED,
            amount=pix_data["request"].amount,
            payment_method=PaymentMethod.PIX,
            error_message="PIX payment declined"
        )

    def _generate_pix_receipt(self, transaction_id: str, pix_data: Dict[str, Any], receipt_type: str) -> str:
        """Gera comprovante PIX"""
        lines = [
            "=" * 40,
            "COMPROVANTE PIX - STONE",
            "=" * 40,
            f"Estabelecimento: {self.pix_merchant_name}",
            f"Cidade: {self.pix_merchant_city}",
            f"Chave PIX: {self.pix_key}",
            "-" * 40,
            f"Valor: R$ {pix_data['request'].amount:.2f}",
            f"Descrição: {pix_data['pix_data']['description']}",
            f"ID Transação: {transaction_id}",
            f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "-" * 40,
            "PIX REALIZADO COM SUCESSO",
            "=" * 40
        ]
        
        return "\n".join(lines)

    async def _display_pix_qr(self, transaction_id: str, qr_data: str):
        """Exibe QR Code PIX no terminal"""
        try:
            if not qr_data:
                logger.warning("No QR data to display")
                return
            
            # Comando para exibir QR no terminal Stone
            display_data = {
                "command": "PIX_DISPLAY",
                "transaction_id": transaction_id,
                "qr_code": qr_data,
                "timeout": self.pix_timeout
            }
            
            await self._send_stone_command("PIX_DISPLAY", display_data)
            
            logger.info(f"📱 PIX QR Code displayed on terminal: {transaction_id}")
            
        except Exception as e:
            logger.error(f"❌ Display QR error: {e}")

    async def print_pix_receipt(self, transaction_id: str, receipt_type: str = "customer") -> bool:
        """🆕 Imprime comprovante PIX"""
        try:
            pix_data = self._pix_transactions.get(transaction_id)
            if not pix_data:
                logger.error(f"PIX transaction not found: {transaction_id}")
                return False
            
            receipt_text = self._generate_pix_receipt(transaction_id, pix_data, receipt_type)
            
            # Envia comando de impressão PIX
            print_data = {
                "command": "PRINT",
                "transaction_id": transaction_id,
                "receipt_type": receipt_type,
                "content": receipt_text,
                "pix_mode": True
            }
            
            response = await self._send_stone_command("PRINT", print_data)
            
            success = self._is_success_response(response)
            if success:
                logger.info(f"🖨️ PIX receipt printed: {transaction_id} ({receipt_type})")
            else:
                logger.error(f"❌ PIX print failed: {self._get_error_message(response)}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ PIX print error: {e}")
            return False

    # Atualiza método de impressão original para suportar PIX
    async def print_receipt(self, transaction_id: str, receipt_type: str = "customer") -> bool:
        """Imprime comprovante (cartão ou PIX)"""
        # 🆕 Verifica se é PIX
        if transaction_id in self._pix_transactions:
            return await self.print_pix_receipt(transaction_id, receipt_type)
        else:
            # Método original para cartões
            try:
                if not await self.is_connected():
                    raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
                
                logger.info(f"🖨️ Printing receipt: {transaction_id} ({receipt_type})")
                
                print_data = {
                    "command": "PRINT",
                    "transaction_id": transaction_id,
                    "receipt_type": receipt_type
                }
                
                response = await self._send_stone_command("PRINT", print_data)
                
                success = self._is_success_response(response)
                if success:
                    logger.info(f"✅ Receipt printed successfully")
                else:
                    logger.error(f"❌ Print failed: {self._get_error_message(response)}")
                
                return success
                
            except Exception as e:
                logger.error(f"❌ Print error: {e}")
                return False
    
    # === Métodos auxiliares Stone ===
    
    async def _send_stone_command(self, command: str, data: Dict[str, Any]) -> bytes:
        """Envia comando específico Stone"""
        try:
            # Monta comando Stone
            command_data = {
                "command": command,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Serializa para JSON
            json_data = json.dumps(command_data).encode('utf-8')
            
            # Adiciona delimitadores Stone
            stone_command = self.COMMANDS.get(command, b"\x02") + json_data + b"\x03"
            
            # Envia via protocolo
            response = await self.protocol.send_command(stone_command)
            
            logger.debug(f"📤 Stone command sent: {command}")
            logger.debug(f"📥 Stone response: {response.hex()}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error sending Stone command {command}: {e}")
            raise
    
    def _is_success_response(self, response: bytes) -> bool:
        """Verifica se resposta Stone indica sucesso"""
        if not response:
            return False
        
        try:
            # Remove delimitadores
            if response.startswith(b'\x02') and response.endswith(b'\x03'):
                response = response[1:-1]
            
            # Tenta parsear JSON
            data = json.loads(response.decode('utf-8'))
            return data.get("status") == "success" or data.get("code") == "00"
            
        except:
            # Fallback: verifica códigos de resposta simples
            return b"00" in response or b"SUCCESS" in response
    
    def _parse_response(self, response: bytes) -> Dict[str, Any]:
        """Parseia resposta Stone"""
        try:
            # Remove delimitadores
            if response.startswith(b'\x02') and response.endswith(b'\x03'):
                response = response[1:-1]
            
            return json.loads(response.decode('utf-8'))
            
        except Exception as e:
            logger.warning(f"⚠️ Could not parse Stone response: {e}")
            return {"raw_response": response.hex()}
    
    def _get_error_message(self, response: bytes) -> str:
        """Obtém mensagem de erro da resposta Stone"""
        try:
            data = self._parse_response(response)
            
            error_code = data.get("code", "99")
            error_message = data.get("message")
            
            if error_message:
                return error_message
            
            return self.RESPONSE_CODES.get(error_code, f"Erro desconhecido: {error_code}")
            
        except:
            return "Erro de comunicação"
    
    def _map_payment_method(self, method: PaymentMethod) -> str:
        """Mapeia método de pagamento para formato Stone"""
        mapping = {
            PaymentMethod.CREDIT_CARD: "CREDIT",
            PaymentMethod.DEBIT_CARD: "DEBIT", 
            PaymentMethod.CONTACTLESS: "CONTACTLESS",
            PaymentMethod.VOUCHER: "VOUCHER",
            PaymentMethod.PIX: "PIX"
        }
        return mapping.get(method, "CREDIT")
    
    def _map_stone_response(self, transaction_id: str, data: Dict[str, Any]) -> TransactionResponse:
        """Mapeia resposta Stone para TransactionResponse"""
        
        # Mapeia status Stone para nosso enum
        stone_status = data.get("status", "unknown")
        status_mapping = {
            "approved": TransactionStatus.APPROVED,
            "declined": TransactionStatus.DECLINED,
            "cancelled": TransactionStatus.CANCELLED,
            "processing": TransactionStatus.PROCESSING,
            "pending": TransactionStatus.PENDING,
            "timeout": TransactionStatus.TIMEOUT,
            "error": TransactionStatus.ERROR
        }
        
        status = status_mapping.get(stone_status, TransactionStatus.ERROR)
        
        # Mapeia método de pagamento de volta
        stone_method = data.get("payment_method", "CREDIT")
        method_mapping = {
            "CREDIT": PaymentMethod.CREDIT_CARD,
            "DEBIT": PaymentMethod.DEBIT_CARD,
            "CONTACTLESS": PaymentMethod.CONTACTLESS,
            "VOUCHER": PaymentMethod.VOUCHER,
            "PIX": PaymentMethod.PIX
        }
        
        payment_method = method_mapping.get(stone_method, PaymentMethod.CREDIT_CARD)
        
        return TransactionResponse(
            transaction_id=transaction_id,
            status=status,
            amount=data.get("amount", 0) / 100.0,  # Stone retorna centavos
            payment_method=payment_method,
            authorization_code=data.get("authorization_code"),
            nsu=data.get("nsu"),
            receipt_merchant=data.get("receipt_merchant"),
            receipt_customer=data.get("receipt_customer"),
            card_brand=data.get("card_brand"),
            card_last_digits=data.get("card_last_digits"),
            installments=data.get("installments", 1),
            error_message=data.get("error_message"),
            timestamp=datetime.utcnow()
        ) 