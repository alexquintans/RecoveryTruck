import hmac
import hashlib
import json
from typing import Dict, Optional
import httpx
from .base import PaymentAdapter

class PagBankAdapter(PaymentAdapter):
    """Adaptador para integração com PagBank (antigo PagSeguro)."""
    
    def __init__(self, config: Dict):
        """Inicializa o adaptador com as configurações do tenant."""
        self.api_url = config.get("api_url", "https://api.pagbank.com.br/v1")
        self.api_key = config["api_key"]
        self.merchant_id = config["merchant_id"]
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    def _generate_signature(self, data: Dict) -> str:
        """Gera assinatura HMAC para autenticação."""
        return hmac.new(
            self.api_key.encode(),
            json.dumps(data).encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def create_payment(self, amount: float, description: str, metadata: Dict) -> Dict:
        """Cria uma nova transação de pagamento."""
        payment_data = {
            "merchant_id": self.merchant_id,
            "amount": int(amount * 100),  # Convert to cents
            "currency": "BRL",
            "description": description,
            "metadata": metadata,
            "payment_methods": ["credit_card", "debit_card", "pix", "boleto"]
        }
        
        # Add signature
        payment_data["signature"] = self._generate_signature(payment_data)
        
        # Make API request
        response = await self.client.post("/payments", json=payment_data)
        response.raise_for_status()
        
        return response.json()
    
    async def check_status(self, transaction_id: str) -> str:
        """Verifica o status de uma transação."""
        response = await self.client.get(f"/payments/{transaction_id}")
        response.raise_for_status()
        
        data = response.json()
        return data["status"]
    
    async def cancel_payment(self, transaction_id: str) -> bool:
        """Cancela uma transação pendente."""
        response = await self.client.post(f"/payments/{transaction_id}/cancel")
        response.raise_for_status()
        
        return True
    
    async def print_receipt(self, transaction_id: str) -> bool:
        """Imprime o comprovante de uma transação."""
        response = await self.client.get(f"/payments/{transaction_id}/receipt")
        response.raise_for_status()
        
        # TODO: Implement printer integration
        return True
    
    async def get_payment_link(self, transaction_id: str) -> Optional[str]:
        """Obtém o link de pagamento para QR Code."""
        response = await self.client.get(f"/payments/{transaction_id}/link")
        response.raise_for_status()
        
        data = response.json()
        return data.get("payment_link")
    
    def verify_webhook(self, payload: Dict, signature: str) -> bool:
        """Verifica a assinatura do webhook."""
        expected_signature = self._generate_signature(payload)
        return hmac.compare_digest(signature, expected_signature) 