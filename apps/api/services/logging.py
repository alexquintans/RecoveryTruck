import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import sys
import os
import threading

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.tracer = trace.get_tracer(__name__)
        self.service_name = os.getenv("SERVICE_NAME", "totem-api")
        self.environment = os.getenv("ENVIRONMENT", "development")

    def _format_log(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """Formata o log em estrutura JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "service": self.service_name,
            "environment": self.environment,
            **kwargs
        }
        
        # Adiciona trace_id se disponível
        current_span = trace.get_current_span()
        if current_span.is_recording():
            context = current_span.get_span_context()
            log_data.update({
                "trace_id": format(context.trace_id, "032x"),
                "span_id": format(context.span_id, "016x"),
                "trace_flags": format(context.trace_flags, "02x")
            })
        
        # Adiciona informações do sistema
        log_data.update({
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "pid": os.getpid(),
            "thread_id": threading.get_ident()
        })
        
        return log_data

    def _log_with_context(self, level: str, message: str, exc_info: Optional[Exception] = None, **kwargs):
        """Registra log com contexto"""
        log_data = self._format_log(level, message, **kwargs)
        
        if exc_info:
            log_data.update({
                "exception": str(exc_info),
                "exception_type": exc_info.__class__.__name__,
                "exception_module": exc_info.__class__.__module__
            })
            
            # Adiciona stack trace se disponível
            if hasattr(exc_info, "__traceback__"):
                import traceback
                log_data["stack_trace"] = traceback.format_tb(exc_info.__traceback__)
        
        # Registra o log
        log_message = json.dumps(log_data)
        if level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        elif level == "INFO":
            self.logger.info(log_message)
        elif level == "DEBUG":
            self.logger.debug(log_message)
        elif level == "CRITICAL":
            self.logger.critical(log_message)

    def info(self, message: str, **kwargs):
        """Log de nível INFO"""
        self._log_with_context("INFO", message, **kwargs)

    def error(self, message: str, exc_info: Optional[Exception] = None, **kwargs):
        """Log de nível ERROR"""
        self._log_with_context("ERROR", message, exc_info, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log de nível WARNING"""
        self._log_with_context("WARNING", message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log de nível DEBUG"""
        self._log_with_context("DEBUG", message, **kwargs)

    def critical(self, message: str, exc_info: Optional[Exception] = None, **kwargs):
        """Log de nível CRITICAL"""
        self._log_with_context("CRITICAL", message, exc_info, **kwargs)

    def with_span(self, name: str):
        """Decorator para adicionar span do OpenTelemetry"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(name) as span:
                    try:
                        # Adiciona atributos do span
                        span.set_attribute("service.name", self.service_name)
                        span.set_attribute("service.environment", self.environment)
                        
                        # Adiciona argumentos da função como atributos
                        for i, arg in enumerate(args):
                            span.set_attribute(f"arg.{i}", str(arg))
                        for key, value in kwargs.items():
                            span.set_attribute(f"arg.{key}", str(value))
                        
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR))
                        span.record_exception(e)
                        self.error(f"Error in {name}", exc_info=e)
                        raise
            return wrapper
        return decorator

def setup_logging():
    """Configura o logging da aplicação"""
    # Configura o formato do log
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Configura o OpenTelemetry
    trace.set_tracer_provider(TracerProvider())
    
    # Configura o exportador OTLP
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTLP_ENDPOINT", "localhost:4317"),
        insecure=os.getenv("OTLP_INSECURE", "true").lower() == "true"
    )
    
    # Adiciona o processador de spans
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(otlp_exporter)
    )

# Exemplo de uso:
# logger = StructuredLogger(__name__)
# 
# @logger.with_span("process_payment")
# async def process_payment(payment_id: str, amount: float):
#     logger.info("Starting payment processing", 
#                payment_id=payment_id, 
#                amount=amount)
#     try:
#         # ... código ...
#         logger.info("Payment processed successfully", 
#                    payment_id=payment_id, 
#                    status="success")
#     except Exception as e:
#         logger.error("Payment processing failed", 
#                     exc_info=e,
#                     payment_id=payment_id)
#         raise 