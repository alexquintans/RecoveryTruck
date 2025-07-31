import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram
import logging

logger = logging.getLogger(__name__)

# Métricas Prometheus
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP',
    ['method', 'endpoint']
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para capturar métricas de requisições HTTP"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Capturar informações da requisição
        method = request.method
        endpoint = request.url.path
        
        try:
            # Processar a requisição
            response = await call_next(request)
            
            # Calcular duração
            duration = time.time() - start_time
            
            # Registrar métricas
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=str(response.status_code)
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # Log de requisições bem-sucedidas (apenas para debug)
            if response.status_code >= 400:
                logger.warning(
                    f"Request {method} {endpoint} returned {response.status_code} "
                    f"in {duration:.3f}s"
                )
            else:
                logger.debug(
                    f"Request {method} {endpoint} completed in {duration:.3f}s"
                )
            
            return response
            
        except Exception as e:
            # Calcular duração mesmo em caso de erro
            duration = time.time() - start_time
            
            # Registrar métricas de erro
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status="500"
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # Log do erro
            logger.error(
                f"Request {method} {endpoint} failed after {duration:.3f}s: {str(e)}",
                exc_info=e
            )
            
            raise 