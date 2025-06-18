# 🧪 Terminal Mock - Simulação Completa para Testes

import asyncio
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from .base import (
    TerminalAdapter, TerminalStatus, PaymentMethod, TransactionStatus,
    TerminalInfo, TransactionRequest, TransactionResponse, PaymentTerminalError
)

logger = logging.getLogger(__name__)

class MockTerminalAdapter(TerminalAdapter):
    """Terminal mock para testes e desenvolvimento"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Configurações do mock
        self.simulate_delays = config.get("simulate_delays", True)
        self.failure_rate = config.get("failure_rate", 0.1)  # 10% de falha por padrão
        self.connection_delay = config.get("connection_delay", 2.0)
        self.transaction_delay = config.get("transaction_delay", 5.0)
        
        # Estado interno
        self._transactions: Dict[str, TransactionResponse] = {}
        self._terminal_info = TerminalInfo(
            serial_number=config.get("serial_number", "MOCK001"),
            model=config.get("model", "MockTerminal v1.0"),
            firmware_version=config.get("firmware_version", "1.0.0"),
            battery_level=random.randint(70, 100),
            signal_strength=random.randint(80, 100)
        )
        
        # Métodos de pagamento suportados
        self._supported_methods = [
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.DEBIT_CARD,
            PaymentMethod.PIX,
            PaymentMethod.CONTACTLESS,
            PaymentMethod.VOUCHER
        ]
        
        logger.info(f"🧪 MockTerminal initialized: {self._terminal_info.model}")
    
    async def connect(self) -> bool:
        """Simula conexão com terminal"""
        try:
            self._set_status(TerminalStatus.CONNECTING)
            logger.info("🔌 Mock terminal connecting...")
            
            if self.simulate_delays:
                await asyncio.sleep(self.connection_delay)
            
            # Simula falha de conexão ocasional
            if random.random() < 0.05:  # 5% de chance de falha
                logger.error("❌ Mock connection failed (simulated)")
                self._set_status(TerminalStatus.ERROR)
                return False
            
            self._set_status(TerminalStatus.CONNECTED)
            self.terminal_info = self._terminal_info
            logger.info("✅ Mock terminal connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Mock connection error: {e}")
            self._set_status(TerminalStatus.ERROR)
            return False
    
    async def disconnect(self) -> bool:
        """Simula desconexão"""
        try:
            logger.info("🔌 Mock terminal disconnecting...")
            
            if self.simulate_delays:
                await asyncio.sleep(0.5)
            
            self._set_status(TerminalStatus.DISCONNECTED)
            logger.info("✅ Mock terminal disconnected")
            return True
            
        except Exception as e:
            logger.error(f"❌ Mock disconnection error: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """Verifica se está conectado"""
        return self.status in [TerminalStatus.CONNECTED, TerminalStatus.BUSY]
    
    async def get_terminal_info(self) -> TerminalInfo:
        """Retorna informações do terminal mock"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        # Atualiza informações dinâmicas
        self._terminal_info.battery_level = max(20, self._terminal_info.battery_level - random.randint(0, 2))
        self._terminal_info.signal_strength = random.randint(75, 100)
        self._terminal_info.last_transaction = datetime.utcnow() if self._transactions else None
        
        return self._terminal_info
    
    async def start_transaction(self, request: TransactionRequest) -> str:
        """Inicia transação simulada"""
        if not await self.is_connected():
            raise PaymentTerminalError("Terminal not connected", terminal_status=self.status)
        
        if self.status == TerminalStatus.BUSY:
            raise PaymentTerminalError("Terminal busy with another transaction", terminal_status=self.status)
        
        # Gera ID da transação
        transaction_id = str(uuid.uuid4())
        
        logger.info(f"💳 Starting mock transaction {transaction_id}: R$ {request.amount:.2f} via {request.payment_method.value}")
        
        # Muda status para ocupado
        self._set_status(TerminalStatus.BUSY)
        
        # Cria resposta inicial
        response = TransactionResponse(
            transaction_id=transaction_id,
            status=TransactionStatus.PENDING,
            amount=request.amount,
            payment_method=request.payment_method,
            installments=request.installments
        )
        
        self._transactions[transaction_id] = response
        self.current_transaction = response
        
        # Simula processamento assíncrono
        asyncio.create_task(self._simulate_transaction_processing(transaction_id, request))
        
        return transaction_id
    
    async def _simulate_transaction_processing(self, transaction_id: str, request: TransactionRequest):
        """Simula o processamento da transação"""
        try:
            transaction = self._transactions[transaction_id]
            
            # Simula tempo de processamento
            if self.simulate_delays:
                await asyncio.sleep(self.transaction_delay)
            
            # Simula diferentes cenários
            scenario = self._determine_transaction_scenario(request)
            
            if scenario == "approved":
                transaction.status = TransactionStatus.APPROVED
                transaction.authorization_code = f"AUTH{random.randint(100000, 999999)}"
                transaction.nsu = f"{random.randint(1000000, 9999999)}"
                
                # Simula dados do cartão (se aplicável)
                if request.payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
                    transaction.card_brand = random.choice(["VISA", "MASTERCARD", "ELO"])
                    transaction.card_last_digits = f"{random.randint(1000, 9999)}"
                
                # Gera comprovantes
                transaction.receipt_customer = self._generate_receipt(transaction, "customer")
                transaction.receipt_merchant = self._generate_receipt(transaction, "merchant")
                
                logger.info(f"✅ Mock transaction {transaction_id} APPROVED")
                
            elif scenario == "declined":
                transaction.status = TransactionStatus.DECLINED
                transaction.error_message = random.choice([
                    "Cartão sem saldo",
                    "Transação negada pelo banco",
                    "Cartão bloqueado",
                    "Senha incorreta"
                ])
                logger.warning(f"❌ Mock transaction {transaction_id} DECLINED: {transaction.error_message}")
                
            elif scenario == "timeout":
                transaction.status = TransactionStatus.TIMEOUT
                transaction.error_message = "Timeout na transação"
                logger.warning(f"⏰ Mock transaction {transaction_id} TIMEOUT")
                
            else:  # error
                transaction.status = TransactionStatus.ERROR
                transaction.error_message = "Erro de comunicação"
                logger.error(f"💥 Mock transaction {transaction_id} ERROR")
            
            # Atualiza timestamp
            transaction.timestamp = datetime.utcnow()
            
            # Libera terminal
            self._set_status(TerminalStatus.CONNECTED)
            self.current_transaction = None
            
        except Exception as e:
            logger.error(f"❌ Error in mock transaction processing: {e}")
            transaction = self._transactions.get(transaction_id)
            if transaction:
                transaction.status = TransactionStatus.ERROR
                transaction.error_message = str(e)
            self._set_status(TerminalStatus.ERROR)
    
    def _determine_transaction_scenario(self, request: TransactionRequest) -> str:
        """Determina o cenário da transação baseado em regras"""
        
        # Regras específicas para testes
        if request.amount == 1.00:
            return "declined"  # R$ 1,00 sempre nega
        elif request.amount == 2.00:
            return "timeout"   # R$ 2,00 sempre timeout
        elif request.amount == 3.00:
            return "error"     # R$ 3,00 sempre erro
        elif request.customer_name and "test" in request.customer_name.lower():
            return "approved"  # Nomes com "test" sempre aprovam
        
        # Cenário aleatório baseado na taxa de falha
        if random.random() < self.failure_rate:
            return random.choice(["declined", "timeout", "error"])
        else:
            return "approved"
    
    def _generate_receipt(self, transaction: TransactionResponse, receipt_type: str) -> str:
        """Gera comprovante simulado"""
        lines = [
            "RECOVERY TRUCK",
            "CNPJ: 12.345.678/0001-90",
            "=" * 30,
            f"COMPROVANTE - {receipt_type.upper()}",
            "=" * 30,
            f"Data: {transaction.timestamp.strftime('%d/%m/%Y %H:%M:%S')}",
            f"NSU: {transaction.nsu}",
            f"Autorização: {transaction.authorization_code}",
            f"Valor: R$ {transaction.amount:.2f}",
            f"Método: {transaction.payment_method.value.upper()}",
        ]
        
        if transaction.card_brand:
            lines.append(f"Cartão: {transaction.card_brand} ****{transaction.card_last_digits}")
        
        if transaction.installments > 1:
            lines.append(f"Parcelas: {transaction.installments}x")
        
        lines.extend([
            "=" * 30,
            "TRANSAÇÃO APROVADA",
            "Obrigado pela preferência!",
            "=" * 30
        ])
        
        return "\n".join(lines)
    
    async def get_transaction_status(self, transaction_id: str) -> TransactionResponse:
        """Obtém status da transação"""
        if transaction_id not in self._transactions:
            raise PaymentTerminalError(f"Transaction {transaction_id} not found")
        
        return self._transactions[transaction_id]
    
    async def cancel_transaction(self, transaction_id: str) -> bool:
        """Cancela transação"""
        if transaction_id not in self._transactions:
            return False
        
        transaction = self._transactions[transaction_id]
        
        if transaction.status in [TransactionStatus.PENDING, TransactionStatus.PROCESSING]:
            transaction.status = TransactionStatus.CANCELLED
            transaction.error_message = "Transação cancelada pelo usuário"
            
            # Libera terminal se estava ocupado
            if self.status == TerminalStatus.BUSY:
                self._set_status(TerminalStatus.CONNECTED)
                self.current_transaction = None
            
            logger.info(f"🚫 Mock transaction {transaction_id} cancelled")
            return True
        
        return False
    
    async def confirm_transaction(self, transaction_id: str) -> TransactionResponse:
        """Confirma transação (para fluxos que requerem confirmação)"""
        if transaction_id not in self._transactions:
            raise PaymentTerminalError(f"Transaction {transaction_id} not found")
        
        transaction = self._transactions[transaction_id]
        
        if transaction.status == TransactionStatus.APPROVED:
            logger.info(f"✅ Mock transaction {transaction_id} confirmed")
            return transaction
        else:
            raise PaymentTerminalError(f"Cannot confirm transaction with status: {transaction.status}")
    
    async def print_receipt(self, transaction_id: str, receipt_type: str = "customer") -> bool:
        """Simula impressão de comprovante"""
        if transaction_id not in self._transactions:
            return False
        
        transaction = self._transactions[transaction_id]
        
        if transaction.status != TransactionStatus.APPROVED:
            logger.warning(f"⚠️ Cannot print receipt for non-approved transaction: {transaction.status}")
            return False
        
        # Simula tempo de impressão
        if self.simulate_delays:
            await asyncio.sleep(2.0)
        
        receipt_content = (transaction.receipt_customer if receipt_type == "customer" 
                          else transaction.receipt_merchant)
        
        logger.info(f"🖨️ Mock receipt printed for transaction {transaction_id}")
        logger.debug(f"Receipt content:\n{receipt_content}")
        
        return True
    
    async def print_custom_text(self, text: str) -> bool:
        """Simula impressão de texto customizado"""
        if not await self.is_connected():
            return False
        
        # Simula tempo de impressão
        if self.simulate_delays:
            await asyncio.sleep(1.0)
        
        logger.info(f"🖨️ Mock custom text printed: {text[:50]}...")
        return True
    
    async def get_supported_payment_methods(self) -> List[PaymentMethod]:
        """Retorna métodos de pagamento suportados"""
        return self._supported_methods.copy()
    
    async def configure_terminal(self, settings: Dict[str, Any]) -> bool:
        """Configura parâmetros do terminal mock"""
        if not await self.is_connected():
            return False
        
        # Atualiza configurações mock
        if "failure_rate" in settings:
            self.failure_rate = max(0.0, min(1.0, settings["failure_rate"]))
        
        if "transaction_delay" in settings:
            self.transaction_delay = max(0.1, settings["transaction_delay"])
        
        if "simulate_delays" in settings:
            self.simulate_delays = bool(settings["simulate_delays"])
        
        logger.info(f"⚙️ Mock terminal configured: {settings}")
        return True
    
    # Métodos específicos para testes
    
    def set_next_transaction_result(self, result: TransactionStatus, error_message: Optional[str] = None):
        """Define o resultado da próxima transação (para testes determinísticos)"""
        self._next_result = result
        self._next_error = error_message
        logger.info(f"🎯 Next transaction will result in: {result}")
    
    def get_transaction_history(self) -> List[TransactionResponse]:
        """Retorna histórico de transações"""
        return list(self._transactions.values())
    
    def clear_transaction_history(self):
        """Limpa histórico de transações"""
        self._transactions.clear()
        logger.info("🗑️ Transaction history cleared")
    
    def simulate_connection_loss(self):
        """Simula perda de conexão"""
        self._set_status(TerminalStatus.ERROR)
        logger.warning("📡 Simulated connection loss")
    
    def simulate_maintenance_mode(self):
        """Simula modo de manutenção"""
        self._set_status(TerminalStatus.MAINTENANCE)
        logger.info("🔧 Simulated maintenance mode") 