#!/usr/bin/env python3
"""
💰 Exemplo de uso do SDK Python do Mercado Pago
Demonstra como usar o SDK oficial para criar preferências, pagamentos e webhooks
"""

import mercadopago
from mercadopago.config import RequestOptions
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MercadoPagoExample:
    """Exemplo de uso do SDK Python do Mercado Pago"""
    
    def __init__(self, access_token: str):
        """Inicializa o SDK com o access token."""
        self.sdk = mercadopago.SDK(access_token)
        logger.info("✅ SDK Mercado Pago inicializado")
    
    def create_preference(self, amount: float, description: str, customer_email: str = None) -> dict:
        """Cria uma preferência de pagamento para Checkout Pro."""
        try:
            preference_data = {
                "items": [
                    {
                        "id": "service_001",
                        "title": description,
                        "description": "Serviço de Recuperação de Veículos",
                        "picture_url": "https://recoverytruck.com/logo.png",
                        "category_id": "services",
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": amount
                    }
                ],
                "payer": {
                    "name": "João",
                    "surname": "Silva",
                    "email": customer_email or "cliente@exemplo.com",
                    "phone": {
                        "area_code": "11",
                        "number": "999999999",
                    },
                    "identification": {
                        "type": "CPF",
                        "number": "12345678901",
                    },
                    "address": {
                        "zip_code": "01234-567",
                        "street_name": "Rua das Flores",
                        "street_number": 123,
                    },
                },
                "back_urls": {
                    "success": "https://seu-dominio.com/payment/success",
                    "failure": "https://seu-dominio.com/payment/failure",
                    "pending": "https://seu-dominio.com/payment/pending"
                },
                "expires": False,
                "additional_info": f"Serviço: {description}",
                "auto_return": "approved",
                "binary_mode": True,  # Apenas aprovado ou rejeitado
                "external_reference": f"payment_{int(amount * 100)}",
                "notification_url": "https://seu-dominio.com/webhooks/mercadopago",
                "operation_type": "regular_payment",
                "payment_methods": {
                    "excluded_payment_types": [
                        {"id": "ticket"},  # Excluir boleto
                    ],
                    "excluded_payment_methods": [
                        {"id": ""},  # Não excluir nenhum método específico
                    ],
                    "installments": 12,
                    "default_installments": 1,
                },
                "statement_descriptor": "RecoveryTruck",
                "metadata": {
                    "source": "totem",
                    "amount": amount,
                    "service_type": "recovery"
                }
            }
            
            result = self.sdk.preference().create(preference_data)
            
            if result["status"] != 201:
                logger.error(f"❌ Erro ao criar preferência: {result}")
                return None
            
            preference = result["response"]
            logger.info(f"✅ Preferência criada: {preference['id']}")
            
            return {
                "preference_id": preference["id"],
                "init_point": preference["init_point"],
                "sandbox_init_point": preference.get("sandbox_init_point")
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar preferência: {e}")
            return None
    
    def create_payment_with_card(self, amount: float, card_token: str, payment_method_id: str = "visa",
                                installments: int = 1, payer_email: str = None) -> dict:
        """Cria pagamento com cartão."""
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
            
            # Configurar opções de request com idempotência
            request_options = RequestOptions()
            request_options.custom_headers = {
                'x-idempotency-key': f'payment_{card_token}_{int(amount * 100)}'
            }
            
            result = self.sdk.preference().create(payment_data, request_options)
            
            if result["status"] != 201:
                logger.error(f"❌ Erro ao criar pagamento: {result}")
                return None
            
            payment = result["response"]
            logger.info(f"✅ Pagamento criado: {payment['id']} - Status: {payment['status']}")
            
            return payment
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar pagamento: {e}")
            return None
    
    def get_payment_status(self, payment_id: str) -> dict:
        """Obtém status de um pagamento."""
        try:
            result = self.sdk.preference().get(payment_id)
            
            if result["status"] != 200:
                logger.error(f"❌ Erro ao buscar pagamento: {result}")
                return None
            
            payment = result["response"]
            logger.info(f"📊 Status do pagamento {payment_id}: {payment['status']}")
            
            return {
                "id": payment["id"],
                "status": payment["status"],
                "amount": payment["transaction_amount"],
                "payment_method": payment.get("payment_method_id"),
                "created_date": payment["date_created"],
                "approved_date": payment.get("date_approved")
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar pagamento {payment_id}: {e}")
            return None
    
    def cancel_payment(self, payment_id: str) -> bool:
        """Cancela um pagamento."""
        try:
            cancel_data = {"status": "cancelled"}
            result = self.sdk.preference().update(payment_id, cancel_data)
            
            if result["status"] != 200:
                logger.error(f"❌ Erro ao cancelar pagamento: {result}")
                return False
            
            logger.info(f"✅ Pagamento {payment_id} cancelado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao cancelar pagamento {payment_id}: {e}")
            return False
    
    def get_payment_methods(self) -> list:
        """Lista métodos de pagamento disponíveis."""
        try:
            result = self.sdk.payment_methods().list()
            
            if result["status"] != 200:
                logger.error(f"❌ Erro ao buscar métodos de pagamento: {result}")
                return []
            
            methods = result["response"]
            logger.info(f"📋 {len(methods)} métodos de pagamento encontrados")
            
            return methods
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar métodos de pagamento: {e}")
            return []
    
    def process_webhook(self, webhook_data: dict) -> dict:
        """Processa dados do webhook."""
        try:
            # Verificar se é um webhook de pagamento
            if webhook_data.get("type") == "payment":
                payment_id = webhook_data["data"]["id"]
                payment_info = self.get_payment_status(payment_id)
                
                if payment_info:
                    logger.info(f"🔄 Webhook processado: {payment_id} - {payment_info['status']}")
                    return payment_info
            
            return webhook_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar webhook: {e}")
            return None

def main():
    """Exemplo de uso do SDK."""
    
    # Configurar access token (substitua pelo seu)
    ACCESS_TOKEN = "TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # Sandbox
    # ACCESS_TOKEN = "APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # Produção
    
    # Inicializar SDK
    mp = MercadoPagoExample(ACCESS_TOKEN)
    
    print("💰 Exemplo de uso do SDK Python Mercado Pago")
    print("=" * 50)
    
    # 1. Criar preferência para Checkout Pro
    print("\n1. Criando preferência para Checkout Pro...")
    preference = mp.create_preference(
        amount=50.00,
        description="Serviço de Recuperação",
        customer_email="cliente@exemplo.com"
    )
    
    if preference:
        print(f"✅ Preferência criada: {preference['preference_id']}")
        print(f"🔗 Link de pagamento: {preference['init_point']}")
    
    # 2. Listar métodos de pagamento
    print("\n2. Listando métodos de pagamento...")
    methods = mp.get_payment_methods()
    for method in methods[:5]:  # Mostrar apenas os primeiros 5
        print(f"💳 {method['name']} ({method['id']})")
    
    # 3. Simular webhook
    print("\n3. Simulando processamento de webhook...")
    webhook_data = {
        "type": "payment",
        "data": {"id": "123456789"}
    }
    webhook_result = mp.process_webhook(webhook_data)
    if webhook_result:
        print(f"🔄 Webhook processado: {webhook_result}")
    
    print("\n✅ Exemplo concluído!")

if __name__ == "__main__":
    main() 