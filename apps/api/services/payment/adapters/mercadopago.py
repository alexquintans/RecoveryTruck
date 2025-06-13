import hmac
import hashlib
import json
from typing import Dict, Optional
import httpx
from .base import PaymentAdapter

class MercadoPagoAdapter(PaymentAdapter):
    """Adaptador para integração com Mercado Pago."""
    
    def __init__(self, config: Dict):
        """Inicializa o adaptador com as configurações do tenant."""
        self.api_url = config.get("api_url", "https://api.mercadopago.com/v1")
        self.access_token = config["access_token"]
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )
    
    def _generate_signature(self, data: Dict) -> str:
        """Gera assinatura HMAC para autenticação."""
        return hmac.new(
            self.access_token.encode(),
            json.dumps(data).encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def create_payment(self, amount: float, description: str, metadata: Dict) -> Dict:
        """Cria uma nova transação de pagamento."""
        payment_data = {
            "transaction_amount": amount,
            "description": description,
            "payment_method_id": "pix",  # Default to PIX
            "payer": {
                "email": metadata.get("customer_email", ""),
                "first_name": metadata.get("customer_name", "").split()[0],
                "last_name": " ".join(metadata.get("customer_name", "").split()[1:])
            },
            "metadata": metadata
        }
        
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
        response = await self.client.put(f"/payments/{transaction_id}", json={"status": "cancelled"})
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
        response = await self.client.get(f"/payments/{transaction_id}")
        response.raise_for_status()
        
        data = response.json()
        if data.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code"):
            return data["point_of_interaction"]["transaction_data"]["qr_code"]
        return None
    
    def verify_webhook(self, payload: Dict, signature: str) -> bool:
        """Verifica a assinatura do webhook."""
        expected_signature = self._generate_signature(payload)
        return hmac.compare_digest(signature, expected_signature) 