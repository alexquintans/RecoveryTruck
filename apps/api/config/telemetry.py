"""Configuração opcional de OpenTelemetry.
Se a biblioteca não estiver instalada, cria funções no-op para permitir execução sem rastreamento."""

try:
    from opentelemetry import trace  # type: ignore
    from opentelemetry.sdk.trace import TracerProvider  # type: ignore
    from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # type: ignore
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor  # type: ignore
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor  # type: ignore
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor  # type: ignore
    _OTEL_AVAILABLE = True
except ModuleNotFoundError:
    _OTEL_AVAILABLE = False

    class _NoOp:
        def __getattr__(self, _):
            def _noop(*args, **kwargs):
                return None
            return _noop

    trace = _NoOp()  # type: ignore
    TracerProvider = BatchSpanProcessor = OTLPSpanExporter = object  # type: ignore
    FastAPIInstrumentor = SQLAlchemyInstrumentor = HTTPXClientInstrumentor = _NoOp()  # type: ignore
    import warnings
    warnings.warn("Biblioteca 'opentelemetry' não instalada. Telemetria desativada.")

# Logger
import logging

logger = logging.getLogger(__name__)

def setup_telemetry(app):
    """Configura o OpenTelemetry para a aplicação"""
    if not _OTEL_AVAILABLE:
        logger.info("OpenTelemetry não disponível – inicialização ignorada")
        return

    try:
        # Configura o provedor de traces
        trace.set_tracer_provider(TracerProvider())
        
        # Configura o exportador OTLP
        otlp_exporter = OTLPSpanExporter(
            endpoint="localhost:4317",  # Endpoint do coletor OTLP
            insecure=True  # Em produção, usar TLS
        )
        
        # Adiciona o processador de spans
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrumenta o FastAPI
        FastAPIInstrumentor.instrument_app(app)
        
        # Instrumenta o SQLAlchemy
        SQLAlchemyInstrumentor().instrument()
        
        # Instrumenta o HTTPX
        HTTPXClientInstrumentor().instrument()
        
        logger.info("OpenTelemetry configured successfully")
    except Exception as e:
        logger.error(f"Error configuring OpenTelemetry: {str(e)}")
        raise 