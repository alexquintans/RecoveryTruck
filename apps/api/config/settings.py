from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Any
import os
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore", env_file=".env")
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/totem")
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # OpenTelemetry
    OTLP_ENDPOINT: str = os.getenv("OTLP_ENDPOINT", "localhost:4317")
    OTLP_INSECURE: bool = os.getenv("OTLP_INSECURE", "True").lower() == "true"
    
    # Printer
    PRINTER_TYPE: str = os.getenv("PRINTER_TYPE", "usb")
    # Converte valores que podem vir como hexadecimal (ex.: 0x0483)
    def _parse_int(value: str) -> int:
        try:
            return int(value, 0)  # base 0 permite 0x (hex), 0o (octal), etc.
        except ValueError:
            return int(value)

    PRINTER_VENDOR_ID: int = _parse_int(os.getenv("PRINTER_VENDOR_ID", "0x0483"))
    PRINTER_PRODUCT_ID: int = _parse_int(os.getenv("PRINTER_PRODUCT_ID", "0x5740"))
    
    # Payment Processors
    STONE_API_URL: str = os.getenv("STONE_API_URL", "https://api.stone.com.br/v1")
    STONE_API_KEY: str = os.getenv("STONE_API_KEY", "")
    STONE_MERCHANT_ID: str = os.getenv("STONE_MERCHANT_ID", "")
    
    PAGSEGURO_API_URL: str = os.getenv("PAGSEGURO_API_URL", "https://ws.pagseguro.uol.com.br/v2")
    PAGSEGURO_API_KEY: str = os.getenv("PAGSEGURO_API_KEY", "")
    PAGSEGURO_MERCHANT_ID: str = os.getenv("PAGSEGURO_MERCHANT_ID", "")
    
    MERCADOPAGO_API_URL: str = os.getenv("MERCADOPAGO_API_URL", "https://api.mercadopago.com/v1")
    MERCADOPAGO_ACCESS_TOKEN: str = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Security
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    def cors_origin_list(self) -> List[str]:
        """Retorna lista de origens a partir da string"""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # em segundos

settings = Settings() 