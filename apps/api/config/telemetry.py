from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
import logging

logger = logging.getLogger(__name__)

def setup_telemetry(app):
    """Configura o OpenTelemetry para a aplicação"""
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