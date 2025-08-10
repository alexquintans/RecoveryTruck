from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import qrcode
import io
import base64
import json
import logging
import os

from database import get_db
from models import PaymentSession, Service, Tenant, Ticket, Consent, TicketService, TicketExtra
from schemas import PaymentSessionCreate, PaymentSession as PaymentSessionSchema, PaymentSessionWithQR, PaymentSessionList, Ticket as TicketSchema
from auth import get_current_operator
from security import encrypt_data, decrypt_data
from services.payment.factory import PaymentAdapterFactory
from services.printer_service import printer_manager
from constants import TicketStatus, PaymentSessionStatus
from services.queue_manager import get_queue_manager
from services.websocket import websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["payment-sessions"]
)

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

@router.post("", response_model=PaymentSessionSchema)
async def create_payment_session(
    session_in: PaymentSessionCreate,
    db: Session = Depends(get_db)
):
    # Suporte a simulação de pagamento
    if getattr(session_in, 'mock', False):
        # Cria uma sessão de pagamento simulada já aprovada
        payment_session = PaymentSession(
            tenant_id=session_in.tenant_id,
            service_id=session_in.service_id,
            customer_name=session_in.customer_name,
            customer_cpf=encrypt_data(session_in.customer_cpf) if session_in.customer_cpf else None,
            customer_phone=session_in.customer_phone,
            consent_version=session_in.consent_version,
            payment_method=session_in.payment_method,
            status="approved",
        )
        db.add(payment_session)
        db.commit()
        db.refresh(payment_session)
        return payment_session
    
    # TODO: Implementar tenant_id via header ou configuração do totem
    # Por enquanto, usar um tenant_id fixo para desenvolvimento
    TEMP_TENANT_ID = "f47ac10b-58cc-4372-a567-0e02b2c3d479"  # UUID fixo temporário
    
    # Verify service exists
    service = db.query(Service).filter(
        Service.id == session_in.service_id,
        Service.is_active == True
    ).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Create payment session (expires in 30 minutes)
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    db_payment_session = PaymentSession(
        tenant_id=TEMP_TENANT_ID,  # TODO: get from context
        service_id=session_in.service_id,
        customer_name=session_in.customer_name,
        customer_cpf=encrypt_data(session_in.customer_cpf) if session_in.customer_cpf else None,
        customer_phone=session_in.customer_phone,
        consent_version=session_in.consent_version,
        payment_method=session_in.payment_method,
        amount=service.price,
        status="pending",
        expires_at=expires_at
    )
    
    db.add(db_payment_session)
    db.commit()
    db.refresh(db_payment_session)
    
    # Create consent record
    db_consent = Consent(
        tenant_id=TEMP_TENANT_ID,
        payment_session_id=db_payment_session.id,
        version=session_in.consent_version,
        signature=getattr(session_in, 'signature', None)  # Salva assinatura se enviada
    )
    
    db.add(db_consent)
    db.commit()
    
    # Get tenant for payment adapter
    tenant = db.query(Tenant).filter(Tenant.id == TEMP_TENANT_ID).first()
    if not tenant:
        # Create default tenant for development
        tenant = Tenant(
            id=TEMP_TENANT_ID,
            name="RecoveryTruck",
            cnpj="12345678901234"
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
    
    # Create payment with adapter (if configured)
    payment_link = None
    if hasattr(tenant, 'payment_adapter') and tenant.payment_adapter:
        try:
            adapter = PaymentAdapterFactory.create_adapter(
                tenant.payment_adapter,
                tenant.payment_config or {}
            )
            
            payment_data = await adapter.create_payment(
                amount=float(service.price),
                description=f"Serviço: {service.name} - Cliente: {session_in.customer_name}",
                metadata={
                    "payment_session_id": str(db_payment_session.id),
                    "service_id": str(service.id),
                    "tenant_id": str(tenant.id)
                }
            )
            
            # Update payment session with payment data
            db_payment_session.transaction_id = payment_data["transaction_id"]
            db_payment_session.payment_link = payment_data.get("payment_link")
            payment_link = payment_data.get("payment_link")
            
            db.commit()
            db.refresh(db_payment_session)
            
        except Exception as e:
            # Log error but continue - pode usar pagamento manual
            print(f"Error creating payment: {e}")
    
    # Generate QR code if payment link exists
    response = PaymentSessionSchema.from_orm(db_payment_session)
    if payment_link:
        response.qr_code = generate_qr_code(payment_link)
    
    return response

@router.post("/{session_id}/simulate-payment-success", response_model=TicketSchema, include_in_schema=os.environ.get("APP_ENV") == "development")
async def simulate_payment_success(
    session_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Simulate a successful payment for a given session.
    This endpoint is only available in development environments.
    """
    if os.environ.get("APP_ENV") != "development":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint not found"
        )

    payment_session = db.query(PaymentSession).filter(PaymentSession.id == session_id).first()
    if not payment_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment session not found")

    if payment_session.status != PaymentSessionStatus.PENDING.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment session is not pending")

    # Update session status
    payment_session.status = PaymentSessionStatus.PAID.value
    payment_session.completed_at = datetime.utcnow()
    
    # Create ticket from session
    ticket = await create_ticket_from_payment_session(payment_session, db)
    
    # Commit changes
    db.commit()
    db.refresh(ticket)
    
    # Notify via WebSocket
    await websocket_manager.broadcast_to_tenant(
        tenant_id=str(payment_session.tenant_id),
        message={
            "type": "payment_update",
            "data": {
                "id": str(payment_session.id),
                "status": "paid",
                "ticket_id": str(ticket.id)
            }
        }
    )

    return ticket


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle payment webhook from payment provider."""
    
    try:
        # Get webhook data
        webhook_data = await request.json()
        logger.info(f"📥 Webhook received: {json.dumps(webhook_data, indent=2)}")
        
        # Validate required fields
        transaction_id = webhook_data.get("transaction_id")
        payment_status = webhook_data.get("status")
        
        if not transaction_id:
            logger.error("❌ Webhook missing transaction_id")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing transaction_id in webhook"
            )
        
        if not payment_status:
            logger.error("❌ Webhook missing status")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing status in webhook"
            )
        
        # Get payment session by transaction_id
        payment_session = db.query(PaymentSession).filter(
            PaymentSession.transaction_id == transaction_id
        ).first()
        
        if not payment_session:
            logger.error(f"❌ Payment session not found for transaction_id: {transaction_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment session not found for transaction_id: {transaction_id}"
            )
        
        # Log current state
        logger.info(f"🔍 Processing webhook for payment session {payment_session.id}")
        logger.info(f"   Current status: {payment_session.status}")
        logger.info(f"   New status: {payment_status}")
        
        # Update payment session status and webhook data
        old_status = payment_session.status
        payment_session.status = PaymentSessionStatus(payment_status).value
        payment_session.webhook_data = webhook_data  # Store as JSONB
        payment_session.updated_at = datetime.utcnow()
        
        # Handle different payment statuses
        if payment_status == PaymentSessionStatus.PAID.value:
            logger.info(f"💰 Payment confirmed for session {payment_session.id}")
            payment_session.completed_at = datetime.utcnow()
            
            # 🎯 INTEGRAÇÃO PRINCIPAL: Criar ticket automaticamente após pagamento confirmado
            try:
                ticket = await create_ticket_from_payment_session(payment_session, db)
                logger.info(f"🎫 Ticket #{ticket.ticket_number} created from payment session {payment_session.id}")
                
                # Commit all changes
                db.commit()
                
                return {
                    "status": "success",
                    "message": "Payment confirmed and ticket created",
                    "payment_session_id": str(payment_session.id),
                    "ticket_id": str(ticket.id),
                    "ticket_number": ticket.ticket_number
                }
                
            except Exception as ticket_error:
                logger.error(f"❌ Error creating ticket from payment session {payment_session.id}: {ticket_error}")
                # Rollback ticket creation but keep payment status
                db.rollback()
                
                # Update only payment session status
                payment_session.status = PaymentSessionStatus.PAID.value
                payment_session.completed_at = datetime.utcnow()
                payment_session.webhook_data = webhook_data
                db.commit()
                
                # Return error but acknowledge webhook
                return {
                    "status": "partial_success",
                    "message": "Payment confirmed but ticket creation failed",
                    "payment_session_id": str(payment_session.id),
                    "error": str(ticket_error)
                }
        
        elif payment_status == PaymentSessionStatus.FAILED.value:
            logger.warning(f"💸 Payment failed for session {payment_session.id}")
            # Payment failed - no ticket creation
            
        elif payment_status == PaymentSessionStatus.CANCELLED.value:
            logger.info(f"🚫 Payment cancelled for session {payment_session.id}")
            # Payment cancelled - no ticket creation
            
        elif payment_status == PaymentSessionStatus.EXPIRED.value:
            logger.info(f"⏰ Payment expired for session {payment_session.id}")
            # Payment expired - no ticket creation
            
        else:
            logger.warning(f"⚠️ Unknown payment status: {payment_status} for session {payment_session.id}")
        
        # Commit payment session updates
        db.commit()
        
        logger.info(f"✅ Webhook processed successfully for session {payment_session.id}")
        logger.info(f"   Status changed: {old_status} → {payment_status}")
        
        return {
            "status": "success",
            "message": f"Webhook processed - status updated to {payment_status}",
            "payment_session_id": str(payment_session.id)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"❌ Unexpected error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.post("/webhook/simulate")
async def simulate_webhook(
    transaction_id: str,
    payment_status: str = "paid",
    db: Session = Depends(get_db)
):
    """Simulate a payment webhook - useful for testing"""
    
    # Validate status
    try:
        PaymentSessionStatus(payment_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment status: {payment_status}. Valid options: {[s.value for s in PaymentSessionStatus]}"
        )
    
    # Create mock webhook data
    mock_webhook_data = {
        "transaction_id": transaction_id,
        "status": payment_status,
        "amount": 50.00,
        "payment_method": "pix",
        "timestamp": datetime.utcnow().isoformat(),
        "provider": "mock",
        "simulated": True
    }
    
    logger.info(f"🧪 Simulating webhook for transaction {transaction_id} with status {payment_status}")
    
    # Create a mock request object
    class MockRequest:
        async def json(self):
            return mock_webhook_data
    
    mock_request = MockRequest()
    
    # Call the actual webhook handler
    return await payment_webhook(mock_request, db)

async def create_ticket_from_payment_session(payment_session: PaymentSession, db: Session):
    """Cria ticket automaticamente após pagamento confirmado."""
    
    try:
        # Get next ticket number for this tenant
        last_ticket = db.query(Ticket).filter(
            Ticket.tenant_id == payment_session.tenant_id
        ).order_by(Ticket.ticket_number.desc()).first()
        
        ticket_number = 1 if not last_ticket else last_ticket.ticket_number + 1
        
        # Create ticket with IN_QUEUE status (pagamento já confirmado, ir direto para fila)
        ticket = Ticket(
            tenant_id=payment_session.tenant_id,
            payment_session_id=payment_session.id,
            ticket_number=ticket_number,
            status=TicketStatus.IN_QUEUE.value,  # Ir direto para fila
            customer_name=payment_session.customer_name,
            customer_cpf=payment_session.customer_cpf,
            customer_phone=payment_session.customer_phone,
            consent_version=payment_session.consent_version,
            print_attempts=0,
            queued_at=datetime.utcnow()  # Definir queued_at imediatamente
        )
        
        db.add(ticket)
        db.flush()  # Para obter o ID do ticket
        
        # ✅ CORREÇÃO: Criar associações na tabela ticket_services para múltiplos serviços
        from models import TicketService
        
        # Buscar todos os serviços da sessão de pagamento
        # Por enquanto, criar apenas o serviço principal, mas preparar para múltiplos
        services_to_add = [payment_session.service_id]
        
        # TODO: Implementar suporte a múltiplos serviços na PaymentSession
        # Por enquanto, usar apenas o service_id principal
        
        for service_id in services_to_add:
            ticket_service = TicketService(
                ticket_id=ticket.id,
                service_id=service_id,
                price=payment_session.amount / len(services_to_add)  # Dividir valor entre serviços
            )
            db.add(ticket_service)
            logger.info(f"🔍 DEBUG - Criada associação ticket_service para ticket {ticket.id} com service_id {service_id}")
        
        db.commit()
        db.refresh(ticket)
        
        logger.info(f"🎯 Ticket #{ticket.ticket_number} created successfully from payment session {payment_session.id} and moved to queue")
        return ticket
        
    except Exception as e:
        logger.error(f"❌ Critical error creating ticket from payment session {payment_session.id}: {e}")
        # Reverter transação se possível
        db.rollback()
        raise e

async def _handle_print_success(ticket: Ticket, db: Session):
    """Manipula o sucesso da impressão, movendo ticket para IN_QUEUE"""
    try:
        ticket.status = TicketStatus.IN_QUEUE.value
        ticket.printed_at = datetime.utcnow()
        ticket.queued_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"🎯 Ticket #{ticket.ticket_number} successfully printed and moved to queue")
        
        # 📡 Notificar operador via WebSocket (quando implementado)
        try:
            notification_data = {
                "type": "new_ticket_in_queue",
                "ticket": {
                    "id": str(ticket.id),
                    "ticket_number": ticket.ticket_number,
                    "customer_name": ticket.customer_name,
                    "status": ticket.status,
                    "queued_at": ticket.queued_at.isoformat() if ticket.queued_at else None
                }
            }
            logger.info(f"📡 New ticket in queue notification prepared: {notification_data}")
            
        except Exception as ws_error:
            logger.error(f"❌ Error preparing WebSocket notification: {ws_error}")
            
    except Exception as e:
        logger.error(f"❌ Error handling print success for ticket #{ticket.ticket_number}: {e}")

