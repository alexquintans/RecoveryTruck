#!/usr/bin/env python3
"""
Teste simples para verificar se o endpoint de customers está funcionando
"""

import requests
import json

def test_customers_endpoint():
    """Testa o endpoint de customers"""
    base_url = "https://recoverytruck-production.up.railway.app"
    
    # Teste 1: Endpoint de health (deve funcionar)
    print("🔍 Testando endpoint de health...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.status_code}")
    except Exception as e:
        print(f"❌ Health: {e}")
    
    # Teste 2: Endpoint de customers/search (deve funcionar)
    print("\n🔍 Testando endpoint de customers/search...")
    try:
        response = requests.get(
            f"{base_url}/customers/search",
            params={
                "q": "12345678901",
                "tenant_id": "7f02a566-2406-436d-b10d-90ecddd3fe2d"
            }
        )
        print(f"✅ Customers/search: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Customers/search: {e}")
    
    # Teste 3: Endpoint de tickets/queue/public (deve funcionar)
    print("\n🔍 Testando endpoint de tickets/queue/public...")
    try:
        response = requests.get(
            f"{base_url}/tickets/queue/public",
            params={"tenant_id": "7f02a566-2406-436d-b10d-90ecddd3fe2d"}
        )
        print(f"✅ Tickets/queue/public: {response.status_code}")
    except Exception as e:
        print(f"❌ Tickets/queue/public: {e}")

if __name__ == "__main__":
    test_customers_endpoint() 