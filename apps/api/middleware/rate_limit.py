from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from typing import Dict, Tuple
import asyncio
from ..config.settings import settings

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.lock = asyncio.Lock()

    async def is_rate_limited(self, key: str) -> Tuple[bool, int]:
        """Verifica se uma requisição deve ser limitada"""
        async with self.lock:
            now = time.time()
            
            # Limpa requisições antigas
            if key in self.requests:
                self.requests[key] = [
                    req_time for req_time in self.requests[key]
                    if now - req_time < settings.RATE_LIMIT_PERIOD
                ]
            else:
                self.requests[key] = []

            # Verifica o limite
            if len(self.requests[key]) >= settings.RATE_LIMIT_REQUESTS:
                return True, len(self.requests[key])

            # Adiciona a requisição atual
            self.requests[key].append(now)
            return False, len(self.requests[key])

    async def get_remaining_requests(self, key: str) -> int:
        """Retorna o número de requisições restantes"""
        async with self.lock:
            if key not in self.requests:
                return settings.RATE_LIMIT_REQUESTS
            
            now = time.time()
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < settings.RATE_LIMIT_PERIOD
            ]
            
            return settings.RATE_LIMIT_REQUESTS - len(self.requests[key])

# Instância global do rate limiter
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Middleware para limitar a taxa de requisições"""
    # Obtém a chave do cliente (IP ou token)
    client_key = request.client.host
    
    # Verifica o limite
    is_limited, current_requests = await rate_limiter.is_rate_limited(client_key)
    
    if is_limited:
        remaining_time = settings.RATE_LIMIT_PERIOD - (
            time.time() - rate_limiter.requests[client_key][0]
        )
        
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests",
                "retry_after": int(remaining_time),
                "current_requests": current_requests,
                "limit": settings.RATE_LIMIT_REQUESTS
            },
            headers={
                "Retry-After": str(int(remaining_time)),
                "X-RateLimit-Limit": str(settings.RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + remaining_time))
            }
        )
    
    # Adiciona headers de rate limit
    response = await call_next(request)
    remaining = await rate_limiter.get_remaining_requests(client_key)
    
    response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + settings.RATE_LIMIT_PERIOD))
    
    return response 