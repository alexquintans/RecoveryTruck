from typing import Any, Callable, Optional
import asyncio
from datetime import datetime, timedelta
import logging
from functools import wraps
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        half_open_timeout: int = 30
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
        self.last_success_time: Optional[datetime] = None
        self.total_requests = 0
        self.failed_requests = 0

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executa a função com o padrão Circuit Breaker"""
        self.total_requests += 1
        
        with tracer.start_as_current_span(f"circuit_breaker.{self.name}") as span:
            span.set_attribute("circuit_breaker.state", self.state)
            span.set_attribute("circuit_breaker.failures", self.failures)
            
            if self.state == "open":
                if self.last_failure_time and \
                   datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.reset_timeout):
                    self.state = "half-open"
                    logger.info(f"Circuit breaker '{self.name}' is now half-open after {self.reset_timeout}s timeout")
                    span.set_attribute("circuit_breaker.state", "half-open")
                else:
                    logger.warning(f"Circuit breaker '{self.name}' is open, request rejected")
                    span.set_attribute("circuit_breaker.rejected", True)
                    raise Exception(f"Circuit breaker '{self.name}' is open")

            try:
                result = await func(*args, **kwargs)
                
                if self.state == "half-open":
                    self.state = "closed"
                    self.failures = 0
                    logger.info(f"Circuit breaker '{self.name}' is now closed after successful half-open test")
                    span.set_attribute("circuit_breaker.state", "closed")
                
                self.last_success_time = datetime.utcnow()
                span.set_attribute("circuit_breaker.success", True)
                return result

            except Exception as e:
                self.failures += 1
                self.failed_requests += 1
                self.last_failure_time = datetime.utcnow()
                
                span.set_attribute("circuit_breaker.error", str(e))
                span.set_attribute("circuit_breaker.error_type", type(e).__name__)
                
                if self.failures >= self.failure_threshold:
                    self.state = "open"
                    logger.error(
                        f"Circuit breaker '{self.name}' is now open after {self.failures} failures. "
                        f"Last error: {str(e)}"
                    )
                    span.set_attribute("circuit_breaker.state", "open")
                
                raise e

    def get_metrics(self) -> dict:
        """Retorna métricas do circuit breaker"""
        return {
            "name": self.name,
            "state": self.state,
            "failures": self.failures,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "failure_rate": self.failed_requests / self.total_requests if self.total_requests > 0 else 0,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None
        }

class Retry:
    def __init__(
        self,
        name: str,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        self.name = name
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
        self.exceptions = exceptions
        self.total_retries = 0
        self.failed_retries = 0

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Executa a função com o padrão Retry"""
        last_exception = None
        
        with tracer.start_as_current_span(f"retry.{self.name}") as span:
            span.set_attribute("retry.max_attempts", self.max_attempts)
            
            for attempt in range(self.max_attempts):
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("retry.attempt", attempt + 1)
                    span.set_attribute("retry.success", True)
                    return result
                except self.exceptions as e:
                    last_exception = e
                    self.total_retries += 1
                    
                    span.set_attribute("retry.attempt", attempt + 1)
                    span.set_attribute("retry.error", str(e))
                    span.set_attribute("retry.error_type", type(e).__name__)
                    
                    if attempt == self.max_attempts - 1:
                        self.failed_retries += 1
                        logger.error(
                            f"Retry '{self.name}' failed after {self.max_attempts} attempts. "
                            f"Last error: {str(e)}"
                        )
                        break
                    
                    wait_time = self.delay * (self.backoff ** attempt)
                    logger.warning(
                        f"Retry '{self.name}' attempt {attempt + 1} failed, "
                        f"retrying in {wait_time:.2f} seconds. Error: {str(e)}"
                    )
                    await asyncio.sleep(wait_time)
            
            raise last_exception

    def get_metrics(self) -> dict:
        """Retorna métricas do retry"""
        return {
            "name": self.name,
            "total_retries": self.total_retries,
            "failed_retries": self.failed_retries,
            "success_rate": (self.total_retries - self.failed_retries) / self.total_retries if self.total_retries > 0 else 0
        }

def with_resilience(
    circuit_breaker: Optional[CircuitBreaker] = None,
    retry: Optional[Retry] = None
):
    """Decorator para adicionar resiliência a uma função"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(f"resilience.{func.__name__}") as span:
                try:
                    if circuit_breaker and retry:
                        result = await retry.execute(
                            lambda: circuit_breaker.execute(func, *args, **kwargs)
                        )
                    elif circuit_breaker:
                        result = await circuit_breaker.execute(func, *args, **kwargs)
                    elif retry:
                        result = await retry.execute(func, *args, **kwargs)
                    else:
                        result = await func(*args, **kwargs)
                    
                    span.set_attribute("resilience.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("resilience.error", str(e))
                    span.set_attribute("resilience.error_type", type(e).__name__)
                    raise
        return wrapper
    return decorator

# Exemplo de uso:
# @with_resilience(
#     circuit_breaker=CircuitBreaker("payment_api", failure_threshold=5),
#     retry=Retry("payment_api", max_attempts=3)
# )
# async def process_payment():
#     pass 