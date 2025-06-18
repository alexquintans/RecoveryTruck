# 🔐 Router de Webhooks com Validação Avançada

from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import json
from datetime import datetime

from apps.api.services.webhook_validator import (
    webhook_validator, WebhookProvider, WebhookValidationResult,
    get_sicredi_config, get_stone_config, get_pagseguro_config,
    get_mercadopago_config, get_safrapay_config, get_pagbank_config
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# === Configuração de Webhooks ===

async def setup_webhook_validators():
    """Configura validadores de webhook para todos os provedores"""
    
    # Configurações de exemplo - em produção viriam do banco de dados
    configs = {
        "sicredi": "webhook_secret_sicredi_123",
        "stone": "webhook_secret_stone_456", 
        "pagseguro": "webhook_secret_pagseguro_789",
        "mercadopago": "webhook_secret_mercadopago_abc",
        "safrapay": "webhook_secret_safrapay_def",
        "pagbank": "webhook_secret_pagbank_ghi"
    }
    
    # Registra configurações
    webhook_validator.register_provider(get_sicredi_config(configs["sicredi"]))
    webhook_validator.register_provider(get_stone_config(configs["stone"]))
    webhook_validator.register_provider(get_pagseguro_config(configs["pagseguro"]))
    webhook_validator.register_provider(get_mercadopago_config(configs["mercadopago"]))
    webhook_validator.register_provider(get_safrapay_config(configs["safrapay"]))
    webhook_validator.register_provider(get_pagbank_config(configs["pagbank"]))
    
    logger.info("🔐 Webhook validators configured")

# === Dependências ===

async def get_client_ip(request: Request) -> str:
    """Obtém IP do cliente"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

async def get_request_body(request: Request) -> bytes:
    """Obtém corpo da requisição"""
    return await request.body()

# === Endpoints de Webhook ===

@router.post("/sicredi")
async def sicredi_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    client_ip: str = Depends(get_client_ip),
    body: bytes = Depends(get_request_body)
):
    """🏦 Webhook do Sicredi"""
    return await process_webhook(
        provider=WebhookProvider.SICREDI,
        request=request,
        body=body,
        client_ip=client_ip,
        background_tasks=background_tasks
    )

@router.post("/stone")
async def stone_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    client_ip: str = Depends(get_client_ip),
    body: bytes = Depends(get_request_body)
):
    """🪨 Webhook do Stone"""
    return await process_webhook(
        provider=WebhookProvider.STONE,
        request=request,
        body=body,
        client_ip=client_ip,
        background_tasks=background_tasks
    )

@router.post("/pagseguro")
async def pagseguro_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    client_ip: str = Depends(get_client_ip),
    body: bytes = Depends(get_request_body)
):
    """💳 Webhook do PagSeguro"""
    return await process_webhook(
        provider=WebhookProvider.PAGSEGURO,
        request=request,
        body=body,
        client_ip=client_ip,
        background_tasks=background_tasks
    )

@router.post("/mercadopago")
async def mercadopago_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    client_ip: str = Depends(get_client_ip),
    body: bytes = Depends(get_request_body)
):
    """💰 Webhook do MercadoPago"""
    return await process_webhook(
        provider=WebhookProvider.MERCADOPAGO,
        request=request,
        body=body,
        client_ip=client_ip,
        background_tasks=background_tasks
    )

@router.post("/safrapay")
async def safrapay_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    client_ip: str = Depends(get_client_ip),
    body: bytes = Depends(get_request_body)
):
    """🏦 Webhook do SafraPay"""
    return await process_webhook(
        provider=WebhookProvider.SAFRAPAY,
        request=request,
        body=body,
        client_ip=client_ip,
        background_tasks=background_tasks
    )

@router.post("/pagbank")
async def pagbank_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    client_ip: str = Depends(get_client_ip),
    body: bytes = Depends(get_request_body)
):
    """🏧 Webhook do PagBank"""
    return await process_webhook(
        provider=WebhookProvider.PAGBANK,
        request=request,
        body=body,
        client_ip=client_ip,
        background_tasks=background_tasks
    )

# === Processamento de Webhook ===

async def process_webhook(
    provider: WebhookProvider,
    request: Request,
    body: bytes,
    client_ip: str,
    background_tasks: BackgroundTasks
) -> JSONResponse:
    """🔍 Processa webhook com validação completa"""
    
    try:
        # Converte headers para dict
        headers = dict(request.headers)
        
        # Log da requisição
        logger.info(f"🔔 Webhook received: {provider.value} from {client_ip}")
        
        # Valida webhook
        result = webhook_validator.validate_webhook(
            provider=provider,
            payload=body,
            headers=headers,
            client_ip=client_ip
        )
        
        if not result.is_valid:
            # Log detalhado dos erros
            logger.error(f"❌ Webhook validation failed: {provider.value}")
            for error in result.errors:
                logger.error(f"   - {error}")
            
            # Retorna erro 400 para webhooks inválidos
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid webhook",
                    "provider": provider.value,
                    "errors": result.errors
                }
            )
        
        # Log de sucesso
        logger.info(f"✅ Webhook validated: {provider.value} - {result.transaction_id}")
        
        # Processa webhook em background
        background_tasks.add_task(
            process_webhook_background,
            provider=provider,
            result=result,
            payload_data=json.loads(body.decode()) if body else {}
        )
        
        # Retorna resposta de sucesso
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "provider": provider.value,
                "transaction_id": result.transaction_id,
                "event_type": result.event_type,
                "timestamp": result.timestamp.isoformat() if result.timestamp else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )

async def process_webhook_background(
    provider: WebhookProvider,
    result: WebhookValidationResult,
    payload_data: Dict[str, Any]
):
    """🔄 Processa webhook em background"""
    
    try:
        logger.info(f"🔄 Processing webhook: {provider.value} - {result.transaction_id}")
        
        if result.event_type in ["payment.approved", "transaction.approved"]:
            await handle_payment_approved(provider, result, payload_data)
        
        elif result.event_type in ["payment.failed", "transaction.failed"]:
            await handle_payment_failed(provider, result, payload_data)
        
        elif result.event_type in ["payment.cancelled", "transaction.cancelled"]:
            await handle_payment_cancelled(provider, result, payload_data)
        
        else:
            logger.info(f"ℹ️ Unhandled event type: {result.event_type}")
        
        logger.info(f"✅ Webhook processed: {provider.value} - {result.transaction_id}")
        
    except Exception as e:
        logger.error(f"❌ Background processing error: {e}")

async def handle_payment_approved(
    provider: WebhookProvider,
    result: WebhookValidationResult,
    payload_data: Dict[str, Any]
):
    """✅ Processa pagamento aprovado"""
    
    logger.info(f"✅ Payment approved: {result.transaction_id}")
    
    try:
        from apps.api.services.printer_service import printer_service, ReceiptData, ReceiptType
        
        receipt_data = ReceiptData(
            transaction_id=result.transaction_id or "unknown",
            receipt_type=ReceiptType.CUSTOMER,
            amount=float(payload_data.get("amount", 0)) / 100,
            payment_method=payload_data.get("payment_method", "unknown"),
            status="approved",
            timestamp=result.timestamp or datetime.now(),
            merchant_name=f"{provider.value.title()} Merchant",
            merchant_cnpj="00000000000000"
        )
        
        await printer_service.print_receipt(receipt_data)
        
    except Exception as e:
        logger.warning(f"⚠️ Auto-print failed: {e}")

async def handle_payment_failed(
    provider: WebhookProvider,
    result: WebhookValidationResult,
    payload_data: Dict[str, Any]
):
    """❌ Processa pagamento negado"""
    logger.info(f"❌ Payment failed: {result.transaction_id}")

async def handle_payment_cancelled(
    provider: WebhookProvider,
    result: WebhookValidationResult,
    payload_data: Dict[str, Any]
):
    """🚫 Processa pagamento cancelado"""
    logger.info(f"🚫 Payment cancelled: {result.transaction_id}")

# === Endpoints de Teste ===

@router.get("/test/{provider}")
async def test_webhook_config(provider: str):
    """🧪 Testa configuração de webhook"""
    
    try:
        provider_enum = WebhookProvider(provider.lower())
        
        if provider_enum not in webhook_validator._configs:
            raise HTTPException(
                status_code=404,
                detail=f"Provider {provider} not configured"
            )
        
        config = webhook_validator._configs[provider_enum]
        
        return {
            "provider": provider_enum.value,
            "configured": True,
            "algorithm": config.algorithm.value,
            "require_timestamp": config.require_timestamp,
            "allow_replay": config.allow_replay,
            "max_timestamp_diff": config.max_timestamp_diff,
            "signature_header": config.signature_header,
            "timestamp_header": config.timestamp_header
        }
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {provider}"
        )

@router.get("/status")
async def webhook_status():
    """📊 Status dos webhooks"""
    
    configured_providers = list(webhook_validator._configs.keys())
    
    return {
        "status": "active",
        "configured_providers": [p.value for p in configured_providers],
        "total_providers": len(configured_providers),
        "replay_protection": {
            "enabled": True,
            "max_age": webhook_validator._replay_protection.max_age,
            "cached_webhooks": len(webhook_validator._replay_protection._processed_webhooks)
        }
    }

# Inicializa validadores
async def init_webhooks():
    """Inicializa sistema de webhooks"""
    await setup_webhook_validators()
