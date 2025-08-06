#!/usr/bin/env python3
"""
Script para verificar dados na base de dados
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao Python path
current_dir = str(Path(__file__).parent)
sys.path.insert(0, current_dir)

from database import get_db
from models import Ticket, PaymentSession
from sqlalchemy import and_

def check_database():
    """Verificar dados na base de dados"""
    db = next(get_db())
    
    tenant_id = "7f02a566-2406-436d-b10d-90ecddd3fe2d"
    cpf = "43421731829"
    
    print(f"🔍 Verificando dados para tenant_id: {tenant_id}")
    print(f"🔍 CPF: {cpf}")
    
    # Verificar total de tickets
    total_tickets = db.query(Ticket).filter(Ticket.tenant_id == tenant_id).count()
    print(f"📊 Total de tickets: {total_tickets}")
    
    # Verificar tickets com CPF
    tickets_with_cpf = db.query(Ticket).filter(
        and_(
            Ticket.tenant_id == tenant_id,
            Ticket.customer_cpf.isnot(None)
        )
    ).all()
    
    print(f"📊 Tickets com CPF: {len(tickets_with_cpf)}")
    
    # Verificar tickets com CPF específico
    tickets_with_specific_cpf = db.query(Ticket).filter(
        and_(
            Ticket.tenant_id == tenant_id,
            Ticket.customer_cpf == cpf
        )
    ).all()
    
    print(f"📊 Tickets com CPF {cpf}: {len(tickets_with_specific_cpf)}")
    
    # Mostrar exemplos de tickets com CPF
    print("\n📋 Exemplos de tickets com CPF:")
    for i, ticket in enumerate(tickets_with_cpf[:5]):
        print(f"  {i+1}. {ticket.customer_name} - CPF: {ticket.customer_cpf} - Phone: {ticket.customer_phone}")
    
    # Verificar PaymentSessions
    total_payment_sessions = db.query(PaymentSession).filter(PaymentSession.tenant_id == tenant_id).count()
    print(f"\n📊 Total de PaymentSessions: {total_payment_sessions}")
    
    # Verificar PaymentSessions com CPF
    payment_sessions_with_cpf = db.query(PaymentSession).filter(
        and_(
            PaymentSession.tenant_id == tenant_id,
            PaymentSession.customer_cpf.isnot(None)
        )
    ).all()
    
    print(f"📊 PaymentSessions com CPF: {len(payment_sessions_with_cpf)}")
    
    # Verificar PaymentSessions com CPF específico
    payment_sessions_with_specific_cpf = db.query(PaymentSession).filter(
        and_(
            PaymentSession.tenant_id == tenant_id,
            PaymentSession.customer_cpf == cpf
        )
    ).all()
    
    print(f"📊 PaymentSessions com CPF {cpf}: {len(payment_sessions_with_specific_cpf)}")
    
    # Mostrar exemplos de PaymentSessions com CPF
    print("\n📋 Exemplos de PaymentSessions com CPF:")
    for i, session in enumerate(payment_sessions_with_cpf[:5]):
        print(f"  {i+1}. {session.customer_name} - CPF: {session.customer_cpf} - Phone: {session.customer_phone}")
    
    # Testar busca exata
    print(f"\n🔍 Testando busca exata por CPF: {cpf}")
    
    # Buscar em Ticket
    ticket_result = db.query(Ticket).filter(
        and_(
            Ticket.tenant_id == tenant_id,
            Ticket.customer_cpf == cpf
        )
    ).order_by(Ticket.created_at.desc()).first()
    
    if ticket_result:
        print(f"✅ Encontrado em Ticket: {ticket_result.customer_name}")
    else:
        print("❌ Não encontrado em Ticket")
    
    # Buscar em PaymentSession
    payment_session_result = db.query(PaymentSession).filter(
        and_(
            PaymentSession.tenant_id == tenant_id,
            PaymentSession.customer_cpf == cpf
        )
    ).order_by(PaymentSession.created_at.desc()).first()
    
    if payment_session_result:
        print(f"✅ Encontrado em PaymentSession: {payment_session_result.customer_name}")
    else:
        print("❌ Não encontrado em PaymentSession")

if __name__ == "__main__":
    check_database() 