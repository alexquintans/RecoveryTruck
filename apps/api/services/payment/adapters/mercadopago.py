import mercadopago
from mercadopago.config import RequestOptions
from typing import Dict, Optional, Any
import logging
from .base import PaymentAdapter
import os

logger = logging.getLogger(__name__)

class MercadoPagoAdapter(PaymentAdapter):
    """💰 Adaptador para integração com Mercado Pago usando SDK Python oficial"""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o adaptador com as configurações do tenant."""
        super().__init__(config)  # Inicializa impressora
        
        self.access_token = config["access_token"]
        self.webhook_url = config.get("webhook_url")
        self.redirect_url_base = config.get("redirect_url_base")
        
        # Inicializar SDK Python do Mercado Pago
        self.sdk = mercadopago.SDK(self.access_token)
        
        logger.info(f"💰 MercadoPagoAdapter initialized with SDK Python")
    
    async def create_payment_preference(self, amount: float, description: str, metadata: Dict) -> Dict:
        """Cria uma preferência de pagamento para o Checkout Pro usando a API de Preferências."""
        if not self.redirect_url_base:
            raise ValueError("A URL base de redirecionamento ('redirect_url_base') não foi configurada.")

        # Dados da preferência conforme documentação oficial do Mercado Pago
        preference_data = {
            "items": [
                {
                    "id": metadata.get("service_id", "service_001"),
                    "title": description,
                    "description": metadata.get("service_description", "Serviço de Recuperação"),
                    "picture_url": metadata.get("picture_url", "https://www.recoverytruck.com/logo.png"),
                    "category_id": "services",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": amount
                }
            ],
            "payer": {
                "email": metadata.get("customer_email", "cliente@recoverytruck.com"),
                "name": metadata.get("customer_name", "Cliente").split()[0] if metadata.get("customer_name") else "Cliente",
                "surname": " ".join(metadata.get("customer_name", "Cliente").split()[1:]) if metadata.get("customer_name") and len(metadata.get("customer_name", "").split()) > 1 else "",
            },
            "back_urls": {
                "success": os.getenv("FRONTEND_URL", "https://seu-frontend.vercel.app") + "/payment/success",
                "failure": os.getenv("FRONTEND_URL", "https://seu-frontend.vercel.app") + "/payment/failure",
                "pending": os.getenv("FRONTEND_URL", "https://seu-frontend.vercel.app") + "/payment/pending"
            },
            "expires": False,
            "additional_info": metadata.get("additional_info", f"Serviço: {description}"),
            "binary_mode": True,
            "external_reference": metadata.get("payment_session_id"),
            "notification_url": self.webhook_url,
            "operation_type": "regular_payment",
            "payment_methods": {
                "installments": 12,
                "default_installments": 1,
                # Permitir todos os métodos de pagamento para teste
                # "excluded_payment_types": [
                #     {"id": "credit_card"},
                #     {"id": "debit_card"},
                #     {"id": "ticket"}
                # ],
                # "excluded_payment_methods": [
                #     {"id": "visa"},
                #     {"id": "master"},
                #     {"id": "elo"},
                #     {"id": "hipercard"},
                #     {"id": "amex"}
                # ]
            },
            "shipments": {
                "mode": "not_specified",
                "free_shipping": True,
            },
            "statement_descriptor": "RecoveryTruck",
        }
        
        try:
            # Usar API de Preferências do Mercado Pago via SDK Python
            logger.info(f"🔍 Criando preferência com dados: {preference_data}")
            result = self.sdk.preference().create(preference_data)
            
            logger.info(f"🔍 Resultado da criação: {result}")
            
            if result["status"] != 201:
                logger.error(f"❌ Erro ao criar preferência: {result}")
                raise Exception(f"Erro ao criar preferência: {result.get('error', 'Unknown error')}")
            
            preference = result["response"]
            
            logger.info(f"✅ Preferência criada via API: {preference['id']}")
            
            # Buscar o QR Code PIX da preferência
            qr_code = None
            if preference.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code"):
                qr_code = preference["point_of_interaction"]["transaction_data"]["qr_code"]
            elif preference.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code_base64"):
                qr_code = preference["point_of_interaction"]["transaction_data"]["qr_code_base64"]
            
            logger.info(f"🔍 QR Code encontrado: {qr_code is not None}")
            
            # Retorna o QR Code PIX e o ID da preferência
            return {
                "qr_code": qr_code,
                "preference_id": preference["id"],
                "init_point": preference.get("init_point")  # Mantém para compatibilidade
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar preferência Mercado Pago: {e}")
            raise
    
    async def create_payment(self, amount: float, description: str, metadata: Dict) -> Dict:
        """Cria uma nova transação de pagamento (usando preferência)."""
        return await self.create_payment_preference(amount, description, metadata)
    
    async def check_status(self, transaction_id: str) -> str:
        """Verifica o status de uma transação usando o ID de pagamento."""
        try:
            result = self.sdk.preference().get(transaction_id)
            
            if result["status"] != 200:
                logger.error(f"❌ Erro ao buscar pagamento: {result}")
                raise Exception(f"Erro ao buscar pagamento: {result.get('error', 'Unknown error')}")
            
            payment = result["response"]
            return payment["status"]
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status do pagamento {transaction_id}: {e}")
            raise
    
    async def cancel_payment(self, transaction_id: str) -> bool:
        """Cancela uma transação pendente."""
        try:
            cancel_data = {"status": "cancelled"}
            result = self.sdk.preference().update(transaction_id, cancel_data)
            
            if result["status"] != 200:
                logger.error(f"❌ Erro ao cancelar pagamento: {result}")
                return False
            
            logger.info(f"✅ Pagamento {transaction_id} cancelado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao cancelar pagamento {transaction_id}: {e}")
            return False
    
    async def _fetch_transaction_details(self, transaction_id: str) -> Dict[str, Any]:
        """🔍 Busca detalhes completos da transação usando SDK Python"""
        try:
            result = self.sdk.preference().get(transaction_id)
            
            if result["status"] != 200:
                logger.error(f"❌ Erro ao buscar detalhes do pagamento: {result}")
                raise Exception(f"Erro ao buscar detalhes: {result.get('error', 'Unknown error')}")
            
            transaction_data = result["response"]
            
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
        try:
            result = self.sdk.preference().get(transaction_id)
            
            if result["status"] != 200:
                logger.error(f"❌ Erro ao buscar pagamento: {result}")
                return None
            
            payment = result["response"]
            
            # Verificar se tem QR Code (PIX)
            if payment.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code"):
                return payment["point_of_interaction"]["transaction_data"]["qr_code"]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter link de pagamento {transaction_id}: {e}")
            return None
    
    def create_payment_with_card(self, amount: float, card_token: str, payment_method_id: str, 
                                installments: int = 1, payer_email: str = None) -> Dict:
        """Cria pagamento com cartão usando SDK Python."""
        try:
            payment_data = {
                "transaction_amount": amount,
                "token": card_token,
                "description": "Pagamento RecoveryTruck",
                "payment_method_id": payment_method_id,
                "installments": installments,
                "payer": {
                    "email": payer_email or "cliente@recoverytruck.com"
                }
            }
            
            # Configurar opções de request (opcional)
            request_options = RequestOptions()
            request_options.custom_headers = {
                'x-idempotency-key': f'payment_{card_token}_{int(amount * 100)}'
            }
            
            result = self.sdk.preference().create(payment_data, request_options)
            
            if result["status"] != 201:
                logger.error(f"❌ Erro ao criar pagamento com cartão: {result}")
                raise Exception(f"Erro ao criar pagamento: {result.get('error', 'Unknown error')}")
            
            payment = result["response"]
            logger.info(f"✅ Pagamento com cartão criado: {payment['id']}")
            
            return payment
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar pagamento com cartão: {e}")
            raise
    
    def get_payment_methods(self) -> Dict:
        """Obtém métodos de pagamento disponíveis."""
        try:
            result = self.sdk.payment_methods().list()
            
            if result["status"] != 200:
                logger.error(f"❌ Erro ao buscar métodos de pagamento: {result}")
                return {}
            
            return result["response"]
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar métodos de pagamento: {e}")
            return {}