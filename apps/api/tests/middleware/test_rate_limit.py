import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import time
from ...middleware.rate_limit import rate_limiter, rate_limit_middleware
from ...config.settings import settings

app = FastAPI()
app.middleware("http")(rate_limit_middleware)

@app.get("/test")
async def test_endpoint():
    return {"message": "success"}

client = TestClient(app)

def test_rate_limit_headers():
    """Testa se os headers de rate limit são retornados corretamente"""
    response = client.get("/test")
    
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers
    
    assert int(response.headers["X-RateLimit-Limit"]) == settings.RATE_LIMIT_REQUESTS
    assert int(response.headers["X-RateLimit-Remaining"]) == settings.RATE_LIMIT_REQUESTS - 1

def test_rate_limit_exceeded():
    """Testa se o rate limit é aplicado corretamente"""
    # Faz requisições até o limite
    for _ in range(settings.RATE_LIMIT_REQUESTS):
        response = client.get("/test")
        assert response.status_code == 200
    
    # Tenta fazer uma requisição além do limite
    response = client.get("/test")
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]
    assert "retry_after" in response.json()
    assert "current_requests" in response.json()
    assert "limit" in response.json()
    
    # Verifica os headers de erro
    assert "Retry-After" in response.headers
    assert response.headers["X-RateLimit-Remaining"] == "0"

def test_rate_limit_reset():
    """Testa se o rate limit é resetado após o período"""
    # Faz requisições até o limite
    for _ in range(settings.RATE_LIMIT_REQUESTS):
        client.get("/test")
    
    # Espera o período de reset
    time.sleep(settings.RATE_LIMIT_PERIOD + 1)
    
    # Tenta fazer uma nova requisição
    response = client.get("/test")
    assert response.status_code == 200
    assert int(response.headers["X-RateLimit-Remaining"]) == settings.RATE_LIMIT_REQUESTS - 1

def test_rate_limit_per_ip():
    """Testa se o rate limit é aplicado por IP"""
    # Faz requisições até o limite com um IP
    for _ in range(settings.RATE_LIMIT_REQUESTS):
        client.get("/test", headers={"X-Forwarded-For": "192.168.1.1"})
    
    # Tenta fazer uma requisição com outro IP
    response = client.get("/test", headers={"X-Forwarded-For": "192.168.1.2"})
    assert response.status_code == 200
    assert int(response.headers["X-RateLimit-Remaining"]) == settings.RATE_LIMIT_REQUESTS - 1

def test_rate_limit_cleanup():
    """Testa se as requisições antigas são limpas corretamente"""
    # Faz algumas requisições
    for _ in range(5):
        client.get("/test")
    
    # Espera um tempo
    time.sleep(settings.RATE_LIMIT_PERIOD + 1)
    
    # Faz mais requisições
    response = client.get("/test")
    assert response.status_code == 200
    assert int(response.headers["X-RateLimit-Remaining"]) == settings.RATE_LIMIT_REQUESTS - 1 