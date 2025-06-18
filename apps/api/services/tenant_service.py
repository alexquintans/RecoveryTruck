# 🏢 Serviço Completo de Gerenciamento de Tenants

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from apps.api.models.tenant import (
    Tenant, TenantPaymentLimits, TenantBusinessRules, 
    TenantFallbackConfig, TenantTerminalConfig
)
from apps.api.services.payment.factory import PaymentAdapterFactory

logger = logging.getLogger(__name__)

class TenantService:
    """🏢 Serviço completo para gerenciamento de tenants"""
    
    def __init__(self, db: Session):
        self.db = db
        logger.info("🏢 TenantService initialized")
    
    def create_tenant(
        self, 
        name: str, 
        cnpj: str, 
        payment_adapter: str = "sicredi",
        environment: str = "production",
        custom_configs: Optional[Dict[str, Any]] = None
    ) -> Tenant:
        """Cria um novo tenant com configurações completas"""
        
        logger.info(f"🆕 Creating tenant: {name} ({cnpj})")
        
        # Cria tenant com configurações padrão
        tenant = Tenant(
            name=name,
            cnpj=cnpj,
            payment_adapter=payment_adapter,
            environment=environment
        )
        
        # Aplica configurações customizadas se fornecidas
        if custom_configs:
            self._apply_custom_configs(tenant, custom_configs)
        
        # Valida configurações
        validation_errors = self.validate_tenant_config(tenant)
        if validation_errors:
            raise ValueError(f"Configuração inválida: {', '.join(validation_errors)}")
        
        # Salva no banco
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        
        logger.info(f"✅ Tenant created successfully: {tenant.id}")
        return tenant
    
    def _apply_custom_configs(self, tenant: Tenant, configs: Dict[str, Any]):
        """Aplica configurações customizadas ao tenant"""
        
        # Configurações de pagamento
        if "payment_config" in configs:
            tenant.payment_config = configs["payment_config"]
        
        # Configurações por modalidade
        if "payment_method_configs" in configs:
            for method, config in configs["payment_method_configs"].items():
                tenant.update_payment_method_config(method, config)
        
        # Limites de pagamento
        if "payment_limits" in configs:
            tenant.update_payment_limits(configs["payment_limits"])
        
        # Regras de negócio
        if "business_rules" in configs:
            tenant.update_business_rules(configs["business_rules"])
        
        # Configuração de fallback
        if "fallback_config" in configs:
            tenant.fallback_config = {**tenant.fallback_config, **configs["fallback_config"]}
        
        # Configuração de terminal
        if "terminal_config" in configs:
            tenant.terminal_config = {**tenant.terminal_config, **configs["terminal_config"]}
        
        # Configurações avançadas
        for key in ["webhook_config", "notification_config", "security_config"]:
            if key in configs:
                setattr(tenant, key, configs[key])
    
    def validate_tenant_config(self, tenant: Tenant) -> List[str]:
        """Valida configuração completa do tenant"""
        errors = []
        
        # Validação básica
        if not tenant.name or len(tenant.name) < 3:
            errors.append("Nome deve ter pelo menos 3 caracteres")
        
        if not tenant.cnpj or len(tenant.cnpj) != 14:
            errors.append("CNPJ deve ter 14 dígitos")
        
        # Validação do adaptador de pagamento
        if tenant.payment_adapter not in PaymentAdapterFactory._adapters:
            errors.append(f"Adaptador não suportado: {tenant.payment_adapter}")
        
        # Validação de limites
        limits_errors = self._validate_payment_limits(tenant.get_payment_limits())
        errors.extend(limits_errors)
        
        # Validação de configurações por modalidade
        method_errors = self._validate_payment_method_configs(tenant.payment_method_configs)
        errors.extend(method_errors)
        
        return errors
    
    def _validate_payment_limits(self, limits: TenantPaymentLimits) -> List[str]:
        """Valida limites de pagamento"""
        errors = []
        
        if limits.transaction_limit <= 0:
            errors.append("Limite de transação deve ser maior que zero")
        
        if limits.daily_limit < limits.transaction_limit:
            errors.append("Limite diário deve ser maior que limite de transação")
        
        if limits.monthly_limit < limits.daily_limit:
            errors.append("Limite mensal deve ser maior que limite diário")
        
        if limits.max_installments < 1 or limits.max_installments > 24:
            errors.append("Número máximo de parcelas deve estar entre 1 e 24")
        
        return errors
    
    def _validate_payment_method_configs(self, configs: Dict[str, Any]) -> List[str]:
        """Valida configurações por modalidade"""
        errors = []
        
        # Validação PIX
        if "pix" in configs:
            pix_config = configs["pix"]
            if pix_config.get("expiration_minutes", 0) <= 0:
                errors.append("Tempo de expiração PIX deve ser maior que zero")
            
            if pix_config.get("max_amount", 0) <= pix_config.get("min_amount", 0):
                errors.append("Valor máximo PIX deve ser maior que valor mínimo")
        
        # Validação Cartão de Crédito
        if "credit_card" in configs:
            cc_config = configs["credit_card"]
            if cc_config.get("max_installments", 0) <= 0:
                errors.append("Número máximo de parcelas deve ser maior que zero")
        
        # Validação Boleto
        if "boleto" in configs:
            boleto_config = configs["boleto"]
            if boleto_config.get("days_to_expire", 0) <= 0:
                errors.append("Dias para vencimento do boleto deve ser maior que zero")
        
        return errors
    
    def get_tenant_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Obtém tenant por ID"""
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
    
    def get_tenant_by_cnpj(self, cnpj: str) -> Optional[Tenant]:
        """Obtém tenant por CNPJ"""
        return self.db.query(Tenant).filter(Tenant.cnpj == cnpj).first()
    
    def get_active_tenants(self) -> List[Tenant]:
        """Obtém todos os tenants ativos"""
        return self.db.query(Tenant).filter(Tenant.is_active == True).all()
    
    def validate_transaction(
        self, 
        tenant_id: str, 
        amount: float, 
        payment_method: str,
        installments: int = 1,
        customer_cpf: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """Valida uma transação contra as regras do tenant"""
        
        tenant = self.get_tenant_by_id(tenant_id)
        if not tenant:
            return False, ["Tenant não encontrado"]
        
        if not tenant.is_active:
            return False, ["Tenant inativo"]
        
        if not tenant.can_process_payment(payment_method):
            return False, [f"Modalidade {payment_method} não disponível"]
        
        errors = []
        
        # Validação de limites
        limit_errors = tenant.validate_transaction_amount(amount, payment_method)
        errors.extend(limit_errors)
        
        # Validação de parcelamento
        if installments > 1:
            method_config = tenant.get_payment_method_config("credit_card")
            max_installments = method_config.get("max_installments", 1)
            min_amount = method_config.get("min_amount_for_installments", 0)
            
            if installments > max_installments:
                errors.append(f"Máximo de {max_installments} parcelas permitidas")
            
            if amount < min_amount:
                errors.append(f"Valor mínimo para parcelamento: R$ {min_amount:.2f}")
        
        # Validação CPF para PIX
        if payment_method == "pix":
            business_rules = tenant.get_business_rules()
            if business_rules.require_cpf_for_pix and not customer_cpf:
                errors.append("CPF obrigatório para pagamento PIX")
            
            if customer_cpf and business_rules.validate_cpf_format:
                if not self._validate_cpf(customer_cpf):
                    errors.append("CPF inválido")
        
        # Validação de saúde do tenant
        if tenant.health_status == "critical":
            errors.append("Sistema temporariamente indisponível")
        
        return len(errors) == 0, errors
    
    def _validate_cpf(self, cpf: str) -> bool:
        """Valida formato e dígitos verificadores do CPF"""
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Calcula primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Calcula segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verifica se os dígitos calculados conferem
        return cpf[9] == str(digito1) and cpf[10] == str(digito2)
    
    def update_transaction_metrics(self, tenant_id: str, amount: float, success: bool):
        """Atualiza métricas de transação do tenant"""
        tenant = self.get_tenant_by_id(tenant_id)
        if not tenant:
            return
        
        if success:
            tenant.update_transaction_metrics(amount)
        else:
            tenant.increment_error_count()
        
        self.db.commit()
    
    def perform_health_check(self, tenant_id: str) -> Dict[str, Any]:
        """Realiza verificação de saúde do tenant"""
        tenant = self.get_tenant_by_id(tenant_id)
        if not tenant:
            return {"status": "error", "message": "Tenant não encontrado"}
        
        health_data = {
            "tenant_id": tenant_id,
            "status": tenant.health_status,
            "last_check": datetime.now().isoformat(),
            "metrics": {
                "daily_transactions": tenant.daily_transaction_count,
                "daily_amount": float(tenant.daily_transaction_amount),
                "monthly_transactions": tenant.monthly_transaction_count,
                "monthly_amount": float(tenant.monthly_transaction_amount),
                "error_count_24h": tenant.error_count_24h
            },
            "adapters": {
                "primary": tenant.payment_adapter,
                "fallbacks": tenant.get_available_fallback_adapters()
            }
        }
        
        # Atualiza timestamp do health check
        tenant.update_health_status(tenant.health_status)
        self.db.commit()
        
        return health_data
