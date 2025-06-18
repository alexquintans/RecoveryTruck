# 🏭 Terminal Factory - Criação Dinâmica de Terminais

from typing import Dict, Any, Type
import logging

from .base import TerminalAdapter
from .mock_terminal import MockTerminalAdapter
from .stone_terminal import StoneTerminalAdapter
from .sicredi_terminal import SicrediTerminalAdapter
from .pagseguro_terminal import PagSeguroTerminalAdapter
from .mercadopago_terminal import MercadoPagoTerminalAdapter
from .safrapay_terminal import SafraPayTerminalAdapter
from .pagbank_terminal import PagBankTerminalAdapter

logger = logging.getLogger(__name__)

class TerminalFactory:
    """Factory para criação dinâmica de adaptadores de terminal"""
    
    # Registro de todos os terminais disponíveis
    TERMINAL_ADAPTERS: Dict[str, Type[TerminalAdapter]] = {
        "mock": MockTerminalAdapter,
        "stone": StoneTerminalAdapter,
        "sicredi": SicrediTerminalAdapter,
        "pagseguro": PagSeguroTerminalAdapter,
        "mercadopago": MercadoPagoTerminalAdapter,
        "safrapay": SafraPayTerminalAdapter,
        "pagbank": PagBankTerminalAdapter
    }
    
    @classmethod
    def create_terminal(cls, terminal_type: str, config: Dict[str, Any]) -> TerminalAdapter:
        """
        Cria uma instância do terminal especificado
        
        Args:
            terminal_type: Tipo do terminal (mock, stone, sicredi, pagseguro, mercadopago, safrapay, pagbank)
            config: Configuração do terminal
            
        Returns:
            Instância do adaptador de terminal
            
        Raises:
            ValueError: Se o tipo de terminal não for suportado
        """
        terminal_type = terminal_type.lower()
        
        if terminal_type not in cls.TERMINAL_ADAPTERS:
            available_types = ", ".join(cls.TERMINAL_ADAPTERS.keys())
            raise ValueError(
                f"Terminal type '{terminal_type}' not supported. "
                f"Available types: {available_types}"
            )
        
        adapter_class = cls.TERMINAL_ADAPTERS[terminal_type]
        
        logger.info(f"🏭 Creating {terminal_type} terminal adapter")
        
        try:
            return adapter_class(config)
        except Exception as e:
            logger.error(f"❌ Failed to create {terminal_type} terminal: {e}")
            raise
    
    @classmethod
    def get_available_terminals(cls) -> Dict[str, str]:
        """
        Retorna lista de terminais disponíveis com descrições
        
        Returns:
            Dicionário com tipo -> descrição
        """
        return {
            "mock": "🧪 Terminal Mock - Para testes e desenvolvimento",
            "stone": "💎 Stone Terminal - Integração completa com hardware Stone + PIX",
            "sicredi": "🏦 Sicredi Terminal - Integração nativa com maquininhas Sicredi + PIX",
            "pagseguro": "💳 PagSeguro Terminal - Suporte completo incluindo PIX",
            "mercadopago": "🏪 MercadoPago Terminal - Point com PIX avançado",
            "safrapay": "💰 SafraPay Terminal - Especializado em vouchers",
            "pagbank": "🏦 PagBank Terminal - Moderninha com PIX otimizado"
        }
    
    @classmethod
    def get_terminal_info(cls, terminal_type: str) -> Dict[str, Any]:
        """
        Retorna informações detalhadas sobre um tipo de terminal
        
        Args:
            terminal_type: Tipo do terminal
            
        Returns:
            Informações do terminal
        """
        terminal_type = terminal_type.lower()
        
        terminal_info = {
            "mock": {
                "name": "Terminal Mock",
                "description": "Terminal simulado para testes",
                "supported_methods": ["credit_card", "debit_card", "pix", "contactless", "voucher"],
                "connection_types": ["mock"],
                "features": ["deterministic_testing", "all_scenarios", "instant_response"],
                "use_cases": ["development", "testing", "demo"]
            },
            "stone": {
                "name": "Stone Terminal",
                "description": "Terminal Stone com integração física completa + PIX",
                "supported_methods": ["credit_card", "debit_card", "pix", "contactless"],
                "connection_types": ["serial", "tcp", "bluetooth"],
                "features": ["physical_integration", "receipt_printing", "robust_protocol", "pix_support", "qr_code_display"],
                "use_cases": ["production", "retail", "restaurants", "pix_payments"]
            },
            "sicredi": {
                "name": "Sicredi Terminal",
                "description": "Terminal Sicredi com protocolo nativo + PIX",
                "supported_methods": ["credit_card", "debit_card", "pix", "contactless", "voucher"],
                "connection_types": ["serial", "tcp", "bluetooth"],
                "features": ["native_protocol", "lrc_validation", "sicredi_specific", "pix_support", "qr_code_display"],
                "use_cases": ["sicredi_clients", "cooperatives", "agribusiness", "pix_payments"]
            },
            "pagseguro": {
                "name": "PagSeguro Terminal",
                "description": "Terminal PagSeguro com suporte completo a PIX",
                "supported_methods": ["credit_card", "debit_card", "pix", "contactless", "voucher"],
                "connection_types": ["serial", "tcp", "bluetooth"],
                "features": ["pix_support", "json_protocol", "high_speed"],
                "use_cases": ["e_commerce", "small_business", "pix_payments"]
            },
            "mercadopago": {
                "name": "MercadoPago Terminal",
                "description": "MercadoPago Point com PIX avançado",
                "supported_methods": ["credit_card", "debit_card", "pix", "contactless", "voucher"],
                "connection_types": ["serial", "tcp", "bluetooth", "usb"],
                "features": ["advanced_pix", "qr_code_generation", "mercadopago_ecosystem"],
                "use_cases": ["marketplace", "delivery", "mobile_payments"]
            },
            "safrapay": {
                "name": "SafraPay Terminal",
                "description": "Terminal SafraPay especializado em vouchers",
                "supported_methods": ["credit_card", "debit_card", "contactless", "voucher"],
                "connection_types": ["serial", "tcp", "bluetooth"],
                "features": ["voucher_specialist", "checksum_validation", "safra_protocol"],
                "use_cases": ["corporate", "voucher_payments", "safra_clients"]
            },
            "pagbank": {
                "name": "PagBank Terminal",
                "description": "PagBank Moderninha com PIX otimizado",
                "supported_methods": ["credit_card", "debit_card", "pix", "contactless", "voucher"],
                "connection_types": ["serial", "tcp", "bluetooth", "usb"],
                "features": ["optimized_pix", "auth_hash", "moderninha_integration"],
                "use_cases": ["modern_retail", "pix_focused", "pagbank_clients"]
            }
        }
        
        return terminal_info.get(terminal_type, {})
    
    @classmethod
    def validate_config(cls, terminal_type: str, config: Dict[str, Any]) -> bool:
        """
        Valida configuração para um tipo de terminal
        
        Args:
            terminal_type: Tipo do terminal
            config: Configuração a ser validada
            
        Returns:
            True se configuração é válida
        """
        terminal_type = terminal_type.lower()
        
        if terminal_type not in cls.TERMINAL_ADAPTERS:
            return False
        
        # Validações básicas
        required_fields = {
            "mock": [],
            "stone": ["stone.merchant_id", "stone.terminal_id"],
            "sicredi": ["sicredi.merchant_id", "sicredi.terminal_id"],
            "pagseguro": ["pagseguro.merchant_id", "pagseguro.terminal_id", "pagseguro.api_key"],
            "mercadopago": ["mercadopago.access_token", "mercadopago.user_id", "mercadopago.pos_id"],
            "safrapay": ["safrapay.merchant_id", "safrapay.terminal_id", "safrapay.establishment_code"],
            "pagbank": ["pagbank.merchant_id", "pagbank.terminal_id", "pagbank.access_token"]
        }
        
        # 🆕 Validações PIX opcionais para Stone e Sicredi
        pix_fields = {
            "stone": ["stone.pix.pix_key"],
            "sicredi": ["sicredi.pix.pix_key"]
        }
        
        fields_to_check = required_fields.get(terminal_type, [])
        
        for field in fields_to_check:
            keys = field.split('.')
            current = config
            
            try:
                for key in keys:
                    current = current[key]
                
                if not current:
                    logger.warning(f"⚠️ Missing required field: {field}")
                    return False
                    
            except (KeyError, TypeError):
                logger.warning(f"⚠️ Missing required field: {field}")
                return False
        
        # 🆕 Valida configurações PIX se presentes
        if terminal_type in pix_fields:
            pix_config = config.get(terminal_type, {}).get("pix", {})
            if pix_config:
                pix_key = pix_config.get("pix_key")
                if pix_key:
                    logger.info(f"✅ PIX configuration found for {terminal_type}")
                else:
                    logger.warning(f"⚠️ PIX config present but missing pix_key for {terminal_type}")
        
        return True
    
    @classmethod
    def create_default_config(cls, terminal_type: str) -> Dict[str, Any]:
        """
        Cria configuração padrão para um tipo de terminal
        
        Args:
            terminal_type: Tipo do terminal
            
        Returns:
            Configuração padrão
        """
        terminal_type = terminal_type.lower()
        
        default_configs = {
            "mock": {
                "connection_type": "mock",
                "timeout": 30,
                "retry_attempts": 3
            },
            "stone": {
                "connection_type": "serial",
                "port": "COM1",
                "baudrate": 9600,
                "timeout": 30,
                "retry_attempts": 3,
                "stone": {
                    "merchant_id": "STONE_MERCHANT_ID",
                    "terminal_id": "STONE_TERMINAL_ID"
                }
            },
            "sicredi": {
                "connection_type": "serial",
                "port": "COM1",
                "baudrate": 9600,
                "timeout": 30,
                "retry_attempts": 3,
                "sicredi": {
                    "merchant_id": "SICREDI_MERCHANT_ID",
                    "terminal_id": "SICREDI_TERMINAL_ID",
                    "pos_id": "SICREDI_POS_ID"
                }
            },
            "pagseguro": {
                "connection_type": "serial",
                "port": "COM1",
                "baudrate": 115200,
                "timeout": 30,
                "retry_attempts": 3,
                "pagseguro": {
                    "merchant_id": "PAGSEGURO_MERCHANT_ID",
                    "terminal_id": "PAGSEGURO_TERMINAL_ID",
                    "api_key": "PAGSEGURO_API_KEY"
                }
            },
            "mercadopago": {
                "connection_type": "usb",
                "timeout": 30,
                "retry_attempts": 3,
                "mercadopago": {
                    "access_token": "MERCADOPAGO_ACCESS_TOKEN",
                    "user_id": "MERCADOPAGO_USER_ID",
                    "pos_id": "MERCADOPAGO_POS_ID",
                    "store_id": "MERCADOPAGO_STORE_ID"
                }
            },
            "safrapay": {
                "connection_type": "serial",
                "port": "COM1",
                "baudrate": 9600,
                "timeout": 30,
                "retry_attempts": 3,
                "safrapay": {
                    "merchant_id": "SAFRAPAY_MERCHANT_ID",
                    "terminal_id": "SAFRAPAY_TERMINAL_ID",
                    "establishment_code": "SAFRAPAY_ESTABLISHMENT_CODE",
                    "api_key": "SAFRAPAY_API_KEY"
                }
            },
            "pagbank": {
                "connection_type": "usb",
                "timeout": 30,
                "retry_attempts": 3,
                "pagbank": {
                    "merchant_id": "PAGBANK_MERCHANT_ID",
                    "terminal_id": "PAGBANK_TERMINAL_ID",
                    "establishment_id": "PAGBANK_ESTABLISHMENT_ID",
                    "access_token": "PAGBANK_ACCESS_TOKEN"
                }
            }
        }
        
        return default_configs.get(terminal_type, {})
    
    @classmethod
    def get_connection_types(cls, terminal_type: str) -> list:
        """
        Retorna tipos de conexão suportados por um terminal
        
        Args:
            terminal_type: Tipo do terminal
            
        Returns:
            Lista de tipos de conexão suportados
        """
        connection_types = {
            "mock": ["mock"],
            "stone": ["serial", "tcp", "bluetooth"],
            "sicredi": ["serial", "tcp", "bluetooth"],
            "pagseguro": ["serial", "tcp", "bluetooth"],
            "mercadopago": ["serial", "tcp", "bluetooth", "usb"],
            "safrapay": ["serial", "tcp", "bluetooth"],
            "pagbank": ["serial", "tcp", "bluetooth", "usb"]
        }
        
        return connection_types.get(terminal_type.lower(), [])
    
    @classmethod
    def get_supported_methods(cls, terminal_type: str) -> list:
        """
        Retorna métodos de pagamento suportados por um terminal
        
        Args:
            terminal_type: Tipo do terminal
            
        Returns:
            Lista de métodos de pagamento suportados
        """
        supported_methods = {
            "mock": ["credit_card", "debit_card", "pix", "contactless", "voucher"],
            "stone": ["credit_card", "debit_card", "contactless"],
            "sicredi": ["credit_card", "debit_card", "contactless", "voucher"],
            "pagseguro": ["credit_card", "debit_card", "pix", "contactless", "voucher"],
            "mercadopago": ["credit_card", "debit_card", "pix", "contactless", "voucher"],
            "safrapay": ["credit_card", "debit_card", "contactless", "voucher"],
            "pagbank": ["credit_card", "debit_card", "pix", "contactless", "voucher"]
        }
        
        return supported_methods.get(terminal_type.lower(), []) 