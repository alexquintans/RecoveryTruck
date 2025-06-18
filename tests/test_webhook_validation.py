# 🧪 Teste Completo do Sistema de Validação de Webhooks

import asyncio
import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from apps.api.services.webhook_validator import (
    WebhookValidator, WebhookProvider, WebhookValidationConfig,
    SignatureAlgorithm, get_sicredi_config, get_stone_config,
    get_pagseguro_config, get_mercadopago_config, get_safrapay_config,
    get_pagbank_config
)

class WebhookTester:
    """🧪 Testador completo de webhooks"""
    
    def __init__(self):
        self.validator = WebhookValidator()
        self.test_secrets = {
            "sicredi": "test_secret_sicredi_123",
            "stone": "test_secret_stone_456",
            "pagseguro": "test_secret_pagseguro_789",
            "mercadopago": "test_secret_mercadopago_abc",
            "safrapay": "test_secret_safrapay_def",
            "pagbank": "test_secret_pagbank_ghi"
        }
        
    def setup_test_configs(self):
        """Configura validadores para teste"""
        
        # Registra todos os provedores
        self.validator.register_provider(get_sicredi_config(self.test_secrets["sicredi"]))
        self.validator.register_provider(get_stone_config(self.test_secrets["stone"]))
        self.validator.register_provider(get_pagseguro_config(self.test_secrets["pagseguro"]))
        self.validator.register_provider(get_mercadopago_config(self.test_secrets["mercadopago"]))
        self.validator.register_provider(get_safrapay_config(self.test_secrets["safrapay"]))
        self.validator.register_provider(get_pagbank_config(self.test_secrets["pagbank"]))
        
        print("🔐 Test configurations registered")
    
    def generate_test_signature(self, payload: str, secret: str, algorithm: str = "sha256") -> str:
        """Gera assinatura de teste"""
        
        if algorithm == "sha256":
            return hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
        elif algorithm == "sha1":
            return hmac.new(
                secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha1
            ).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def create_test_payload(self, provider: str, transaction_id: str = None) -> Dict[str, Any]:
        """Cria payload de teste específico por provedor"""
        
        base_payload = {
            "id": transaction_id or f"txn_{provider}_{int(time.time())}",
            "amount": 9999,  # R$ 99.99
            "status": "approved",
            "timestamp": datetime.now().isoformat()
        }
        
        if provider == "sicredi":
            return {
                **base_payload,
                "merchant_id": "SICREDI_MERCHANT_123",
                "payment_method": "credit_card"
            }
        
        elif provider == "stone":
            return {
                "transaction": {
                    **base_payload,
                    "merchant_id": "STONE_MERCHANT_456"
                },
                "event": "transaction.approved"
            }
        
        elif provider == "pagseguro":
            return {
                **base_payload,
                "notificationCode": f"PS_{transaction_id or 'test'}",
                "notificationType": "transaction"
            }
        
        elif provider == "mercadopago":
            return {
                "action": "payment.updated",
                "data": {
                    "id": base_payload["id"]
                },
                **base_payload
            }
        
        elif provider == "safrapay":
            return {
                **base_payload,
                "payment_id": base_payload["id"],
                "merchant_id": "SAFRA_MERCHANT_789"
            }
        
        elif provider == "pagbank":
            return {
                **base_payload,
                "charges": [
                    {
                        "id": base_payload["id"],
                        "amount": base_payload["amount"],
                        "status": base_payload["status"]
                    }
                ]
            }
        
        return base_payload
    
    def create_test_headers(self, provider: str, payload: str, valid: bool = True) -> Dict[str, str]:
        """Cria headers de teste"""
        
        config = self.validator._configs[WebhookProvider(provider)]
        secret = self.test_secrets[provider]
        
        headers = {}
        
        # Timestamp
        if config.timestamp_header:
            headers[config.timestamp_header] = str(int(time.time()))
        
        # Signature
        if valid:
            if config.algorithm == SignatureAlgorithm.HMAC_SHA256:
                signature = self.generate_test_signature(payload, secret, "sha256")
            elif config.algorithm == SignatureAlgorithm.HMAC_SHA1:
                signature = self.generate_test_signature(payload, secret, "sha1")
            else:
                signature = "valid_signature"
        else:
            signature = "invalid_signature"
        
        # Adiciona prefixo se necessário
        if config.signature_prefix:
            signature = config.signature_prefix + signature
        
        headers[config.signature_header] = signature
        
        return headers
    
    async def test_valid_webhook(self, provider: str) -> bool:
        """Testa webhook válido"""
        
        print(f"\n🧪 Testing valid webhook: {provider}")
        
        try:
            # Cria payload e headers válidos
            payload_data = self.create_test_payload(provider)
            payload_str = json.dumps(payload_data, separators=(',', ':'), sort_keys=True)
            headers = self.create_test_headers(provider, payload_str, valid=True)
            
            # Valida webhook
            result = self.validator.validate_webhook(
                provider=WebhookProvider(provider),
                payload=payload_str,
                headers=headers,
                client_ip="127.0.0.1"
            )
            
            if result.is_valid:
                print(f"   ✅ Valid webhook test passed")
                print(f"   📋 Transaction ID: {result.transaction_id}")
                print(f"   📋 Event Type: {result.event_type}")
                return True
            else:
                print(f"   ❌ Valid webhook test failed")
                for error in result.errors:
                    print(f"      - {error}")
                return False
                
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False
    
    async def test_invalid_signature(self, provider: str) -> bool:
        """Testa webhook com assinatura inválida"""
        
        print(f"\n🧪 Testing invalid signature: {provider}")
        
        try:
            # Cria payload válido mas headers inválidos
            payload_data = self.create_test_payload(provider)
            payload_str = json.dumps(payload_data, separators=(',', ':'), sort_keys=True)
            headers = self.create_test_headers(provider, payload_str, valid=False)
            
            # Valida webhook
            result = self.validator.validate_webhook(
                provider=WebhookProvider(provider),
                payload=payload_str,
                headers=headers,
                client_ip="127.0.0.1"
            )
            
            if not result.is_valid and "Signature mismatch" in result.errors:
                print(f"   ✅ Invalid signature test passed")
                return True
            else:
                print(f"   ❌ Invalid signature test failed - should have been rejected")
                return False
                
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False
    
    async def test_replay_attack(self, provider: str) -> bool:
        """Testa proteção contra replay attack"""
        
        print(f"\n🧪 Testing replay attack protection: {provider}")
        
        try:
            # Cria payload e headers válidos
            payload_data = self.create_test_payload(provider, "replay_test_txn")
            payload_str = json.dumps(payload_data, separators=(',', ':'), sort_keys=True)
            headers = self.create_test_headers(provider, payload_str, valid=True)
            
            # Primeira validação - deve passar
            result1 = self.validator.validate_webhook(
                provider=WebhookProvider(provider),
                payload=payload_str,
                headers=headers,
                client_ip="127.0.0.1"
            )
            
            # Segunda validação - deve falhar (replay)
            result2 = self.validator.validate_webhook(
                provider=WebhookProvider(provider),
                payload=payload_str,
                headers=headers,
                client_ip="127.0.0.1"
            )
            
            if result1.is_valid and not result2.is_valid and "Replay attack detected" in result2.errors:
                print(f"   ✅ Replay attack protection test passed")
                return True
            else:
                print(f"   ❌ Replay attack protection test failed")
                print(f"      First result: {result1.is_valid}")
                print(f"      Second result: {result2.is_valid}")
                return False
                
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False
    
    async def test_timestamp_validation(self, provider: str) -> bool:
        """Testa validação de timestamp"""
        
        print(f"\n🧪 Testing timestamp validation: {provider}")
        
        config = self.validator._configs[WebhookProvider(provider)]
        
        if not config.require_timestamp:
            print(f"   ⏭️ Timestamp not required for {provider}")
            return True
        
        try:
            # Cria payload válido
            payload_data = self.create_test_payload(provider)
            payload_str = json.dumps(payload_data, separators=(',', ':'), sort_keys=True)
            
            # Headers com timestamp muito antigo
            headers = self.create_test_headers(provider, payload_str, valid=True)
            old_timestamp = int(time.time()) - 600  # 10 minutos atrás
            headers[config.timestamp_header] = str(old_timestamp)
            
            # Valida webhook
            result = self.validator.validate_webhook(
                provider=WebhookProvider(provider),
                payload=payload_str,
                headers=headers,
                client_ip="127.0.0.1"
            )
            
            if not result.is_valid and any("Timestamp too old" in error for error in result.errors):
                print(f"   ✅ Timestamp validation test passed")
                return True
            else:
                print(f"   ❌ Timestamp validation test failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False
    
    async def test_provider_specific_validation(self, provider: str) -> bool:
        """Testa validações específicas do provedor"""
        
        print(f"\n🧪 Testing provider-specific validation: {provider}")
        
        try:
            # Cria payload com campos faltando
            payload_data = {"incomplete": "data"}
            payload_str = json.dumps(payload_data, separators=(',', ':'), sort_keys=True)
            headers = self.create_test_headers(provider, payload_str, valid=True)
            
            # Valida webhook
            result = self.validator.validate_webhook(
                provider=WebhookProvider(provider),
                payload=payload_str,
                headers=headers,
                client_ip="127.0.0.1"
            )
            
            # Deve passar na validação geral mas ter warnings específicos
            if result.is_valid and len(result.warnings) > 0:
                print(f"   ✅ Provider-specific validation test passed")
                print(f"   ⚠️ Warnings: {len(result.warnings)}")
                for warning in result.warnings:
                    print(f"      - {warning}")
                return True
            else:
                print(f"   ❌ Provider-specific validation test failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        
        print("🚀 INICIANDO TESTES DO SISTEMA DE VALIDAÇÃO DE WEBHOOKS")
        print("=" * 60)
        
        # Setup
        self.setup_test_configs()
        
        providers = ["sicredi", "stone", "pagseguro", "mercadopago", "safrapay", "pagbank"]
        
        total_tests = 0
        passed_tests = 0
        
        for provider in providers:
            print(f"\n🔍 TESTANDO PROVEDOR: {provider.upper()}")
            print("-" * 40)
            
            # Testes para cada provedor
            tests = [
                self.test_valid_webhook(provider),
                self.test_invalid_signature(provider),
                self.test_replay_attack(provider),
                self.test_timestamp_validation(provider),
                self.test_provider_specific_validation(provider)
            ]
            
            for test in tests:
                total_tests += 1
                if await test:
                    passed_tests += 1
        
        # Resultado final
        print("\n" + "=" * 60)
        print("📊 RESULTADO DOS TESTES")
        print("=" * 60)
        print(f"✅ Testes aprovados: {passed_tests}")
        print(f"❌ Testes falharam: {total_tests - passed_tests}")
        print(f"📈 Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 TODOS OS TESTES PASSARAM! Sistema de webhooks funcionando perfeitamente!")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} testes falharam. Verifique os logs acima.")
        
        return passed_tests == total_tests

async def main():
    """Função principal de teste"""
    
    tester = WebhookTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Sistema de validação de webhooks está funcionando corretamente!")
    else:
        print("\n❌ Problemas encontrados no sistema de validação de webhooks!")

if __name__ == "__main__":
    asyncio.run(main()) 