# 🔐 Serviço Completo de Validação de Webhooks

import hmac
import hashlib
import json
import time
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import base64
import re
from urllib.parse import parse_qs, unquote

logger = logging.getLogger(__name__)

class WebhookProvider(Enum):
    """Provedores de webhook suportados"""
    SICREDI = "sicredi"
    STONE = "stone"
    PAGSEGURO = "pagseguro"
    MERCADOPAGO = "mercadopago"
    SAFRAPAY = "safrapay"
    PAGBANK = "pagbank"

class SignatureAlgorithm(Enum):
    """Algoritmos de assinatura suportados"""
    HMAC_SHA256 = "hmac_sha256"
    HMAC_SHA1 = "hmac_sha1"
    RSA_SHA256 = "rsa_sha256"
    JWT = "jwt"

@dataclass
class WebhookValidationConfig:
    """Configuração de validação de webhook"""
    provider: WebhookProvider
    secret_key: str
    algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA256
    
    # Configurações de segurança
    max_timestamp_diff: int = 300  # 5 minutos
    require_timestamp: bool = True
    allow_replay: bool = False
    
    # Configurações específicas do provedor
    signature_header: str = "X-Signature"
    timestamp_header: Optional[str] = "X-Timestamp"
    signature_prefix: Optional[str] = None  # Ex: "sha256="
    
    # Configurações de payload
    encoding: str = "utf-8"
    normalize_payload: bool = True
    include_headers: List[str] = field(default_factory=list)
    
    # Configurações de IP
    allowed_ips: List[str] = field(default_factory=list)
    ip_header: str = "X-Forwarded-For"

@dataclass
class WebhookValidationResult:
    """Resultado da validação de webhook"""
    is_valid: bool
    provider: WebhookProvider
    transaction_id: Optional[str] = None
    event_type: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    # Detalhes da validação
    signature_valid: bool = False
    timestamp_valid: bool = True
    ip_valid: bool = True
    replay_check_passed: bool = True
    
    # Erros
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class WebhookReplayProtection:
    """🛡️ Proteção contra replay attacks"""
    
    def __init__(self, max_age: int = 300):
        self.max_age = max_age
        self._processed_webhooks: Dict[str, datetime] = {}
    
    def is_replay(self, webhook_id: str, timestamp: datetime) -> bool:
        """Verifica se é um replay attack"""
        
        # Limpa webhooks antigos
        self._cleanup_old_webhooks()
        
        # Verifica se já foi processado
        if webhook_id in self._processed_webhooks:
            logger.warning(f"🚨 Replay attack detected: {webhook_id}")
            return True
        
        # Registra webhook
        self._processed_webhooks[webhook_id] = timestamp
        return False
    
    def _cleanup_old_webhooks(self):
        """Remove webhooks antigos do cache"""
        cutoff = datetime.now() - timedelta(seconds=self.max_age)
        
        old_webhooks = [
            webhook_id for webhook_id, timestamp in self._processed_webhooks.items()
            if timestamp < cutoff
        ]
        
        for webhook_id in old_webhooks:
            del self._processed_webhooks[webhook_id]

