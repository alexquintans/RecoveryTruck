from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from database import get_db
from models import Ticket, Service, Payment, Consent
from schemas import TicketCreate, Ticket as TicketSchema, TicketList
from auth import get_current_operator
from security import encrypt_data

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"]
)

@router.post("", response_model=TicketSchema)
async def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Create new ticket."""
    # Verify service exists and belongs to tenant
    service = db.query(Service).filter(
        Service.id == ticket.service_id,
        Service.tenant_id == current_operator.tenant_id,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Get next ticket number
    last_ticket = db.query(Ticket).filter(
        Ticket.tenant_id == current_operator.tenant_id
    ).order_by(Ticket.ticket_number.desc()).first()
    
    ticket_number = 1 if not last_ticket else last_ticket.ticket_number + 1
    
    # Create ticket
    db_ticket = Ticket(
        tenant_id=current_operator.tenant_id,
        service_id=ticket.service_id,
        ticket_number=ticket_number,
        status="pending",
        customer_name=ticket.customer_name,
        customer_cpf=encrypt_data(ticket.customer_cpf),  # Encrypt sensitive data
        customer_phone=ticket.customer_phone,
        consent_version=ticket.consent_version
    )
    
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    # Create consent record
    db_consent = Consent(
        tenant_id=current_operator.tenant_id,
        ticket_id=db_ticket.id,
        version=ticket.consent_version
    )
    
    db.add(db_consent)
    db.commit()
    
    return db_ticket

@router.get("", response_model=TicketList)
async def list_tickets(
    status: Optional[str] = None,
    service_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """List tickets with optional filters."""
    query = db.query(Ticket).filter(Ticket.tenant_id == current_operator.tenant_id)
    
    if status:
        query = query.filter(Ticket.status == status)
    if service_id:
        query = query.filter(Ticket.service_id == service_id)
        
    total = query.count()
    tickets = query.offset(skip).limit(limit).all()
    
    return {"items": tickets, "total": total}

@router.get("/{ticket_id}", response_model=TicketSchema)
async def get_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Get ticket by ID."""
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_operator.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
        
    return ticket

@router.put("/{ticket_id}/call", response_model=TicketSchema)
async def call_ticket(
    ticket_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Mark ticket as called."""
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.tenant_id == current_operator.tenant_id,
        Ticket.status == "paid"  # Only paid tickets can be called
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found or not paid"
        )
        
    ticket.status = "called"
    ticket.called_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ticket)
    
    return ticket

@router.get("/queue", response_model=TicketList)
async def get_queue(
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Get current queue (paid tickets not called)."""
    tickets = db.query(Ticket).filter(
        Ticket.tenant_id == current_operator.tenant_id,
        Ticket.status == "paid",
        Ticket.called_at == None
    ).order_by(Ticket.created_at.asc()).all()
    
    return {"items": tickets, "total": len(tickets)} 