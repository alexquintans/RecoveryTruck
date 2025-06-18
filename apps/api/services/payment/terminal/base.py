# 🏧 Interface Base para Terminais Físicos

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Optional, Any, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

class TerminalStatus(str, Enum):
    """Status do terminal físico"""
    DISCONNECTED = "disconnected"      # Desconectado
    CONNECTING = "connecting"          # Conectando
    CONNECTED = "connected"            # Conectado e pronto
    BUSY = "busy"                      # Processando transação
    ERROR = "error"                    # Erro de comunicação
    MAINTENANCE = "maintenance"        # Em manutenção

class PaymentMethod(str, Enum):
    """Métodos de pagamento suportados"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PIX = "pix"
    CONTACTLESS = "contactless"        # Aproximação/NFC
    VOUCHER = "voucher"                # Vale alimentação/refeição
    BOLETO = "boleto"

class TransactionStatus(str, Enum):
    """Status da transação no terminal"""
    PENDING = "pending"                # Aguardando ação do cliente
    PROCESSING = "processing"          # Processando
    APPROVED = "approved"              # Aprovada
    DECLINED = "declined"              # Negada
    CANCELLED = "cancelled"            # Cancelada
    ERROR = "error"                    # Erro na transação
    TIMEOUT = "timeout"                # Timeout

@dataclass
class TerminalInfo:
    """Informações do terminal"""
    serial_number: str
    model: str
    firmware_version: str
    battery_level: Optional[int] = None
    signal_strength: Optional[int] = None
    last_transaction: Optional[datetime] = None

@dataclass
class CreditCardConfig:
    """Configuração específica para cartão de crédito"""
    max_installments: int = 12
    min_amount_for_installments: float = 50.0
    brands_accepted: List[str] = field(default_factory=lambda: ["visa", "mastercard", "elo", "amex"])
    allow_contactless: bool = True
    require_signature_above: float = 50.0
    
@dataclass
class DebitCardConfig:
    """Configuração específica para cartão de débito"""
    require_password: bool = True
    max_amount: float = 5000.0
    allow_contactless: bool = True
    contactless_limit: float = 200.0

@dataclass
class PIXConfig:
    """Configuração específica para PIX"""
    require_cpf_validation: bool = True
    expiration_minutes: int = 30
    allow_change: bool = False
    min_amount: float = 0.01
    max_amount: float = 50000.0
    auto_confirm: bool = True
    qr_code_format: str = "base64"

@dataclass
class ContactlessConfig:
    """Configuração específica para pagamento por aproximação"""
    max_amount: float = 200.0
    require_pin_above: float = 50.0
    supported_technologies: List[str] = field(default_factory=lambda: ["nfc", "rfid"])

@dataclass
class VoucherConfig:
    """Configuração específica para vouchers"""
    types_accepted: List[str] = field(default_factory=lambda: ["meal", "food", "fuel"])
    require_cpf: bool = True
    max_amount: float = 1000.0
    validate_balance: bool = True

@dataclass
class BoletoConfig:
    """Configuração específica para boleto"""
    days_to_expire: int = 3
    fine_percentage: float = 2.0
    interest_per_day: float = 0.033
    min_amount: float = 5.0
    max_amount: float = 10000.0
    allow_discount: bool = True

@dataclass
class PaymentMethodConfigs:
    """Configurações consolidadas para todas as modalidades"""
    credit_card: CreditCardConfig = field(default_factory=CreditCardConfig)
    debit_card: DebitCardConfig = field(default_factory=DebitCardConfig)
    pix: PIXConfig = field(default_factory=PIXConfig)
    contactless: ContactlessConfig = field(default_factory=ContactlessConfig)
    voucher: VoucherConfig = field(default_factory=VoucherConfig)
    boleto: BoletoConfig = field(default_factory=BoletoConfig)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PaymentMethodConfigs':
        """Cria configurações a partir de dicionário"""
        return cls(
            credit_card=CreditCardConfig(**config_dict.get("credit_card", {})),
            debit_card=DebitCardConfig(**config_dict.get("debit_card", {})),
            pix=PIXConfig(**config_dict.get("pix", {})),
            contactless=ContactlessConfig(**config_dict.get("contactless", {})),
            voucher=VoucherConfig(**config_dict.get("voucher", {})),
            boleto=BoletoConfig(**config_dict.get("boleto", {}))
        )

@dataclass
class TransactionRequest:
    """Solicitação de transação"""
    amount: float
    payment_method: PaymentMethod
    installments: int = 1
    description: Optional[str] = None
    customer_name: Optional[str] = None
    customer_document: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # 🆕 Campos específicos por modalidade
    # PIX
    pix_key: Optional[str] = None
    pix_expiration_minutes: Optional[int] = None
    
    # Cartão
    card_brand: Optional[str] = None
    require_signature: bool = False
    
    # Voucher
    voucher_type: Optional[str] = None
    
    # Boleto
    boleto_due_date: Optional[datetime] = None
    boleto_fine_percentage: Optional[float] = None
    
    def validate_with_config(self, config: PaymentMethodConfigs) -> List[str]:
        """Valida requisição com base nas configurações específicas"""
        errors = []
        
        if self.payment_method == PaymentMethod.CREDIT_CARD:
            cc_config = config.credit_card
            if self.installments > cc_config.max_installments:
                errors.append(f"Máximo {cc_config.max_installments} parcelas permitidas")
            if self.amount < cc_config.min_amount_for_installments and self.installments > 1:
                errors.append(f"Valor mínimo R$ {cc_config.min_amount_for_installments:.2f} para parcelamento")
            if self.card_brand and self.card_brand.lower() not in cc_config.brands_accepted:
                errors.append(f"Bandeira {self.card_brand} não aceita")
                
        elif self.payment_method == PaymentMethod.DEBIT_CARD:
            db_config = config.debit_card
            if self.amount > db_config.max_amount:
                errors.append(f"Valor máximo R$ {db_config.max_amount:.2f} para débito")
                
        elif self.payment_method == PaymentMethod.PIX:
            pix_config = config.pix
            if pix_config.require_cpf_validation and not self.customer_document:
                errors.append("CPF obrigatório para transações PIX")
            if self.amount < pix_config.min_amount:
                errors.append(f"Valor mínimo R$ {pix_config.min_amount:.2f} para PIX")
            if self.amount > pix_config.max_amount:
                errors.append(f"Valor máximo R$ {pix_config.max_amount:.2f} para PIX")
                
        elif self.payment_method == PaymentMethod.CONTACTLESS:
            cl_config = config.contactless
            if self.amount > cl_config.max_amount:
                errors.append(f"Valor máximo R$ {cl_config.max_amount:.2f} para aproximação")
                
        elif self.payment_method == PaymentMethod.VOUCHER:
            vc_config = config.voucher
            if self.amount > vc_config.max_amount:
                errors.append(f"Valor máximo R$ {vc_config.max_amount:.2f} para voucher")
            if vc_config.require_cpf and not self.customer_document:
                errors.append("CPF obrigatório para vouchers")
            if self.voucher_type and self.voucher_type not in vc_config.types_accepted:
                errors.append(f"Tipo de voucher {self.voucher_type} não aceito")
                
        elif self.payment_method == PaymentMethod.BOLETO:
            bl_config = config.boleto
            if self.amount < bl_config.min_amount:
                errors.append(f"Valor mínimo R$ {bl_config.min_amount:.2f} para boleto")
            if self.amount > bl_config.max_amount:
                errors.append(f"Valor máximo R$ {bl_config.max_amount:.2f} para boleto")
        
        return errors

@dataclass
class TransactionResponse:
    """Resposta da transação"""
    transaction_id: str
    status: TransactionStatus
    amount: float
    payment_method: PaymentMethod
    authorization_code: Optional[str] = None
    nsu: Optional[str] = None           # Número Sequencial Único
    receipt_merchant: Optional[str] = None
    receipt_customer: Optional[str] = None
    card_brand: Optional[str] = None
    card_last_digits: Optional[str] = None
    installments: int = 1
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    # 🆕 Campos específicos por modalidade
    # PIX
    qr_code: Optional[str] = None
    pix_copy_paste: Optional[str] = None
    pix_expiration: Optional[datetime] = None
    
    # Boleto
    boleto_url: Optional[str] = None
    boleto_barcode: Optional[str] = None
    boleto_due_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class PaymentTerminalError(Exception):
    """Exceção específica para erros de terminal"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, terminal_status: Optional[TerminalStatus] = None):
        super().__init__(message)
        self.error_code = error_code
        self.terminal_status = terminal_status

