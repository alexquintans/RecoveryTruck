from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
import re
import logging

from database import get_db
from models import PaymentSession, Ticket, Consent
from schemas import Customer

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["customers"]
)

def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF seguindo algoritmo oficial brasileiro
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Calcula segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    # Verifica se os dígitos calculados são iguais aos do CPF
    return cpf[-2:] == f"{digito1}{digito2}"

def normalize_cpf(cpf: str) -> str:
    """
    Normaliza CPF removendo formatação
    """
    return re.sub(r'[^0-9]', '', cpf)

@router.get("/search", response_model=Optional[Customer])
async def search_customer(
    q: str = Query(..., min_length=3, description="Termo de busca (nome ou CPF)"),
    tenant_id: UUID = Query(..., description="ID do tenant"),
    db: Session = Depends(get_db)
):
    """
    Busca cliente na base de dados por nome ou CPF.
    Procura PRINCIPALMENTE na tabela Ticket onde estão os dados reais dos clientes.
    Retorna dados do cliente mais recente encontrado.
    """
    
    logger.info(f"🔍 Buscando cliente: termo='{q}', tenant_id={tenant_id}")
    
    # Limpar e normalizar o termo de busca
    search_term = q.strip()
    
    # Verificar se é um CPF (apenas números)
    cpf_clean = normalize_cpf(search_term)
    is_cpf = len(cpf_clean) == 11
    
    if is_cpf:
        # Validar CPF se tiver 11 dígitos
        if not validate_cpf(cpf_clean):
            logger.warning(f"❌ CPF inválido fornecido: {search_term}")
            return None
        
        logger.info(f"🔍 Buscando por CPF: {cpf_clean}")
        
        # PRIMEIRO: Buscar em Ticket (dados reais dos clientes)
        ticket = db.query(Ticket).filter(
            and_(
                Ticket.tenant_id == tenant_id,
                Ticket.customer_cpf == cpf_clean
            )
        ).order_by(Ticket.created_at.desc()).first()
        
        if ticket:
            logger.info(f"✅ Cliente encontrado em Ticket: {ticket.customer_name}")
            return Customer(
                name=ticket.customer_name,
                cpf=ticket.customer_cpf,
                phone=ticket.customer_phone
            )
        
        # SEGUNDO: Buscar em PaymentSession (apenas como fallback)
        payment_session = db.query(PaymentSession).filter(
            and_(
                PaymentSession.tenant_id == tenant_id,
                PaymentSession.customer_cpf == cpf_clean
            )
        ).order_by(PaymentSession.created_at.desc()).first()
        
        if payment_session:
            logger.info(f"✅ Cliente encontrado em PaymentSession (fallback): {payment_session.customer_name}")
            return Customer(
                name=payment_session.customer_name,
                cpf=payment_session.customer_cpf,
                phone=payment_session.customer_phone
            )
        
        logger.info(f"ℹ️ Cliente não encontrado para CPF: {cpf_clean}")
        return None
    
    else:
        # Busca por nome (case insensitive)
        logger.info(f"🔍 Buscando por nome: {search_term}")
        name_search = f"%{search_term}%"
        
        # PRIMEIRO: Buscar em Ticket (dados reais dos clientes)
        ticket = db.query(Ticket).filter(
            and_(
                Ticket.tenant_id == tenant_id,
                Ticket.customer_name.ilike(name_search)
            )
        ).order_by(Ticket.created_at.desc()).first()
        
        if ticket:
            logger.info(f"✅ Cliente encontrado em Ticket: {ticket.customer_name}")
            return Customer(
                name=ticket.customer_name,
                cpf=ticket.customer_cpf,
                phone=ticket.customer_phone
            )
        
        # SEGUNDO: Buscar em PaymentSession (apenas como fallback)
        payment_session = db.query(PaymentSession).filter(
            and_(
                PaymentSession.tenant_id == tenant_id,
                PaymentSession.customer_name.ilike(name_search)
            )
        ).order_by(PaymentSession.created_at.desc()).first()
        
        if payment_session:
            logger.info(f"✅ Cliente encontrado em PaymentSession (fallback): {payment_session.customer_name}")
            return Customer(
                name=payment_session.customer_name,
                cpf=payment_session.customer_cpf,
                phone=payment_session.customer_phone
            )
        
        logger.info(f"ℹ️ Cliente não encontrado para nome: {search_term}")
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
    Busca tanto em PaymentSession quanto em Ticket.
    """
    logger.info(f"🔍 Buscando consentimento: tenant_id={tenant_id}, cpf={cpf}, name={name}, phone={phone}")
    
    consent = None
    now = datetime.utcnow()
    cutoff = now - timedelta(days=30)

    if cpf:
        cpf_clean = normalize_cpf(cpf)
        if validate_cpf(cpf_clean):
            # PRIMEIRO: Buscar em Ticket (dados reais dos clientes)
            consent = db.query(Consent).join(PaymentSession).join(Ticket).filter(
                Consent.tenant_id == tenant_id,
                Consent.payment_session_id == PaymentSession.id,
                PaymentSession.id == Ticket.payment_session_id,
                Ticket.customer_cpf == cpf_clean,
                Consent.signature.isnot(None),
                Consent.created_at >= cutoff
            ).order_by(Consent.created_at.desc()).first()
            
            # SEGUNDO: Buscar em PaymentSession (apenas como fallback)
            if not consent:
                consent = db.query(Consent).join(PaymentSession).filter(
                    Consent.tenant_id == tenant_id,
                    Consent.payment_session_id == PaymentSession.id,
                    PaymentSession.customer_cpf == cpf_clean,
                    Consent.signature.isnot(None),
                    Consent.created_at >= cutoff
                ).order_by(Consent.created_at.desc()).first()
        else:
            logger.warning(f"❌ CPF inválido para busca de consentimento: {cpf}")
    
    elif name and phone:
        # PRIMEIRO: Buscar em Ticket (dados reais dos clientes)
        consent = db.query(Consent).join(PaymentSession).join(Ticket).filter(
            Consent.tenant_id == tenant_id,
            Consent.payment_session_id == PaymentSession.id,
            PaymentSession.id == Ticket.payment_session_id,
            Ticket.customer_name.ilike(f"%{name}%"),
            Ticket.customer_phone == phone,
            Consent.signature.isnot(None),
            Consent.created_at >= cutoff
        ).order_by(Consent.created_at.desc()).first()
        
        # SEGUNDO: Buscar em PaymentSession (apenas como fallback)
        if not consent:
            consent = db.query(Consent).join(PaymentSession).filter(
                Consent.tenant_id == tenant_id,
                Consent.payment_session_id == PaymentSession.id,
                PaymentSession.customer_name.ilike(f"%{name}%"),
                PaymentSession.customer_phone == phone,
                Consent.signature.isnot(None),
                Consent.created_at >= cutoff
            ).order_by(Consent.created_at.desc()).first()
    
    elif name:
        # PRIMEIRO: Buscar em Ticket (dados reais dos clientes)
        consent = db.query(Consent).join(PaymentSession).join(Ticket).filter(
            Consent.tenant_id == tenant_id,
            Consent.payment_session_id == PaymentSession.id,
            PaymentSession.id == Ticket.payment_session_id,
            Ticket.customer_name.ilike(f"%{name}%"),
            Consent.signature.isnot(None),
            Consent.created_at >= cutoff
        ).order_by(Consent.created_at.desc()).first()
        
        # SEGUNDO: Buscar em PaymentSession (apenas como fallback)
        if not consent:
            consent = db.query(Consent).join(PaymentSession).filter(
                Consent.tenant_id == tenant_id,
                Consent.payment_session_id == PaymentSession.id,
                PaymentSession.customer_name.ilike(f"%{name}%"),
                Consent.signature.isnot(None),
                Consent.created_at >= cutoff
            ).order_by(Consent.created_at.desc()).first()

    if consent:
        logger.info(f"✅ Consentimento encontrado: {consent.id}")
        return {
            "signature": consent.signature,
            "created_at": consent.created_at.isoformat()
        }
    
    logger.info("ℹ️ Nenhum consentimento válido encontrado")
    return None 