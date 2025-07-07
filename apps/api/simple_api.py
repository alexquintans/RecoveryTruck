from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Totem API Simples", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "API funcionando!", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0", "timestamp": datetime.utcnow().isoformat()} 