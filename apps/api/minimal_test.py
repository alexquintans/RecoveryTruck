from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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

@app.websocket("/ws-test")
async def websocket_test(websocket: WebSocket):
    """Endpoint WebSocket de teste mínimo"""
    print(f"🔍 DEBUG - Teste WebSocket recebido")
    print(f"🔍 DEBUG - Headers: {websocket.headers}")
    print(f"🔍 DEBUG - URL: {websocket.url}")
    print(f"🔍 DEBUG - Client: {websocket.client}")
    
    try:
        await websocket.accept()
        print(f"🔍 DEBUG - Teste WebSocket aceito com sucesso!")
        
        while True:
            data = await websocket.receive_text()
            print(f"🔍 DEBUG - Teste recebeu: {data}")
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print(f"🔍 DEBUG - Teste desconectado")
    except Exception as e:
        print(f"🔍 DEBUG - Teste erro: {e}")
        import traceback
        traceback.print_exc()

@app.get("/")
async def root():
    return {"message": "Minimal WebSocket Test API"}

@app.get("/health")
async def health():
    return {"status": "healthy"} 