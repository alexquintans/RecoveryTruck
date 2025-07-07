from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import asyncio

# Configuração simples para desenvolvimento Docker
app = FastAPI(
    title="Totem API",
    description="API para sistema de autoatendimento com pagamento integrado",
    version="0.2.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens para desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.2.0",
        "message": "Totem API funcionando!",
        "environment": "docker-development"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Totem API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    ) 