class TerminalAdapter(ABC):
    """Interface base para adaptadores de terminal físico"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.status = TerminalStatus.DISCONNECTED
        self.terminal_info: Optional[TerminalInfo] = None
        self.current_transaction: Optional[TransactionResponse] = None
        self._connection = None
        self._status_callbacks: List[callable] = []
        
        # 🆕 Configurações específicas por modalidade
        self.payment_configs = PaymentMethodConfigs.from_dict(
            config.get("payment_method_configs", {})
        )
        
        logger.info(f"🏗️ Terminal adapter initialized with payment method configs")
    
    # === Métodos de Conexão ===
    
    @abstractmethod
    async def connect(self) -> bool:
        """Conecta com o terminal físico"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Desconecta do terminal físico"""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """Verifica se está conectado"""
        pass
    
    @abstractmethod
    async def get_terminal_info(self) -> TerminalInfo:
        """Obtém informações do terminal"""
        pass
    
    # === Métodos de Validação ===
    
    def validate_transaction_request(self, request: TransactionRequest) -> List[str]:
        """🆕 Valida requisição de transação com configurações específicas"""
        errors = []
        
        # Validação básica
        if request.amount <= 0:
            errors.append("Valor deve ser maior que zero")
        
        # Validação específica por modalidade
        config_errors = request.validate_with_config(self.payment_configs)
        errors.extend(config_errors)
        
        return errors
    
    def _validate_cpf(self, cpf: str) -> bool:
        """🆕 Valida CPF brasileiro"""
        if not cpf:
            return False
        
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se não são todos iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Validação dos dígitos verificadores
        def calculate_digit(cpf_partial):
            sum_val = sum(int(cpf_partial[i]) * (len(cpf_partial) + 1 - i) for i in range(len(cpf_partial)))
            remainder = sum_val % 11
            return 0 if remainder < 2 else 11 - remainder
        
        first_digit = calculate_digit(cpf[:9])
        second_digit = calculate_digit(cpf[:10])
        
        return cpf[9] == str(first_digit) and cpf[10] == str(second_digit)

    # === Métodos de Transação ===
    
    @abstractmethod
    async def start_transaction(self, request: TransactionRequest) -> str:
        """
        Inicia uma transação no terminal
        
        🆕 Inclui validação automática das configurações específicas por modalidade
        """
        # Validação automática antes de iniciar transação
        validation_errors = self.validate_transaction_request(request)
        if validation_errors:
            raise PaymentTerminalError(f"Validação falhou: {'; '.join(validation_errors)}")
        
        pass
    
    @abstractmethod
    async def get_transaction_status(self, transaction_id: str) -> TransactionResponse:
        """Obtém status da transação"""
        pass
    
    @abstractmethod
    async def cancel_transaction(self, transaction_id: str) -> bool:
        """Cancela transação em andamento"""
        pass
    
    @abstractmethod
    async def confirm_transaction(self, transaction_id: str) -> TransactionResponse:
        """Confirma transação (para fluxos que requerem confirmação)"""
        pass
    
    # === Métodos de Impressão ===
    
    @abstractmethod
    async def print_receipt(self, transaction_id: str, receipt_type: str = "customer") -> bool:
        """Imprime comprovante no terminal"""
        pass
    
    @abstractmethod
    async def print_custom_text(self, text: str) -> bool:
        """Imprime texto customizado"""
        pass
    
    # === Métodos de Configuração ===
    
    @abstractmethod
    async def get_supported_payment_methods(self) -> List[PaymentMethod]:
        """Retorna métodos de pagamento suportados"""
        pass
    
    @abstractmethod
    async def configure_terminal(self, settings: Dict[str, Any]) -> bool:
        """Configura parâmetros do terminal"""
        pass
    
    # === Métodos de Monitoramento ===
    
    def add_status_callback(self, callback: callable):
        """Adiciona callback para mudanças de status"""
        self._status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: callable):
        """Remove callback de status"""
        if callback in self._status_callbacks:
            self._status_callbacks.remove(callback)
    
    async def _notify_status_change(self, old_status: TerminalStatus, new_status: TerminalStatus):
        """Notifica mudança de status"""
        logger.info(f"🔄 Terminal status changed: {old_status} → {new_status}")
        
        for callback in self._status_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(old_status, new_status, self)
                else:
                    callback(old_status, new_status, self)
            except Exception as e:
                logger.error(f"❌ Error in status callback: {e}")
    
    def _set_status(self, new_status: TerminalStatus):
        """Define novo status e notifica callbacks"""
        if self.status != new_status:
            old_status = self.status
            self.status = new_status
            asyncio.create_task(self._notify_status_change(old_status, new_status))
    
    # === Métodos Utilitários ===
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do terminal"""
        try:
            is_connected = await self.is_connected()
            terminal_info = await self.get_terminal_info() if is_connected else None
            
            return {
                "status": self.status.value,
                "connected": is_connected,
                "terminal_info": terminal_info.__dict__ if terminal_info else None,
                "last_check": datetime.utcnow().isoformat(),
                "config": {
                    "type": self.config.get("type"),
                    "model": self.config.get("model"),
                    "connection": self.config.get("connection_type")
                }
            }
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": TerminalStatus.ERROR.value,
                "connected": False,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def reset_terminal(self) -> bool:
        """Reseta o terminal (reconecta)"""
        try:
            logger.info("🔄 Resetting terminal...")
            await self.disconnect()
            await asyncio.sleep(2)  # Aguarda desconexão completa
            return await self.connect()
        except Exception as e:
            logger.error(f"❌ Terminal reset failed: {e}")
            return False
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(status={self.status.value}, config={self.config.get('type', 'unknown')})" 