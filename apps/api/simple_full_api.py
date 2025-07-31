from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI(
    title="🏪 Sistema de Totem - API Simplificada",
    description="API para sistema de autoatendimento",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API is working!", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/test")
async def test():
    return {"message": "Test endpoint working!", "timestamp": datetime.utcnow().isoformat()}

@app.get("/debug")
async def debug():
    return {
        "message": "Debug info",
        "timestamp": datetime.utcnow().isoformat(),
        "env_vars": {
            "DATABASE_URL": "SET" if os.getenv("DATABASE_URL") else "NOT_SET",
            "JWT_SECRET": "SET" if os.getenv("JWT_SECRET") else "NOT_SET",
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT_SET"),
            "PORT": os.getenv("PORT", "NOT_SET")
        }
    } 