@router.get("/{session_id}", response_model=PaymentSessionSchema)
async def get_payment_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get payment session by ID."""
    session = db.query(PaymentSession).filter(PaymentSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment session not found"
        )
        
    return session

@router.get("", response_model=PaymentSessionList)
async def list_payment_sessions(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List payment sessions with optional filters."""
    query = db.query(PaymentSession)
    
    if status:
        query = query.filter(PaymentSession.status == status)
        
    total = query.count()
    sessions = query.offset(skip).limit(limit).all()
    
    return {"items": sessions, "total": total}

@router.post("/test-print")
async def test_print():
    """Endpoint para testar a impressão - útil para debug"""
    try:
        test_data = {
            "ticket_number": 999,
            "service_name": "Teste de Impressão",
            "customer_name": "Cliente Teste",
            "customer_cpf": "1234",
            "status": "TESTE",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await printer_manager.queue_print_job("default", "ticket", test_data)
        
        return {
            "status": "success",
            "message": "Teste de impressão enviado para a fila",
            "queue_size": printer_manager.print_queue.qsize()
        }
        
    except Exception as e:
        logger.error(f"❌ Error in test print: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no teste de impressão: {str(e)}"
        )

@router.get("/print-status")
async def get_print_status():
    """Retorna o status do sistema de impressão"""
    try:
        print_status = {
            "queue_size": printer_manager.print_queue.qsize(),
            "configured_printers": list(printer_manager.printers.keys()),
            "printers_detail": {}
        }
        
        # Detalhes de cada impressora
        for printer_name in printer_manager.printers.keys():
            print_status["printers_detail"][printer_name] = printer_manager.get_printer_status(printer_name)
        
        return print_status
        
    except Exception as e:
        logger.error(f"❌ Error getting print status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter status de impressão: {str(e)}"
        )

@router.get("/integration/status")
async def get_integration_status(
    db: Session = Depends(get_db)
):
    """Retorna o status da integração pagamento ↔ ticket"""
    
    # Buscar estatísticas das últimas 24 horas
    yesterday = datetime.utcnow() - timedelta(hours=24)
    
    # Payment sessions criadas
    total_sessions = db.query(PaymentSession).filter(
        PaymentSession.created_at >= yesterday
    ).count()
    
    # Payment sessions por status
    sessions_by_status = {}
    for status in PaymentSessionStatus:
        count = db.query(PaymentSession).filter(
            PaymentSession.created_at >= yesterday,
            PaymentSession.status == status.value
        ).count()
        sessions_by_status[status.value] = count
    
    # Tickets criados a partir de payment sessions
    tickets_from_sessions = db.query(Ticket).filter(
        Ticket.created_at >= yesterday,
        Ticket.payment_session_id.isnot(None)
    ).count()
    
    # Payment sessions pagas que geraram tickets
    paid_sessions = db.query(PaymentSession).filter(
        PaymentSession.created_at >= yesterday,
        PaymentSession.status == PaymentSessionStatus.PAID.value
    ).count()
    
    # Taxa de conversão (pagamentos → tickets)
    conversion_rate = (tickets_from_sessions / paid_sessions * 100) if paid_sessions > 0 else 0
    
    # Sessões com problemas (pagas mas sem ticket)
    problematic_sessions = db.query(PaymentSession).outerjoin(Ticket).filter(
        PaymentSession.created_at >= yesterday,
        PaymentSession.status == PaymentSessionStatus.PAID.value,
        Ticket.id.is_(None)
    ).all()
    
    # Tempo médio entre pagamento e criação do ticket
    successful_integrations = db.query(PaymentSession, Ticket).join(Ticket).filter(
        PaymentSession.created_at >= yesterday,
        PaymentSession.status == PaymentSessionStatus.PAID.value
    ).all()
    
    avg_integration_time = None
    if successful_integrations:
        integration_times = []
        for session, ticket in successful_integrations:
            if session.completed_at and ticket.created_at:
                time_diff = (ticket.created_at - session.completed_at).total_seconds()
                integration_times.append(time_diff)
        
        if integration_times:
            avg_integration_time = sum(integration_times) / len(integration_times)
    
    return {
        "period": "last_24_hours",
        "summary": {
            "total_payment_sessions": total_sessions,
            "paid_sessions": paid_sessions,
            "tickets_created": tickets_from_sessions,
            "conversion_rate_percent": round(conversion_rate, 2),
            "problematic_sessions": len(problematic_sessions),
            "avg_integration_time_seconds": round(avg_integration_time, 2) if avg_integration_time else None
        },
        "sessions_by_status": sessions_by_status,
        "integration_health": {
            "status": "healthy" if conversion_rate >= 95 else "warning" if conversion_rate >= 80 else "critical",
            "issues": [
                {
                    "session_id": str(session.id),
                    "transaction_id": session.transaction_id,
                    "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                    "customer_name": session.customer_name,
                    "amount": float(session.amount)
                }
                for session in problematic_sessions[:10]  # Mostrar apenas os primeiros 10
            ]
        },
        "flow_validation": {
            "webhook_endpoint": "/payment-sessions/webhook",
            "simulation_endpoint": "/payment-sessions/webhook/simulate",
            "expected_flow": "payment_confirmed → webhook_received → ticket_created → ticket_printed → in_queue"
        }
    }

@router.get("/integration/test")
async def test_integration_flow(
    db: Session = Depends(get_db)
):
    """Testa o fluxo completo de integração pagamento ↔ ticket"""
    
    # Criar uma sessão de pagamento de teste
    test_service = db.query(Service).filter(Service.is_active == True).first()
    if not test_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum serviço ativo encontrado para teste"
        )
    
    # Criar payment session de teste
    test_session = PaymentSession(
        tenant_id=test_service.tenant_id,
        service_id=test_service.id,
        customer_name="Cliente Teste Integração",
        customer_cpf="12345678901",
        customer_phone="11999999999",
        consent_version="1.0",
        payment_method="pix",
        amount=test_service.price,
        status=PaymentSessionStatus.PENDING.value,
        transaction_id=f"test_integration_{int(datetime.utcnow().timestamp())}",
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    
    db.add(test_session)
    db.commit()
    db.refresh(test_session)
    
    logger.info(f"🧪 Created test payment session {test_session.id} for integration test")
    
    # Simular webhook de pagamento confirmado
    try:
        simulation_result = await simulate_webhook(
            transaction_id=test_session.transaction_id,
            payment_status="paid",
            db=db
        )
        
        # Verificar se ticket foi criado
        created_ticket = db.query(Ticket).filter(
            Ticket.payment_session_id == test_session.id
        ).first()
        
        if created_ticket:
            return {
                "status": "success",
                "message": "Integração funcionando corretamente",
                "test_data": {
                    "payment_session_id": str(test_session.id),
                    "transaction_id": test_session.transaction_id,
                    "ticket_id": str(created_ticket.id),
                    "ticket_number": created_ticket.ticket_number,
                    "ticket_status": created_ticket.status
                },
                "simulation_result": simulation_result,
                "flow_completed": True
            }
        else:
            return {
                "status": "error",
                "message": "Ticket não foi criado após pagamento confirmado",
                "test_data": {
                    "payment_session_id": str(test_session.id),
                    "transaction_id": test_session.transaction_id
                },
                "simulation_result": simulation_result,
                "flow_completed": False
            }
            
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return {
            "status": "error",
            "message": f"Erro no teste de integração: {str(e)}",
            "test_data": {
                "payment_session_id": str(test_session.id),
                "transaction_id": test_session.transaction_id
            },
            "flow_completed": False
        } 