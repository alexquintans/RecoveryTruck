import hmac
import hashlib
import json
from typing import Dict, Optional, Any
import httpx
import logging
from .base import PaymentAdapter

logger = logging.getLogger(__name__)

class MercadoPagoAdapter(PaymentAdapter):
    """💰 Adaptador para integração com Mercado Pago com impressão completa"""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o adaptador com as configurações do tenant."""
        super().__init__(config)  # Inicializa impressora
        
        self.api_url = config.get("api_url", "https://api.mercadopago.com/v1")
        self.access_token = config["access_token"]
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )
        
        logger.info(f"💰 MercadoPagoAdapter initialized")
    
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
    
    async def _fetch_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """🔍 Busca detalhes completos da transação na API MercadoPago"""
        try:
            response = await self.client.get(f"/payments/{transaction_id}")
            response.raise_for_status()
            
            transaction_data = response.json()
            
            # Enriquece dados com informações específicas do MercadoPago
            transaction_data["merchant"] = {
                "name": self.config.get("merchant_name", "MercadoPago Merchant"),
                "cnpj": self.config.get("merchant_cnpj", "00000000000000"),
                "address": self.config.get("merchant_address")
            }
            
            logger.info(f"🔍 MercadoPago transaction details fetched: {transaction_id}")
            return transaction_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching MercadoPago transaction {transaction_id}: {e}")
            raise
    
    async def get_payment_link(self, transaction_id: str) -> Optional[str]:
        """Obtém o link de pagamento para QR Code."""
        response = await self.client.get(f"/payments/{transaction_id}")
        response.raise_for_status()
        
        data = response.json()
        if data.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code"):
            return data["point_of_interaction"]["transaction_data"]["qr_code"]
        return None