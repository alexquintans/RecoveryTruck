from typing import Dict, Type
from .adapters.base import PaymentAdapter
from .adapters.sicredi import SicrediAdapter
from .adapters.stone import StoneAdapter
from .adapters.pagseguro import PagSeguroAdapter
from .adapters.mercadopago import MercadoPagoAdapter
from .adapters.safrapay import SafraPayAdapter
from .adapters.pagbank import PagBankAdapter

class PaymentAdapterFactory:
    """Factory para criar adaptadores de pagamento."""
    
    _adapters: Dict[str, Type[PaymentAdapter]] = {
        "sicredi": SicrediAdapter,
        "stone": StoneAdapter,
        "pagseguro": PagSeguroAdapter,
        "mercadopago": MercadoPagoAdapter,
        "safrapay": SafraPayAdapter,
        "pagbank": PagBankAdapter
    }
    
    @classmethod
    def create_adapter(cls, adapter_name: str, config: Dict) -> PaymentAdapter:
        """Cria uma instância do adaptador especificado."""
        adapter_class = cls._adapters.get(adapter_name)
        if not adapter_class:
            raise ValueError(f"Adaptador não suportado: {adapter_name}")
            
        return adapter_class(config)
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[PaymentAdapter]) -> None:
        """Registra um novo adaptador."""
        cls._adapters[name] = adapter_class 