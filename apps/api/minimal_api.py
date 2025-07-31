from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is working!", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/test")
async def test():
    return {"message": "Test endpoint working!", "timestamp": datetime.utcnow().isoformat()} 