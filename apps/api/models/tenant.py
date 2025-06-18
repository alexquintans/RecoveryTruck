from sqlalchemy import Column, String, JSON, Boolean, DateTime, Float, Integer, Text
from sqlalchemy.sql import func
from uuid import uuid4
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json

from database import Base

@dataclass
class TenantPaymentLimits:
    """Limites de pagamento por tenant"""
    # Limites gerais
    daily_limit: float = 50000.0
    monthly_limit: float = 1000000.0
    transaction_limit: float = 10000.0
    
    # Limites por modalidade
    credit_card_limit: float = 10000.0
    debit_card_limit: float = 5000.0
    pix_limit: float = 50000.0
    contactless_limit: float = 200.0
    voucher_limit: float = 1000.0
    boleto_limit: float = 50000.0
    
    # Limites de parcelamento
    max_installments: int = 12
    min_amount_installments: float = 50.0

@dataclass
class TenantBusinessRules:
    """Regras de negócio por tenant"""
    # Validações obrigatórias
    require_cpf_for_pix: bool = True
    require_cpf_for_voucher: bool = True
    validate_cpf_format: bool = True
    
    # Configurações de timeout
    payment_timeout_minutes: int = 30
    pix_timeout_minutes: int = 15
    
    # Configurações de retry
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 5
    
    # Configurações de impressão
    auto_print_receipt: bool = True
    print_customer_copy: bool = True
    print_merchant_copy: bool = True
    
    # Configurações de notificação
    send_sms_confirmation: bool = False
    send_email_confirmation: bool = False

@dataclass
class TenantFallbackConfig:
    """Configuração de fallback e redundância"""
    # Adaptadores de fallback em ordem de prioridade
    fallback_adapters: List[str] = field(default_factory=lambda: ["stone", "pagseguro"])
    
    # Configurações de failover
    enable_auto_failover: bool = True
    failover_timeout_seconds: int = 30
    max_failover_attempts: int = 2
    
    # Configurações de health check
    health_check_interval_seconds: int = 60
    health_check_timeout_seconds: int = 10
    
    # Configurações de circuit breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout_seconds: int = 300

@dataclass
class TenantTerminalConfig:
    """Configuração específica de terminais físicos"""
    # Terminal principal
    primary_terminal_type: str = "sicredi"
    primary_terminal_config: Dict[str, Any] = field(default_factory=dict)
    
    # Terminais de backup
    backup_terminals: List[Dict[str, Any]] = field(default_factory=list)
    
    # Configurações de conexão
    connection_timeout_seconds: int = 30
    reconnection_attempts: int = 3
    reconnection_delay_seconds: int = 5
    
    # Configurações de monitoramento
    enable_terminal_monitoring: bool = True
    monitoring_interval_seconds: int = 30

