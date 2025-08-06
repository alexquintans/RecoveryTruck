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
    result = cpf[-2:] == f"{digito1}{digito2}"
    
    # DEBUG: Log da validação
    logger.info(f"🔍 DEBUG - validate_cpf: cpf='{cpf}', digito1={digito1}, digito2={digito2}, cpf[-2:]='{cpf[-2:]}', expected='{digito1}{digito2}', result={result}")
    
    return result

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
    
    # DEBUG: Verificar se o termo original parece ser um CPF formatado
    original_looks_like_cpf = len(search_term) == 14 and search_term.count('.') == 2 and search_term.count('-') == 1
    logger.info(f"🔍 DEBUG - original_looks_like_cpf: {original_looks_like_cpf}")
    
    # Se o original parece ser um CPF formatado mas não tem 11 dígitos após limpeza, pode ser um problema
    if original_looks_like_cpf and len(cpf_clean) != 11:
        logger.warning(f"🔍 DEBUG - CPF formatado mas não tem 11 dígitos após limpeza: '{search_term}' -> '{cpf_clean}' (len: {len(cpf_clean)})")
    
    logger.info(f"🔍 DEBUG - search_term: '{search_term}'")
    logger.info(f"🔍 DEBUG - cpf_clean: '{cpf_clean}'")
    logger.info(f"🔍 DEBUG - is_cpf: {is_cpf}")
    
    if is_cpf:
        # Validar CPF se tiver 11 dígitos
        logger.info(f"🔍 DEBUG - Validando CPF: {cpf_clean}")
        is_valid_cpf = validate_cpf(cpf_clean)
        logger.info(f"🔍 DEBUG - CPF válido: {is_valid_cpf}")
        
        if not is_valid_cpf:
            logger.warning(f"❌ CPF inválido fornecido: {search_term}")
            return None
        
        logger.info(f"🔍 Buscando por CPF: {cpf_clean}")
        
        # PRIMEIRO: Buscar em Ticket (dados reais dos clientes)
        logger.info(f"🔍 DEBUG - Executando query em Ticket...")
        
        # Buscar tanto por CPF normalizado quanto formatado
        logger.info(f"🔍 DEBUG - Buscando por CPF normalizado: '{cpf_clean}'")
        logger.info(f"🔍 DEBUG - Buscando por CPF original: '{search_term}'")
        
        # Primeiro, vamos verificar se existem tickets com CPF
        all_tickets_with_cpf = db.query(Ticket).filter(
            and_(
                Ticket.tenant_id == tenant_id,
                Ticket.customer_cpf.isnot(None)
            )
        ).all()
        
        logger.info(f"🔍 DEBUG - Total de tickets com CPF: {len(all_tickets_with_cpf)}")
        for t in all_tickets_with_cpf[:3]:
            logger.info(f"🔍 DEBUG - Ticket com CPF: '{t.customer_cpf}' (nome: {t.customer_name})")
        
        ticket = db.query(Ticket).filter(
            and_(
                Ticket.tenant_id == tenant_id,
                or_(
                    Ticket.customer_cpf == cpf_clean,  # CPF sem formatação
                    Ticket.customer_cpf == search_term   # CPF com formatação original
                )
            )
        ).order_by(Ticket.created_at.desc()).first()
        
        logger.info(f"🔍 DEBUG - Resultado da busca em Ticket: {ticket}")
        
        if ticket:
            logger.info(f"✅ Cliente encontrado em Ticket: {ticket.customer_name}")
            return Customer(
                name=ticket.customer_name,
                cpf=ticket.customer_cpf,
                phone=ticket.customer_phone
            )
        
        # SEGUNDO: Buscar em PaymentSession (apenas como fallback)
        logger.info(f"🔍 DEBUG - Executando query em PaymentSession...")
        payment_session = db.query(PaymentSession).filter(
            and_(
                PaymentSession.tenant_id == tenant_id,
                or_(
                    PaymentSession.customer_cpf == cpf_clean,  # CPF sem formatação
                    PaymentSession.customer_cpf == search_term   # CPF com formatação original
                )
            )
        ).order_by(PaymentSession.created_at.desc()).first()
        
        logger.info(f"🔍 DEBUG - Resultado da busca em PaymentSession: {payment_session}")
        
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
        
        logger.info(f"🔍 DEBUG - name_search: '{name_search}'")
        
        # PRIMEIRO: Buscar em Ticket (dados reais dos clientes)
        logger.info(f"🔍 DEBUG - Executando query em Ticket por nome...")
        ticket = db.query(Ticket).filter(
            and_(
                Ticket.tenant_id == tenant_id,
                Ticket.customer_name.ilike(name_search)
            )
        ).order_by(Ticket.created_at.desc()).first()
        
        logger.info(f"🔍 DEBUG - Resultado da busca em Ticket por nome: {ticket}")
        
        if ticket:
            logger.info(f"✅ Cliente encontrado em Ticket: {ticket.customer_name}")
            return Customer(
                name=ticket.customer_name,
                cpf=ticket.customer_cpf,
                phone=ticket.customer_phone
            )
        
        # SEGUNDO: Buscar em PaymentSession (apenas como fallback)
        logger.info(f"🔍 DEBUG - Executando query em PaymentSession por nome...")
        payment_session = db.query(PaymentSession).filter(
            and_(
                PaymentSession.tenant_id == tenant_id,
                PaymentSession.customer_name.ilike(name_search)
            )
        ).order_by(PaymentSession.created_at.desc()).first()
        
        logger.info(f"🔍 DEBUG - Resultado da busca em PaymentSession por nome: {payment_session}")
        
        if payment_session:
            logger.info(f"✅ Cliente encontrado em PaymentSession (fallback): {payment_session.customer_name}")
            return Customer(
                name=payment_session.customer_name,
                cpf=payment_session.customer_cpf,
                phone=payment_session.customer_phone
            )
        
        logger.info(f"ℹ️ Cliente não encontrado para nome: {search_term}")
        return None

@router.get("/debug/tickets")
async def debug_tickets(
    tenant_id: UUID = Query(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint de debug para verificar dados na tabela Ticket
    """
    logger.info(f"🔍 DEBUG - Verificando dados na tabela Ticket para tenant_id={tenant_id}")
    
    # Contar total de tickets
    total_tickets = db.query(Ticket).filter(Ticket.tenant_id == tenant_id).count()
    logger.info(f"🔍 DEBUG - Total de tickets: {total_tickets}")
    
    # Buscar tickets com CPF
    tickets_with_cpf = db.query(Ticket).filter(
        and_(
            Ticket.tenant_id == tenant_id,
            Ticket.customer_cpf.isnot(None)
        )
    ).all()
    
    logger.info(f"🔍 DEBUG - Tickets com CPF: {len(tickets_with_cpf)}")
    
    # Mostrar alguns exemplos
    for i, ticket in enumerate(tickets_with_cpf[:5]):
        logger.info(f"🔍 DEBUG - Ticket {i+1}: {ticket.customer_name}, CPF: {ticket.customer_cpf}")
    
    return {
        "total_tickets": total_tickets,
        "tickets_with_cpf": len(tickets_with_cpf),
        "examples": [
            {
                "name": ticket.customer_name,
                "cpf": ticket.customer_cpf,
                "phone": ticket.customer_phone
            }
            for ticket in tickets_with_cpf[:5]
        ]
    }

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