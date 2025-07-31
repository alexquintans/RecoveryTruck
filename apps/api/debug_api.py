from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Debug API is working!", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/debug")
async def debug():
    import os
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