class Tenant(Base):
    """🏢 Modelo COMPLETO para tenants com configurações avançadas"""
    
    __tablename__ = "tenants"
    
    # === Identificação ===
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    cnpj = Column(String(14), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # === Configurações de Pagamento Básicas ===
    payment_adapter = Column(String(50), default="sicredi")  # Adaptador principal
    payment_config = Column(JSON, default=dict)  # Configurações específicas do adaptador
    
    # 🆕 === Configurações Específicas por Modalidade ===
    payment_method_configs = Column(JSON, default=dict)  # Configurações detalhadas por modalidade
    
    # 🆕 === Limites e Regras de Negócio ===
    payment_limits = Column(JSON, default=dict)  # Limites de transação
    business_rules = Column(JSON, default=dict)  # Regras de negócio
    
    # 🆕 === Fallbacks e Redundância ===
    fallback_config = Column(JSON, default=dict)  # Configuração de fallback
    backup_adapters = Column(JSON, default=list)  # Lista de adaptadores de backup
    
    # 🆕 === Configurações de Terminal Físico ===
    terminal_config = Column(JSON, default=dict)  # Configuração de terminais físicos
    
    # 🆕 === Configurações Avançadas ===
    webhook_config = Column(JSON, default=dict)  # Configurações de webhook
    notification_config = Column(JSON, default=dict)  # Configurações de notificação
    security_config = Column(JSON, default=dict)  # Configurações de segurança
    
    # 🆕 === Métricas e Monitoramento ===
    daily_transaction_count = Column(Integer, default=0)
    daily_transaction_amount = Column(Float, default=0.0)
    monthly_transaction_count = Column(Integer, default=0)
    monthly_transaction_amount = Column(Float, default=0.0)
    last_transaction_at = Column(DateTime(timezone=True))
    
    # 🆕 === Status e Saúde ===
    health_status = Column(String(20), default="healthy")  # healthy, warning, critical
    last_health_check = Column(DateTime(timezone=True))
    error_count_24h = Column(Integer, default=0)
    
    # 🆕 === Configurações de Ambiente ===
    environment = Column(String(20), default="production")  # production, staging, development
    debug_mode = Column(Boolean, default=False)
    log_level = Column(String(10), default="INFO")
    
    # === Timestamps ===
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Inicializa configurações padrão se não fornecidas
        if not self.payment_method_configs:
            self.payment_method_configs = self._get_default_payment_method_configs()
        
        if not self.payment_limits:
            self.payment_limits = TenantPaymentLimits().__dict__
        
        if not self.business_rules:
            self.business_rules = TenantBusinessRules().__dict__
        
        if not self.fallback_config:
            self.fallback_config = TenantFallbackConfig().__dict__
        
        if not self.terminal_config:
            self.terminal_config = TenantTerminalConfig().__dict__
    
    def _get_default_payment_method_configs(self) -> Dict[str, Any]:
        """🆕 Configurações padrão por modalidade de pagamento"""
        return {
            "credit_card": {
                "max_installments": 12,
                "min_amount_for_installments": 50.0,
                "brands_accepted": ["visa", "mastercard", "elo", "amex"],
                "allow_contactless": True,
                "require_signature_above": 50.0
            },
            "debit_card": {
                "require_password": True,
                "max_amount": 5000.0,
                "allow_contactless": True,
                "contactless_limit": 200.0
            },
            "pix": {
                "require_cpf_validation": True,
                "expiration_minutes": 30,
                "allow_change": False,
                "min_amount": 0.01,
                "max_amount": 50000.0,
                "auto_confirm": True,
                "qr_code_format": "base64"
            },
            "contactless": {
                "max_amount": 200.0,
                "require_pin_above": 50.0,
                "supported_technologies": ["nfc", "rfid"]
            },
            "voucher": {
                "types_accepted": ["meal", "food", "fuel"],
                "require_cpf": True,
                "max_amount": 1000.0,
                "validate_balance": True
            },
            "boleto": {
                "days_to_expire": 3,
                "fine_percentage": 2.0,
                "interest_per_day": 0.033,
                "min_amount": 5.0,
                "max_amount": 10000.0,
                "allow_discount": True
            }
        }
    
    # 🆕 === Métodos de Configuração ===
    
    def get_payment_method_config(self, payment_method: str) -> Dict[str, Any]:
        """Obtém configuração específica de uma modalidade"""
        return self.payment_method_configs.get(payment_method, {})
    
    def update_payment_method_config(self, payment_method: str, config: Dict[str, Any]):
        """Atualiza configuração de uma modalidade"""
        if not self.payment_method_configs:
            self.payment_method_configs = {}
        
        self.payment_method_configs[payment_method] = {
            **self.payment_method_configs.get(payment_method, {}),
            **config
        }
    
    def get_payment_limits(self) -> TenantPaymentLimits:
        """Obtém limites de pagamento"""
        return TenantPaymentLimits(**self.payment_limits)
    
    def update_payment_limits(self, limits: Dict[str, Any]):
        """Atualiza limites de pagamento"""
        self.payment_limits = {**self.payment_limits, **limits}
    
    def get_business_rules(self) -> TenantBusinessRules:
        """Obtém regras de negócio"""
        return TenantBusinessRules(**self.business_rules)
    
    def update_business_rules(self, rules: Dict[str, Any]):
        """Atualiza regras de negócio"""
        self.business_rules = {**self.business_rules, **rules}
    
    def get_fallback_config(self) -> TenantFallbackConfig:
        """Obtém configuração de fallback"""
        return TenantFallbackConfig(**self.fallback_config)
    
    def get_terminal_config(self) -> TenantTerminalConfig:
        """Obtém configuração de terminal"""
        return TenantTerminalConfig(**self.terminal_config)
    
    # 🆕 === Métodos de Validação ===
    
    def validate_transaction_amount(self, amount: float, payment_method: str) -> List[str]:
        """Valida valor da transação contra limites configurados"""
        errors = []
        limits = self.get_payment_limits()
        
        # Validação geral
        if amount > limits.transaction_limit:
            errors.append(f"Valor excede limite de transação: R$ {limits.transaction_limit:.2f}")
        
        # Validação por modalidade
        method_limits = {
            "credit_card": limits.credit_card_limit,
            "debit_card": limits.debit_card_limit,
            "pix": limits.pix_limit,
            "contactless": limits.contactless_limit,
            "voucher": limits.voucher_limit,
            "boleto": limits.boleto_limit
        }
        
        method_limit = method_limits.get(payment_method)
        if method_limit and amount > method_limit:
            errors.append(f"Valor excede limite para {payment_method}: R$ {method_limit:.2f}")
        
        return errors
    
    def can_process_payment(self, payment_method: str) -> bool:
        """Verifica se pode processar pagamento com a modalidade"""
        if not self.is_active:
            return False
        
        if self.health_status == "critical":
            return False
        
        method_config = self.get_payment_method_config(payment_method)
        return bool(method_config)
    
    def get_available_fallback_adapters(self) -> List[str]:
        """Obtém lista de adaptadores de fallback disponíveis"""
        fallback_config = self.get_fallback_config()
        if not fallback_config.enable_auto_failover:
            return []
        
        return fallback_config.fallback_adapters
    
    # 🆕 === Métodos de Monitoramento ===
    
    def update_transaction_metrics(self, amount: float):
        """Atualiza métricas de transação"""
        self.daily_transaction_count += 1
        self.daily_transaction_amount += amount
        self.monthly_transaction_count += 1
        self.monthly_transaction_amount += amount
        self.last_transaction_at = func.now()
    
    def increment_error_count(self):
        """Incrementa contador de erros"""
        self.error_count_24h += 1
        
        # Atualiza status de saúde baseado em erros
        if self.error_count_24h > 50:
            self.health_status = "critical"
        elif self.error_count_24h > 20:
            self.health_status = "warning"
    
    def reset_daily_metrics(self):
        """Reseta métricas diárias"""
        self.daily_transaction_count = 0
        self.daily_transaction_amount = 0.0
        self.error_count_24h = 0
        self.health_status = "healthy"
    
    def update_health_status(self, status: str):
        """Atualiza status de saúde"""
        self.health_status = status
        self.last_health_check = func.now()
    
    # 🆕 === Métodos de Configuração Avançada ===
    
    def enable_debug_mode(self):
        """Habilita modo debug"""
        self.debug_mode = True
        self.log_level = "DEBUG"
    
    def disable_debug_mode(self):
        """Desabilita modo debug"""
        self.debug_mode = False
        self.log_level = "INFO"
    
    def set_environment(self, environment: str):
        """Define ambiente (production, staging, development)"""
        if environment in ["production", "staging", "development"]:
            self.environment = environment
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização"""
        return {
            "id": self.id,
            "name": self.name,
            "cnpj": self.cnpj,
            "is_active": self.is_active,
            "payment_adapter": self.payment_adapter,
            "payment_config": self.payment_config,
            "payment_method_configs": self.payment_method_configs,
            "payment_limits": self.payment_limits,
            "business_rules": self.business_rules,
            "fallback_config": self.fallback_config,
            "terminal_config": self.terminal_config,
            "health_status": self.health_status,
            "environment": self.environment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, adapter={self.payment_adapter}, status={self.health_status})>" 