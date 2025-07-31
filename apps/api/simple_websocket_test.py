from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f"🔍 DEBUG - WebSocket recebido")
    await websocket.accept()
    print(f"🔍 DEBUG - WebSocket aceito!")
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"🔍 DEBUG - Mensagem recebida: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"🔍 DEBUG - Erro: {e}")

@app.get("/health")
async def health_check():
    return {"status": "ok"} 