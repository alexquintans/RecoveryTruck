#!/usr/bin/env python3
"""
Teste de Integração Mercado Pago Sandbox
=========================================

Este script testa a integração com o Mercado Pago usando credenciais de sandbox.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuração de Sandbox
SANDBOX_CONFIG = {
    "access_token": "TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",  # Token de teste
    "public_key": "TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",   # Chave pública de teste
    "api_url": "https://api.mercadopago.com/v1"
}

def test_sandbox_integration():
    """Testa a integração com sandbox do Mercado Pago"""
    
    print("🧪 Testando Integração Mercado Pago Sandbox")
    print("=" * 50)
    
    # 1. Testar conexão com API
    print("1️⃣ Testando conexão com API...")
    try:
        headers = {
            "Authorization": f"Bearer {SANDBOX_CONFIG['access_token']}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{SANDBOX_CONFIG['api_url']}/users/me", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Conexão OK - Usuário: {user_data.get('nickname', 'N/A')}")
            print(f"   Tipo de conta: {user_data.get('site_id', 'N/A')}")
        else:
            print(f"❌ Erro na conexão: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
    
    # 2. Criar preferência de teste
    print("\n2️⃣ Criando preferência de teste...")
    try:
        preference_data = {
            "items": [
                {
                    "title": "Teste de Integração",
                    "quantity": 1,
                    "unit_price": 10.00
                }
            ],
            "back_urls": {
                "success": "http://localhost:5173/payment/success",
                "failure": "http://localhost:5173/payment/failure",
                "pending": "http://localhost:5173/payment/pending"
            },
            "auto_return": "approved",
            "external_reference": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "notification_url": "http://localhost:8000/webhooks/mercadopago"
        }
        
        response = requests.post(
            f"{SANDBOX_CONFIG['api_url']}/checkout/preferences",
            headers=headers,
            json=preference_data
        )
        
        if response.status_code == 201:
            preference = response.json()
            preference_id = preference.get('id')
            print(f"✅ Preferência criada: {preference_id}")
            print(f"   URL de checkout: {preference.get('init_point')}")
            return preference_id
        else:
            print(f"❌ Erro ao criar preferência: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar preferência: {e}")
        return False

def test_frontend_integration(preference_id):
    """Testa a integração frontend"""
    print(f"\n3️⃣ Testando integração frontend...")
    print(f"   Preference ID: {preference_id}")
    print(f"   Public Key: {SANDBOX_CONFIG['public_key']}")
    
    # HTML de teste
    html_test = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Teste Mercado Pago</title>
    <script src="https://sdk.mercadopago.com/js/v2"></script>
</head>
<body>
    <h1>Teste de Integração Mercado Pago</h1>
    
    <div id="cho-container"></div>
    
    <script>
        const mp = new MercadoPago('{SANDBOX_CONFIG['public_key']}', {{
            locale: 'pt-BR'
        }});
        
        mp.checkout({{
            preference: {{
                id: '{preference_id}'
            }},
            render: {{
                container: '.cho-container',
                label: 'Pagar com Mercado Pago',
                type: 'button'
            }},
            callbacks: {{
                onSuccess: (data) => {{
                    console.log('✅ Pagamento aprovado:', data);
                    alert('Pagamento aprovado!');
                }},
                onError: (error) => {{
                    console.error('❌ Erro:', error);
                    alert('Erro no pagamento: ' + error.message);
                }},
                onCancel: () => {{
                    console.log('🚫 Cancelado');
                    alert('Pagamento cancelado');
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Salvar arquivo de teste
    with open("test_mercadopago.html", "w", encoding="utf-8") as f:
        f.write(html_test)
    
    print("✅ Arquivo de teste criado: test_mercadopago.html")
    print("   Abra o arquivo no navegador para testar")

if __name__ == "__main__":
    print("🚀 Iniciando testes de integração Mercado Pago...")
    
    # Testar integração
    preference_id = test_sandbox_integration()
    
    if preference_id:
        test_frontend_integration(preference_id)
        print("\n✅ Testes concluídos!")
        print("📝 Próximos passos:")
        print("   1. Configure as credenciais de sandbox no seu sistema")
        print("   2. Abra test_mercadopago.html no navegador")
        print("   3. Teste o fluxo de pagamento")
    else:
        print("\n❌ Testes falharam!")
        print("📝 Verifique:")
        print("   1. Credenciais de sandbox válidas")
        print("   2. Conexão com a internet")
        print("   3. Configuração da API") 