from abc import ABC, abstractmethod
from typing import Dict, Optional

class PaymentAdapter(ABC):
    """Interface base para adaptadores de pagamento."""
    
    @abstractmethod
    def create_payment(self, amount: float, description: str, metadata: Dict) -> Dict:
        """Cria uma nova transação de pagamento."""
        pass
    
    @abstractmethod
    def check_status(self, transaction_id: str) -> str:
        """Verifica o status de uma transação."""
        pass
    
    @abstractmethod
    def cancel_payment(self, transaction_id: str) -> bool:
        """Cancela uma transação pendente."""
        pass
    
    @abstractmethod
    def print_receipt(self, transaction_id: str) -> bool:
        """Imprime o comprovante de uma transação."""
        pass
    
    @abstractmethod
    def get_payment_link(self, transaction_id: str) -> Optional[str]:
        """Obtém o link de pagamento para QR Code."""
        pass
    
    @abstractmethod
    def verify_webhook(self, payload: Dict, signature: str) -> bool:
        """Verifica a assinatura do webhook."""
        pass 