from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import qrcode
import io
import base64
import json
import hmac
import hashlib

from database import get_db
from models import Payment, Ticket, Service, Tenant
from schemas import PaymentCreate, Payment as PaymentSchema, PaymentList
from auth import get_current_operator
from security import encrypt_data
from services.payment.factory import PaymentAdapterFactory

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

# Sicredi API settings
SICREDI_API_URL = "https://api.sicredi.com.br/v1"  # Replace with actual URL
SICREDI_API_KEY = "your_api_key"  # Load from env
SICREDI_MERCHANT_ID = "your_merchant_id"  # Load from env

def generate_sicredi_payment_link(ticket: Ticket, service: Service) -> str:
    """Generate Sicredi payment link with QR code."""
    # Format amount in cents
    amount_cents = int(service.price * 100)
    
    # Create payment data
    payment_data = {
        "merchant_id": SICREDI_MERCHANT_ID,
        "amount": amount_cents,
        "currency": "BRL",
        "order_id": str(ticket.id),
        "description": f"Ticket #{ticket.ticket_number} - {service.name}",
        "callback_url": f"{SICREDI_API_URL}/payments/webhook",
        "return_url": f"{SICREDI_API_URL}/payments/return"
    }
    
    # Generate signature
    signature = hmac.new(
        SICREDI_API_KEY.encode(),
        json.dumps(payment_data).encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Add signature to payment data
    payment_data["signature"] = signature
    
    # Make request to Sicredi API
    # TODO: Implement actual API call
    payment_link = f"{SICREDI_API_URL}/payments/create"
    
    return payment_link

def generate_qr_code(payment_link: str) -> str:
    """Generate QR code from payment link."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payment_link)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

@router.post("", response_model=PaymentSchema)
async def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Create new payment."""
    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == current_operator.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Verify ticket exists and belongs to tenant
    ticket = db.query(Ticket).filter(
        Ticket.id == payment.ticket_id,
        Ticket.tenant_id == current_operator.tenant_id
    ).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Get service
    service = db.query(Service).filter(
        Service.id == ticket.service_id,
        Service.tenant_id == current_operator.tenant_id
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Create payment adapter
    adapter = PaymentAdapterFactory.create_adapter(
        tenant.payment_adapter,
        tenant.payment_config
    )
    
    # Create payment in adquirente
    payment_data = await adapter.create_payment(
        amount=service.price,
        description=f"Ticket #{ticket.ticket_number} - {service.name}",
        metadata={
            "ticket_id": str(ticket.id),
            "service_id": str(service.id),
            "tenant_id": str(tenant.id)
        }
    )
    
    # Create payment record
    db_payment = Payment(
        tenant_id=current_operator.tenant_id,
        ticket_id=payment.ticket_id,
        amount=service.price,
        status="pending",
        payment_method=payment.payment_method,
        transaction_id=payment_data["transaction_id"],
        payment_link=payment_data.get("payment_link")
    )
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    # Generate QR code if payment link exists
    if db_payment.payment_link:
        qr_code = generate_qr_code(db_payment.payment_link)
        response = PaymentSchema.from_orm(db_payment)
        response.qr_code = qr_code
        return response
    
    return db_payment

@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle payment webhook from adquirente."""
    # Get webhook data
    webhook_data = await request.json()
    
    # Get payment
    payment = db.query(Payment).filter(
        Payment.transaction_id == webhook_data["transaction_id"]
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Get tenant and adapter
    tenant = db.query(Tenant).filter(Tenant.id == payment.tenant_id).first()
    adapter = PaymentAdapterFactory.create_adapter(
        tenant.payment_adapter,
        tenant.payment_config
    )
    
    # Verify webhook signature
    signature = request.headers.get("X-Signature")
    if not adapter.verify_webhook(webhook_data, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Update payment status
    payment.status = webhook_data["status"]
    payment.webhook_data = json.dumps(webhook_data)
    
    if webhook_data["status"] == "completed":
        payment.completed_at = datetime.utcnow()
        
        # Update ticket status
        ticket = db.query(Ticket).filter(Ticket.id == payment.ticket_id).first()
        if ticket:
            ticket.status = "paid"
    
    db.commit()
    
    return {"status": "ok"}

@router.get("", response_model=PaymentList)
async def list_payments(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """List payments with optional filters."""
    query = db.query(Payment).filter(Payment.tenant_id == current_operator.tenant_id)
    
    if status:
        query = query.filter(Payment.status == status)
        
    total = query.count()
    payments = query.offset(skip).limit(limit).all()
    
    return {"items": payments, "total": total}

@router.get("/{payment_id}", response_model=PaymentSchema)
async def get_payment(
    payment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_operator: Operator = Depends(get_current_operator)
):
    """Get payment by ID."""
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.tenant_id == current_operator.tenant_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
        
    return payment 