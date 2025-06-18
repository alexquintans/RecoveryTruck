import hmac
import hashlib
import json
from typing import Dict, Optional, Any
import httpx
import logging
from .base import PaymentAdapter

logger = logging.getLogger(__name__)

class SicrediAdapter(PaymentAdapter):
    """🏦 Adaptador para integração com Sicredi com impressão completa"""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o adaptador com as configurações do tenant."""
        super().__init__(config)  # Inicializa impressora
        
        self.api_url = config["api_url"]
        self.api_key = config["api_key"]
        self.merchant_id = config["merchant_id"]
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        logger.info(f"🏦 SicrediAdapter initialized for merchant {self.merchant_id}")
    
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
            "metadata": metadata
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
    
    async def _fetch_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """🔍 Busca detalhes completos da transação na API Sicredi"""
        try:
            response = await self.client.get(f"/payments/{transaction_id}")
            response.raise_for_status()
            
            transaction_data = response.json()
            
            # Enriquece dados com informações específicas do Sicredi
            transaction_data["merchant"] = {
                "name": self.config.get("merchant_name", "Sicredi Merchant"),
                "cnpj": self.config.get("merchant_cnpj", "00000000000000"),
                "address": self.config.get("merchant_address")
            }
            
            logger.info(f"🔍 Transaction details fetched: {transaction_id}")
            return transaction_data
            
        except Exception as e:
            logger.error(f"❌ Error fetching Sicredi transaction {transaction_id}: {e}")
            raise
    
    async def get_payment_link(self, transaction_id: str) -> Optional[str]:
        """Obtém o link de pagamento para QR Code."""
        response = await self.client.get(f"/payments/{transaction_id}/link")
        response.raise_for_status()
        
        data = response.json()
        return data.get("payment_link")
    
 