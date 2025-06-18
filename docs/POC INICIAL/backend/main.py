from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import json
from datetime import datetime
from pydantic import BaseModel
import random

app = FastAPI()

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento em memória para tickets e conexões WebSocket
tickets = {}
active_connections: List[WebSocket] = []

# Serviços disponíveis
SERVICES = {
    "banheira_gelo": {
        "id": "banheira_gelo",
        "name": "Banheira de Gelo",
        "price": 50.00,
        "duration": 10  # minutos
    },
    "bota_compressao": {
        "id": "bota_compressao",
        "name": "Bota de Compressão",
        "price": 30.00,
        "duration": 10  # minutos
    }
}

class Ticket(BaseModel):
    id: int
    service_id: str
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    terms_accepted: bool = False
    signature_data: Optional[str] = None

class PaymentRequest(BaseModel):
    payment_method: str

class TermsAcceptance(BaseModel):
    signature_data: str

@app.get("/services")
async def get_services():
    return list(SERVICES.values())

@app.post("/tickets")
async def create_ticket(service_id: str):
    if service_id not in SERVICES:
        raise HTTPException(status_code=400, detail="Serviço inválido")
    
    ticket_id = len(tickets) + 1
    ticket = Ticket(
        id=ticket_id,
        service_id=service_id,
        status="pending_terms",
        created_at=datetime.now()
    )
    tickets[ticket_id] = ticket
    return ticket

@app.post("/tickets/{ticket_id}/accept-terms")
async def accept_terms(ticket_id: int, terms: TermsAcceptance):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    ticket = tickets[ticket_id]
    if ticket.status != "pending_terms":
        raise HTTPException(status_code=400, detail="Termos já foram aceitos")
    
    ticket.terms_accepted = True
    ticket.signature_data = terms.signature_data
    ticket.status = "pending_payment"
    
    return ticket

@app.post("/tickets/{ticket_id}/pay")
async def pay_ticket(ticket_id: int, payment: PaymentRequest):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    ticket = tickets[ticket_id]
    if ticket.status != "pending_payment":
        raise HTTPException(status_code=400, detail="Ticket não está aguardando pagamento")
    
    if not ticket.terms_accepted:
        raise HTTPException(status_code=400, detail="Termos não foram aceitos")
    
    # Simula processamento do pagamento (80% de chance de sucesso)
    if random.random() < 0.8:
        ticket.status = "waiting"
        ticket.paid_at = datetime.now()
        ticket.payment_method = payment.payment_method
        
        # Notifica todos os clientes conectados
        await broadcast_ticket_update(ticket)
        return ticket
    else:
        raise HTTPException(status_code=400, detail="Falha no processamento do pagamento")

@app.get("/tickets")
async def get_tickets():
    return list(tickets.values())

@app.post("/tickets/{ticket_id}/start")
async def start_service(ticket_id: int):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    ticket = tickets[ticket_id]
    if ticket.status != "waiting":
        raise HTTPException(status_code=400, detail="Ticket não está aguardando atendimento")
    
    ticket.status = "in_progress"
    await broadcast_ticket_update(ticket)
    return ticket

@app.post("/tickets/{ticket_id}/end")
async def end_service(ticket_id: int):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket não encontrado")
    
    ticket = tickets[ticket_id]
    if ticket.status != "in_progress":
        raise HTTPException(status_code=400, detail="Ticket não está em atendimento")
    
    ticket.status = "completed"
    await broadcast_ticket_update(ticket)
    return ticket

@app.get("/report")
async def get_report():
    today = datetime.now().date()
    today_tickets = [
        t for t in tickets.values()
        if t.created_at.date() == today
    ]
    
    total = len(today_tickets)
    completed = len([t for t in today_tickets if t.status == "completed"])
    revenue = sum(
        SERVICES[t.service_id]["price"]
        for t in today_tickets
        if t.status in ["completed", "in_progress", "waiting"]
    )
    
    return {
        "date": today.isoformat(),
        "total_tickets": total,
        "completed_services": completed,
        "revenue": revenue
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Processa mensagens do WebSocket se necessário
    except:
        active_connections.remove(websocket)

async def broadcast_ticket_update(ticket: Ticket):
    message = {
        "type": "ticket_update",
        "ticket": {
            "id": ticket.id,
            "status": ticket.status,
            "service_id": ticket.service_id
        }
    }
    for connection in active_connections:
        try:
            await connection.send_text(json.dumps(message))
        except:
            active_connections.remove(connection)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 