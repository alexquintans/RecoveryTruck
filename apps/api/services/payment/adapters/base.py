from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Union
from datetime import datetime
import logging

from services.printer_service import (
    printer_service, ReceiptData, ReceiptType, PrinterConfig, PrinterType, PrinterConnection
)
from services.webhook_validator import webhook_validator, WebhookProvider

logger = logging.getLogger(__name__)

class PaymentAdapter(ABC):
    """🔌 Interface base para adaptadores de pagamento com integração de impressão"""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa adaptador com configuração"""
        self.config = config
        self._setup_printer()
    
    def _setup_printer(self):
        """Configura impressora para o adaptador"""
        printer_config = self.config.get("printer", {})
        
        if printer_config.get("enabled", True):
            # Configuração padrão da impressora
            printer_id = f"{self.__class__.__name__.lower()}_printer"
            
            config = PrinterConfig(
                name=printer_config.get("name", "Default"),
                printer_type=PrinterType(printer_config.get("type", "thermal")),
                connection_type=PrinterConnection(printer_config.get("connection", "file")),
                port=printer_config.get("port"),
                ip_address=printer_config.get("ip_address"),
                tcp_port=printer_config.get("tcp_port", 9100),
                paper_width=printer_config.get("paper_width", 80),
                chars_per_line=printer_config.get("chars_per_line", 48),
                encoding=printer_config.get("encoding", "cp850"),
                cut_paper=printer_config.get("cut_paper", True),
                beep=printer_config.get("beep", False)
            )
            
            printer_service.register_printer(printer_id, config)
            self.printer_id = printer_id
        else:
            self.printer_id = None
    
    @abstractmethod
    async def create_payment(self, amount: float, description: str, metadata: Dict) -> Dict:
        """Cria uma nova transação de pagamento."""
        pass
    
    @abstractmethod
    async def check_status(self, transaction_id: str) -> str:
        """Verifica o status de uma transação."""
        pass
    
    @abstractmethod
    async def cancel_payment(self, transaction_id: str) -> bool:
        """Cancela uma transação pendente."""
        pass
    
    async def print_receipt(
        self, 
        transaction_id: str, 
        receipt_type: str = "customer",
        transaction_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """🖨️ Imprime o comprovante de uma transação"""
        
        if not self.printer_id:
            logger.warning(f"⚠️ Printer not configured for {self.__class__.__name__}")
            return False
        
        try:
            # Obtém dados da transação se não fornecidos
            if not transaction_data:
                transaction_data = await self._get_transaction_data(transaction_id)
            
            if not transaction_data:
                logger.error(f"❌ Transaction data not found: {transaction_id}")
                return False
            
            # Cria dados do comprovante
            receipt_data = self._create_receipt_data(transaction_id, receipt_type, transaction_data)
            
            # Imprime comprovante
            success = await printer_service.print_receipt(receipt_data, self.printer_id)
            
            if success:
                logger.info(f"✅ Receipt printed successfully: {transaction_id}")
            else:
                logger.error(f"❌ Failed to print receipt: {transaction_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error printing receipt {transaction_id}: {e}")
            return False
    
    async def _get_transaction_data(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Obtém dados da transação (implementação específica por adaptador)"""
        try:
            # Chama API do provedor para obter dados da transação
            response = await self._fetch_transaction_details(transaction_id)
            return response
        except Exception as e:
            logger.error(f"❌ Error fetching transaction data {transaction_id}: {e}")
            return None
    
    @abstractmethod
    async def _fetch_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """Busca detalhes da transação na API do provedor"""
        pass
    
    def _create_receipt_data(
        self, 
        transaction_id: str, 
        receipt_type: str, 
        transaction_data: Dict[str, Any]
    ) -> ReceiptData:
        """Cria dados do comprovante a partir dos dados da transação"""
        
        # Mapeia tipo de comprovante
        receipt_type_enum = ReceiptType.CUSTOMER
        if receipt_type == "merchant":
            receipt_type_enum = ReceiptType.MERCHANT
        elif receipt_type == "both":
            receipt_type_enum = ReceiptType.BOTH
        
        # Extrai dados básicos
        amount = float(transaction_data.get("amount", 0)) / 100  # Converte de centavos
        payment_method = transaction_data.get("payment_method", "unknown")
        status = transaction_data.get("status", "unknown")
        
        # Timestamp da transação
        timestamp_str = transaction_data.get("created_at") or transaction_data.get("timestamp")
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()
        
        # Dados do estabelecimento
        merchant_data = transaction_data.get("merchant", {})
        merchant_name = merchant_data.get("name", self.config.get("merchant_name", "Estabelecimento"))
        merchant_cnpj = merchant_data.get("cnpj", self.config.get("merchant_cnpj", "00000000000000"))
        merchant_address = merchant_data.get("address", self.config.get("merchant_address"))
        
        # Dados do cliente
        customer_data = transaction_data.get("customer", {})
        customer_name = customer_data.get("name")
        customer_cpf = customer_data.get("cpf")
        
        # Dados específicos por modalidade
        card_data = transaction_data.get("card", {})
        pix_data = transaction_data.get("pix", {})
        boleto_data = transaction_data.get("boleto", {})
        
        return ReceiptData(
            transaction_id=transaction_id,
            receipt_type=receipt_type_enum,
            amount=amount,
            payment_method=payment_method,
            status=status,
            timestamp=timestamp,
            merchant_name=merchant_name,
            merchant_cnpj=merchant_cnpj,
            merchant_address=merchant_address,
            customer_name=customer_name,
            customer_cpf=customer_cpf,
            # Dados do cartão
            card_brand=card_data.get("brand"),
            card_last_digits=card_data.get("last_digits"),
            installments=transaction_data.get("installments"),
            authorization_code=transaction_data.get("authorization_code"),
            nsu=transaction_data.get("nsu"),
            # Dados PIX
            pix_key=pix_data.get("key"),
            pix_qr_code=pix_data.get("qr_code"),
            # Dados Boleto
            boleto_barcode=boleto_data.get("barcode"),
            boleto_due_date=self._parse_date(boleto_data.get("due_date")),
            # Metadados
            metadata=transaction_data.get("metadata", {})
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Converte string de data para datetime"""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except:
                return None
    
    @abstractmethod
    async def get_payment_link(self, transaction_id: str) -> Optional[str]:
        """Obtém o link de pagamento para QR Code."""
        pass
    
    def verify_webhook(
        self, 
        payload: Union[str, bytes, Dict[str, Any]], 
        headers: Dict[str, str],
        client_ip: Optional[str] = None
    ) -> bool:
        """🔐 Verifica webhook com validação completa de segurança"""
        
        # Mapeia classe para provider
        provider_map = {
            "SicrediAdapter": WebhookProvider.SICREDI,
            "StoneAdapter": WebhookProvider.STONE,
            "PagSeguroAdapter": WebhookProvider.PAGSEGURO,
            "MercadoPagoAdapter": WebhookProvider.MERCADOPAGO,
            "SafraPayAdapter": WebhookProvider.SAFRAPAY,
            "PagBankAdapter": WebhookProvider.PAGBANK
        }
        
        provider = provider_map.get(self.__class__.__name__)
        if not provider:
            logger.error(f"❌ Unknown adapter: {self.__class__.__name__}")
            return False
        
        try:
            # Valida webhook usando o serviço avançado
            result = webhook_validator.validate_webhook(
                provider=provider,
                payload=payload,
                headers=headers,
                client_ip=client_ip
            )
            
            if result.is_valid:
                logger.info(f"✅ Webhook validated: {provider.value} - {result.transaction_id}")
                
                # Log warnings se houver
                for warning in result.warnings:
                    logger.warning(f"⚠️ {warning}")
                
                return True
            else:
                logger.error(f"❌ Webhook validation failed: {provider.value}")
                for error in result.errors:
                    logger.error(f"   - {error}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Webhook validation error: {e}")
            return False 