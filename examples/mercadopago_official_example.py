#!/usr/bin/env python3
"""
💰 Exemplo Oficial Mercado Pago - API de Preferências
Baseado na documentação oficial do Mercado Pago
"""

import mercadopago
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_preference_official():
    """Exemplo baseado na documentação oficial do Mercado Pago"""
    
    # Inicializar SDK
    sdk = mercadopago.SDK("PROD_ACCESS_TOKEN")  # Substitua pelo seu token
    
    # Request baseado na documentação oficial
    request = {
        "items": [
            {
                "id": "1234",
                "title": "Serviço de Recuperação",
                "description": "Recuperação de veículo",
                "picture_url": "https://www.recoverytruck.com/logo.jpg",
                "category_id": "services",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 100.00,
            },
        ],
        "marketplace_fee": 0,
        "payer": {
            "name": "João",
            "surname": "Silva",
            "email": "joao.silva@example.com",
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
            "success": "https://recoverytruck.com/payment/success",
            "failure": "https://recoverytruck.com/payment/failure",
            "pending": "https://recoverytruck.com/payment/pending",
        },
        "differential_pricing": {
            "id": 1,
        },
        "expires": False,
        "additional_info": "Serviço de recuperação de veículo",
        "auto_return": "approved",
        "binary_mode": True,
        "external_reference": "payment_123456",
        "marketplace": "marketplace",
        "notification_url": "https://recoverytruck.com/webhooks/mercadopago",
        "operation_type": "regular_payment",
        "payment_methods": {
            "default_payment_method_id": "master",
            "excluded_payment_types": [
                {
                    "id": "ticket",
                },
            ],
            "excluded_payment_methods": [
                {
                    "id": "",
                },
            ],
            "installments": 12,
            "default_installments": 1,
        },
        "shipments": {
            "mode": "custom",
            "local_pickup": False,
            "default_shipping_method": None,
            "free_methods": [
                {
                    "id": 1,
                },
            ],
            "cost": 0,
            "free_shipping": True,
            "dimensions": "10x10x20,500",
            "receiver_address": {
                "zip_code": "01234-567",
                "street_number": 123,
                "street_name": "Rua das Flores",
                "floor": "1",
                "apartment": "101",
            },
        },
        "statement_descriptor": "RecoveryTruck",
    }
    
    try:
        # Criar preferência usando SDK Python
        preference_response = sdk.preference().create(request)
        
        if preference_response["status"] == 201:
            preference = preference_response["response"]
            
            print("✅ Preferência criada com sucesso!")
            print(f"📋 ID da Preferência: {preference['id']}")
            print(f"🔗 Link de Pagamento: {preference['init_point']}")
            print(f"🔗 Link Sandbox: {preference.get('sandbox_init_point', 'N/A')}")
            
            # Mostrar dados da preferência
            print("\n📊 Dados da Preferência:")
            print(f"   - Items: {len(preference['items'])}")
            print(f"   - Payer: {preference['payer']['name']} {preference['payer']['surname']}")
            print(f"   - Email: {preference['payer']['email']}")
            print(f"   - External Reference: {preference['external_reference']}")
            print(f"   - Binary Mode: {preference.get('binary_mode', False)}")
            print(f"   - Auto Return: {preference.get('auto_return', 'N/A')}")
            
            return preference
            
        else:
            print(f"❌ Erro ao criar preferência: {preference_response}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def create_simple_preference():
    """Exemplo simplificado para testes"""
    
    sdk = mercadopago.SDK("TEST_ACCESS_TOKEN")  # Token de teste
    
    simple_request = {
        "items": [
            {
                "title": "Serviço de Recuperação",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 50.00
            }
        ],
        "payer": {
            "email": "teste@exemplo.com",
            "name": "Teste",
            "surname": "Usuário"
        },
        "back_urls": {
            "success": "https://exemplo.com/success",
            "failure": "https://exemplo.com/failure",
            "pending": "https://exemplo.com/pending"
        },
        "auto_return": "approved",
        "external_reference": "test_123",
        "notification_url": "https://exemplo.com/webhook",
        "binary_mode": True
    }
    
    try:
        result = sdk.preference().create(simple_request)
        
        if result["status"] == 201:
            preference = result["response"]
            print(f"✅ Preferência simples criada: {preference['id']}")
            return preference
        else:
            print(f"❌ Erro: {result}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    """Função principal"""
    
    print("💰 Exemplo Oficial Mercado Pago - API de Preferências")
    print("=" * 60)
    
    # Escolher tipo de exemplo
    print("\nEscolha o tipo de exemplo:")
    print("1. Exemplo completo (documentação oficial)")
    print("2. Exemplo simplificado (para testes)")
    
    choice = input("\nDigite 1 ou 2: ").strip()
    
    if choice == "1":
        print("\n🔄 Criando preferência completa...")
        preference = create_preference_official()
    elif choice == "2":
        print("\n🔄 Criando preferência simplificada...")
        preference = create_simple_preference()
    else:
        print("❌ Opção inválida")
        return
    
    if preference:
        print(f"\n🎉 Preferência criada com sucesso!")
        print(f"🔗 Link para pagamento: {preference['init_point']}")
        print(f"📋 ID: {preference['id']}")
        
        # Salvar dados em arquivo para referência
        with open("preference_data.json", "w") as f:
            json.dump(preference, f, indent=2, ensure_ascii=False)
        print("💾 Dados salvos em 'preference_data.json'")
    else:
        print("❌ Falha ao criar preferência")

if __name__ == "__main__":
    main() 