class WebhookValidator:
    """🔐 Validador completo de webhooks"""
    
    def __init__(self):
        self._configs: Dict[WebhookProvider, WebhookValidationConfig] = {}
        self._replay_protection = WebhookReplayProtection()
        logger.info("🔐 WebhookValidator initialized")
    
    def register_provider(self, config: WebhookValidationConfig):
        """Registra configuração de um provedor"""
        self._configs[config.provider] = config
        logger.info(f"🔐 Provider registered: {config.provider.value}")
    
    def validate_webhook(
        self,
        provider: WebhookProvider,
        payload: Union[str, bytes, Dict[str, Any]],
        headers: Dict[str, str],
        client_ip: Optional[str] = None
    ) -> WebhookValidationResult:
        """🔍 Valida webhook completo"""
        
        result = WebhookValidationResult(
            is_valid=False,
            provider=provider
        )
        
        try:
            # Verifica se provedor está configurado
            if provider not in self._configs:
                result.errors.append(f"Provider {provider.value} not configured")
                return result
            
            config = self._configs[provider]
            
            # 1. Validação de IP
            if not self._validate_ip(client_ip, config, result):
                return result
            
            # 2. Extração de dados do payload
            payload_data, payload_str = self._normalize_payload(payload, config)
            
            # 3. Extração de metadados
            self._extract_metadata(payload_data, result)
            
            # 4. Validação de timestamp
            if not self._validate_timestamp(headers, config, result):
                return result
            
            # 5. Validação de assinatura
            if not self._validate_signature(payload_str, headers, config, result):
                return result
            
            # 6. Proteção contra replay
            if not self._validate_replay(payload_data, result, config):
                return result
            
            # 7. Validações específicas do provedor
            self._provider_specific_validation(payload_data, config, result)
            
            result.is_valid = True
            logger.info(f"✅ Webhook validated successfully: {provider.value}")
            
        except Exception as e:
            logger.error(f"❌ Webhook validation error: {e}")
            result.errors.append(f"Validation error: {str(e)}")
        
        return result
    
    def _validate_ip(
        self,
        client_ip: Optional[str],
        config: WebhookValidationConfig,
        result: WebhookValidationResult
    ) -> bool:
        """Valida IP do cliente"""
        
        if not config.allowed_ips:
            return True  # Sem restrição de IP
        
        if not client_ip:
            result.errors.append("Client IP not provided")
            result.ip_valid = False
            return False
        
        # Remove porta se presente
        ip_clean = client_ip.split(':')[0]
        
        if ip_clean not in config.allowed_ips:
            result.errors.append(f"IP not allowed: {ip_clean}")
            result.ip_valid = False
            logger.warning(f"🚨 Unauthorized IP: {ip_clean}")
            return False
        
        result.ip_valid = True
        return True
    
    def _normalize_payload(
        self,
        payload: Union[str, bytes, Dict[str, Any]],
        config: WebhookValidationConfig
    ) -> Tuple[Dict[str, Any], str]:
        """Normaliza payload para validação"""
        
        # Converte para string se necessário
        if isinstance(payload, bytes):
            payload_str = payload.decode(config.encoding)
        elif isinstance(payload, dict):
            payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        else:
            payload_str = str(payload)
        
        # Parse para dict se for JSON
        try:
            if isinstance(payload, (str, bytes)):
                payload_data = json.loads(payload_str)
            else:
                payload_data = payload
        except json.JSONDecodeError:
            payload_data = {"raw": payload_str}
        
        return payload_data, payload_str
    
    def _extract_metadata(
        self,
        payload_data: Dict[str, Any],
        result: WebhookValidationResult
    ):
        """Extrai metadados do payload"""
        
        # ID da transação (varia por provedor)
        transaction_fields = ["id", "transaction_id", "payment_id", "order_id"]
        for field in transaction_fields:
            if field in payload_data:
                result.transaction_id = str(payload_data[field])
                break
        
        # Tipo de evento
        event_fields = ["type", "event", "event_type", "action"]
        for field in event_fields:
            if field in payload_data:
                result.event_type = str(payload_data[field])
                break
    
    def _validate_timestamp(
        self,
        headers: Dict[str, str],
        config: WebhookValidationConfig,
        result: WebhookValidationResult
    ) -> bool:
        """Valida timestamp do webhook"""
        
        if not config.require_timestamp:
            return True
        
        timestamp_header = config.timestamp_header
        if not timestamp_header or timestamp_header not in headers:
            if config.require_timestamp:
                result.errors.append("Timestamp header missing")
                result.timestamp_valid = False
                return False
            return True
        
        try:
            timestamp_str = headers[timestamp_header]
            
            # Tenta diferentes formatos de timestamp
            timestamp = self._parse_timestamp(timestamp_str)
            result.timestamp = timestamp
            
            # Verifica se não é muito antigo ou futuro
            now = datetime.now()
            diff = abs((now - timestamp).total_seconds())
            
            if diff > config.max_timestamp_diff:
                result.errors.append(f"Timestamp too old/future: {diff}s")
                result.timestamp_valid = False
                return False
            
            result.timestamp_valid = True
            return True
            
        except Exception as e:
            result.errors.append(f"Invalid timestamp: {e}")
            result.timestamp_valid = False
            return False
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp em diferentes formatos"""
        
        # Unix timestamp
        if timestamp_str.isdigit():
            return datetime.fromtimestamp(int(timestamp_str))
        
        # ISO format
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            pass
        
        # RFC 2822
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(timestamp_str)
        except:
            pass
        
        raise ValueError(f"Unsupported timestamp format: {timestamp_str}")
    
    def _validate_signature(
        self,
        payload_str: str,
        headers: Dict[str, str],
        config: WebhookValidationConfig,
        result: WebhookValidationResult
    ) -> bool:
        """Valida assinatura do webhook"""
        
        signature_header = config.signature_header
        if signature_header not in headers:
            result.errors.append(f"Signature header missing: {signature_header}")
            result.signature_valid = False
            return False
        
        received_signature = headers[signature_header]
        
        # Remove prefixo se configurado
        if config.signature_prefix:
            if not received_signature.startswith(config.signature_prefix):
                result.errors.append(f"Invalid signature prefix")
                result.signature_valid = False
                return False
            received_signature = received_signature[len(config.signature_prefix):]
        
        # Calcula assinatura esperada
        expected_signature = self._calculate_signature(payload_str, config, headers)
        
        # Compara assinaturas
        if not hmac.compare_digest(received_signature, expected_signature):
            result.errors.append("Signature mismatch")
            result.signature_valid = False
            logger.warning(f"🚨 Signature mismatch for {config.provider.value}")
            return False
        
        result.signature_valid = True
        return True
    
    def _calculate_signature(
        self,
        payload_str: str,
        config: WebhookValidationConfig,
        headers: Dict[str, str]
    ) -> str:
        """Calcula assinatura baseada no algoritmo configurado"""
        
        if config.algorithm == SignatureAlgorithm.HMAC_SHA256:
            return self._hmac_signature(payload_str, config.secret_key, hashlib.sha256)
        
        elif config.algorithm == SignatureAlgorithm.HMAC_SHA1:
            return self._hmac_signature(payload_str, config.secret_key, hashlib.sha1)
        
        else:
            raise ValueError(f"Unsupported algorithm: {config.algorithm}")
    
    def _hmac_signature(self, payload: str, secret: str, hash_func) -> str:
        """Calcula assinatura HMAC"""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hash_func
        ).hexdigest()
        return signature
    
    def _validate_replay(
        self,
        payload_data: Dict[str, Any],
        result: WebhookValidationResult,
        config: WebhookValidationConfig
    ) -> bool:
        """Valida proteção contra replay"""
        
        if config.allow_replay:
            return True
        
        # Gera ID único do webhook
        webhook_id = self._generate_webhook_id(payload_data, result)
        
        if self._replay_protection.is_replay(webhook_id, result.timestamp or datetime.now()):
            result.errors.append("Replay attack detected")
            result.replay_check_passed = False
            return False
        
        result.replay_check_passed = True
        return True
    
    def _generate_webhook_id(
        self,
        payload_data: Dict[str, Any],
        result: WebhookValidationResult
    ) -> str:
        """Gera ID único para o webhook"""
        
        # Usa transaction_id + timestamp + event_type
        components = [
            result.transaction_id or "unknown",
            str(result.timestamp or datetime.now()),
            result.event_type or "unknown"
        ]
        
        webhook_id = "|".join(components)
        return hashlib.sha256(webhook_id.encode()).hexdigest()[:16]
    
    def _provider_specific_validation(
        self,
        payload_data: Dict[str, Any],
        config: WebhookValidationConfig,
        result: WebhookValidationResult
    ):
        """Validações específicas por provedor"""
        
        if config.provider == WebhookProvider.SICREDI:
            self._validate_sicredi(payload_data, result)
        
        elif config.provider == WebhookProvider.STONE:
            self._validate_stone(payload_data, result)
        
        elif config.provider == WebhookProvider.PAGSEGURO:
            self._validate_pagseguro(payload_data, result)
        
        elif config.provider == WebhookProvider.MERCADOPAGO:
            self._validate_mercadopago(payload_data, result)
        
        elif config.provider == WebhookProvider.SAFRAPAY:
            self._validate_safrapay(payload_data, result)
        
        elif config.provider == WebhookProvider.PAGBANK:
            self._validate_pagbank(payload_data, result)
    
    def _validate_sicredi(self, payload_data: Dict[str, Any], result: WebhookValidationResult):
        """Validações específicas do Sicredi"""
        
        # Verifica campos obrigatórios
        required_fields = ["id", "status", "amount"]
        for field in required_fields:
            if field not in payload_data:
                result.warnings.append(f"Sicredi: Missing field {field}")
        
        # Valida status
        valid_statuses = ["approved", "pending", "failed", "cancelled"]
        status = payload_data.get("status")
        if status and status not in valid_statuses:
            result.warnings.append(f"Sicredi: Invalid status {status}")
    
    def _validate_stone(self, payload_data: Dict[str, Any], result: WebhookValidationResult):
        """Validações específicas do Stone"""
        
        # Verifica estrutura do Stone
        if "transaction" in payload_data:
            transaction = payload_data["transaction"]
            if not isinstance(transaction, dict):
                result.warnings.append("Stone: Invalid transaction structure")
        
        # Valida eventos do Stone
        valid_events = ["transaction.approved", "transaction.failed", "transaction.cancelled"]
        event_type = result.event_type
        if event_type and event_type not in valid_events:
            result.warnings.append(f"Stone: Unknown event type {event_type}")
    
    def _validate_pagseguro(self, payload_data: Dict[str, Any], result: WebhookValidationResult):
        """Validações específicas do PagSeguro"""
        
        # Verifica notificationCode
        if "notificationCode" not in payload_data:
            result.warnings.append("PagSeguro: Missing notificationCode")
        
        # Verifica notificationType
        valid_types = ["transaction", "preApproval"]
        notification_type = payload_data.get("notificationType")
        if notification_type and notification_type not in valid_types:
            result.warnings.append(f"PagSeguro: Invalid notification type {notification_type}")
    
    def _validate_mercadopago(self, payload_data: Dict[str, Any], result: WebhookValidationResult):
        """Validações específicas do MercadoPago"""
        
        # Verifica action
        valid_actions = ["payment.created", "payment.updated"]
        action = payload_data.get("action")
        if action and action not in valid_actions:
            result.warnings.append(f"MercadoPago: Unknown action {action}")
        
        # Verifica data_id
        if "data" in payload_data and "id" not in payload_data["data"]:
            result.warnings.append("MercadoPago: Missing data.id")
    
    def _validate_safrapay(self, payload_data: Dict[str, Any], result: WebhookValidationResult):
        """Validações específicas do SafraPay"""
        
        # Validações específicas do SafraPay
        if "payment_id" not in payload_data:
            result.warnings.append("SafraPay: Missing payment_id")
    
    def _validate_pagbank(self, payload_data: Dict[str, Any], result: WebhookValidationResult):
        """Validações específicas do PagBank"""
        
        # Validações específicas do PagBank
        if "charges" in payload_data:
            charges = payload_data["charges"]
            if not isinstance(charges, list):
                result.warnings.append("PagBank: Invalid charges structure")

# === Configurações Pré-definidas por Provedor ===

def get_sicredi_config(secret_key: str) -> WebhookValidationConfig:
    """Configuração padrão para Sicredi"""
    return WebhookValidationConfig(
        provider=WebhookProvider.SICREDI,
        secret_key=secret_key,
        algorithm=SignatureAlgorithm.HMAC_SHA256,
        signature_header="X-Sicredi-Signature",
        timestamp_header="X-Sicredi-Timestamp",
        signature_prefix="sha256=",
        max_timestamp_diff=300,
        require_timestamp=True,
        allow_replay=False
    )

def get_stone_config(secret_key: str) -> WebhookValidationConfig:
    """Configuração padrão para Stone"""
    return WebhookValidationConfig(
        provider=WebhookProvider.STONE,
        secret_key=secret_key,
        algorithm=SignatureAlgorithm.HMAC_SHA256,
        signature_header="X-Stone-Signature",
        timestamp_header="X-Stone-Timestamp",
        signature_prefix="sha256=",
        max_timestamp_diff=600,
        require_timestamp=True,
        allow_replay=False
    )

def get_pagseguro_config(secret_key: str) -> WebhookValidationConfig:
    """Configuração padrão para PagSeguro"""
    return WebhookValidationConfig(
        provider=WebhookProvider.PAGSEGURO,
        secret_key=secret_key,
        algorithm=SignatureAlgorithm.HMAC_SHA1,
        signature_header="X-PagSeguro-Signature",
        signature_prefix="",
        max_timestamp_diff=300,
        require_timestamp=False,
        allow_replay=False
    )

def get_mercadopago_config(secret_key: str) -> WebhookValidationConfig:
    """Configuração padrão para MercadoPago"""
    return WebhookValidationConfig(
        provider=WebhookProvider.MERCADOPAGO,
        secret_key=secret_key,
        algorithm=SignatureAlgorithm.HMAC_SHA256,
        signature_header="X-Signature",
        timestamp_header="X-Request-Id",
        max_timestamp_diff=600,
        require_timestamp=False,
        allow_replay=False
    )

def get_safrapay_config(secret_key: str) -> WebhookValidationConfig:
    """Configuração padrão para SafraPay"""
    return WebhookValidationConfig(
        provider=WebhookProvider.SAFRAPAY,
        secret_key=secret_key,
        algorithm=SignatureAlgorithm.HMAC_SHA256,
        signature_header="X-SafraPay-Signature",
        timestamp_header="X-SafraPay-Timestamp",
        signature_prefix="sha256=",
        max_timestamp_diff=300,
        require_timestamp=True,
        allow_replay=False
    )

def get_pagbank_config(secret_key: str) -> WebhookValidationConfig:
    """Configuração padrão para PagBank"""
    return WebhookValidationConfig(
        provider=WebhookProvider.PAGBANK,
        secret_key=secret_key,
        algorithm=SignatureAlgorithm.HMAC_SHA256,
        signature_header="X-PagBank-Signature",
        timestamp_header="X-PagBank-Timestamp",
        signature_prefix="sha256=",
        max_timestamp_diff=300,
        require_timestamp=True,
        allow_replay=False
    )

# === Instância Global ===
webhook_validator = WebhookValidator()