from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
import re

from database import get_db
from models import PaymentSession, Ticket, Consent
from schemas import Customer

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

@router.get("/search", response_model=Optional[Customer])
async def search_customer(
    q: str = Query(..., min_length=3, description="Termo de busca (nome ou CPF)"),
    tenant_id: UUID = Query(..., description="ID do tenant"),
    db: Session = Depends(get_db)
):
    """
    Busca cliente na base de dados por nome ou CPF.
    Procura nas tabelas PaymentSession e Ticket.
    """
    
    # Limpar e normalizar o termo de busca
    search_term = q.strip()
    
    # Verificar se é um CPF (apenas números)
    is_cpf = re.match(r'^\d{11}$', search_term.replace('.', '').replace('-', ''))
    
    if is_cpf:
        # Busca por CPF (normalizado)
        cpf_clean = search_term.replace('.', '').replace('-', '')
        
        # Buscar em PaymentSession
        payment_session = db.query(PaymentSession).filter(
            and_(
                PaymentSession.tenant_id == tenant_id,
                PaymentSession.customer_cpf == cpf_clean
            )
        ).order_by(PaymentSession.created_at.desc()).first()
        
        if payment_session:
            return Customer(
                name=payment_session.customer_name,
                cpf=payment_session.customer_cpf,
                phone=payment_session.customer_phone
            )
        
        # Buscar em Ticket
        ticket = db.query(Ticket).filter(
            and_(
                Ticket.tenant_id == tenant_id,
                Ticket.customer_cpf == cpf_clean
            )
        ).order_by(Ticket.created_at.desc()).first()
        
        if ticket:
            return Customer(
                name=ticket.customer_name,
                cpf=ticket.customer_cpf,
                phone=ticket.customer_phone
            )
    
    else:
        # Busca por nome (case insensitive)
        name_search = f"%{search_term}%"
        
        # Buscar em PaymentSession
        payment_session = db.query(PaymentSession).filter(
            and_(
                PaymentSession.tenant_id == tenant_id,
                or_(
                    PaymentSession.customer_name.ilike(name_search),
                    PaymentSession.customer_name.ilike(f"%{search_term}%")
                )
            )
        ).order_by(PaymentSession.created_at.desc()).first()
        
        if payment_session:
            return Customer(
                name=payment_session.customer_name,
                cpf=payment_session.customer_cpf,
                phone=payment_session.customer_phone
            )
        
        # Buscar em Ticket
        ticket = db.query(Ticket).filter(
            and_(
                Ticket.tenant_id == tenant_id,
                or_(
                    Ticket.customer_name.ilike(name_search),
                    Ticket.customer_name.ilike(f"%{search_term}%")
                )
            )
        ).order_by(Ticket.created_at.desc()).first()
        
        if ticket:
            return Customer(
                name=ticket.customer_name,
                cpf=ticket.customer_cpf,
                phone=ticket.customer_phone
            )
    
    # Cliente não encontrado
    return None 

@router.get("/consents/last")
async def get_last_consent(
    tenant_id: UUID = Query(...),
    cpf: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Busca o consentimento mais recente do cliente (por CPF, ou nome+telefone, ou nome).
    Retorna assinatura e data se válido (menos de 30 dias).
    """
    consent = None
    now = datetime.utcnow()
    cutoff = now - timedelta(days=30)

    if cpf:
        cpf_clean = cpf.replace('.', '').replace('-', '')
        consent = db.query(Consent).join(PaymentSession).filter(
            Consent.tenant_id == tenant_id,
            Consent.payment_session_id == PaymentSession.id,
            PaymentSession.customer_cpf == cpf_clean,
            Consent.signature.isnot(None),
            Consent.created_at >= cutoff
        ).order_by(Consent.created_at.desc()).first()
    elif name and phone:
        consent = db.query(Consent).join(PaymentSession).filter(
            Consent.tenant_id == tenant_id,
            Consent.payment_session_id == PaymentSession.id,
            PaymentSession.customer_name.ilike(f"%{name}%"),
            PaymentSession.customer_phone == phone,
            Consent.signature.isnot(None),
            Consent.created_at >= cutoff
        ).order_by(Consent.created_at.desc()).first()
    elif name:
        consent = db.query(Consent).join(PaymentSession).filter(
            Consent.tenant_id == tenant_id,
            Consent.payment_session_id == PaymentSession.id,
            PaymentSession.customer_name.ilike(f"%{name}%"),
            Consent.signature.isnot(None),
            Consent.created_at >= cutoff
        ).order_by(Consent.created_at.desc()).first()

    if consent:
        return {
            "signature": consent.signature,
            "created_at": consent.created_at.isoformat()
        }
    return None 