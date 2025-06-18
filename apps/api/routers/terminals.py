# 🏧 API Endpoints para Terminais Físicos

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import logging

from ..core.auth import get_current_tenant
from ..services.payment.terminal_manager import terminal_manager
from ..services.payment.terminal import (
    TransactionRequest, PaymentMethod, PaymentTerminalError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/terminals", tags=["terminals"])

# === Schemas ===

class TerminalConfigRequest(BaseModel):
    """Configuração de terminal"""
    type: str = Field(..., description="Tipo do terminal (mock, stone, etc.)")
    connection_type: str = Field("serial", description="Tipo de conexão (serial, tcp, bluetooth)")
    port: Optional[str] = Field(None, description="Porta serial (ex: COM1, /dev/ttyUSB0)")
    host: Optional[str] = Field(None, description="Host TCP")
    tcp_port: Optional[int] = Field(None, description="Porta TCP")
    bluetooth_address: Optional[str] = Field(None, description="Endereço Bluetooth")
    baudrate: int = Field(115200, description="Taxa de transmissão serial")
    timeout: int = Field(30, description="Timeout em segundos")
    
    # Configurações específicas por provedor
    stone: Optional[Dict[str, Any]] = Field(None, description="Configurações Stone")
    sicredi: Optional[Dict[str, Any]] = Field(None, description="Configurações Sicredi")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "stone",
                "connection_type": "serial",
                "port": "COM1",
                "baudrate": 115200,
                "timeout": 30,
                "stone": {
                    "merchant_id": "123456789",
                    "terminal_id": "TERM001"
                }
            }
        }

class TransactionCreateRequest(BaseModel):
    """Solicitação de transação"""
    amount: float = Field(..., gt=0, description="Valor da transação")
    payment_method: PaymentMethod = Field(..., description="Método de pagamento")
    installments: int = Field(1, ge=1, le=12, description="Número de parcelas")
    description: Optional[str] = Field(None, description="Descrição da transação")
    customer_name: Optional[str] = Field(None, description="Nome do cliente")
    customer_document: Optional[str] = Field(None, description="CPF/CNPJ do cliente")
    
    class Config:
        schema_extra = {
            "example": {
                "amount": 25.50,
                "payment_method": "credit_card",
                "installments": 1,
                "description": "Banheira de Gelo - 30min",
                "customer_name": "João Silva",
                "customer_document": "12345678901"
            }
        }

class TerminalStatusResponse(BaseModel):
    """Status do terminal"""
    tenant_id: str
    terminal_type: Optional[str]
    status: str
    health: Optional[Dict[str, Any]]
    current_transaction: Optional[Dict[str, Any]]

class TransactionStatusResponse(BaseModel):
    """Status da transação"""
    transaction_id: str
    status: str
    amount: float
    payment_method: str
    authorization_code: Optional[str]
    nsu: Optional[str]
    receipt_customer: Optional[str]
    receipt_merchant: Optional[str]
    card_brand: Optional[str]
    card_last_digits: Optional[str]
    installments: int
    error_message: Optional[str]
    timestamp: str

# === Endpoints de Configuração ===

@router.post("/configure")
async def configure_terminal(
    config: TerminalConfigRequest,
    tenant_id: str = Depends(get_current_tenant)
):
    """Configura terminal para o tenant"""
    try:
        logger.info(f"🔧 Configuring terminal for tenant {tenant_id}")
        
        # Converte para dict
        config_dict = {
            "terminal": config.dict(exclude_none=True)
        }
        
        # Adiciona/atualiza terminal
        success = await terminal_manager.add_terminal(tenant_id, config_dict)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to configure terminal")
        
        return {
            "message": "Terminal configured successfully",
            "tenant_id": tenant_id,
            "terminal_type": config.type
        }
        
    except Exception as e:
        logger.error(f"❌ Error configuring terminal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/configure")
async def remove_terminal_config(
    tenant_id: str = Depends(get_current_tenant)
):
    """Remove configuração do terminal"""
    try:
        success = await terminal_manager.remove_terminal(tenant_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Terminal not found")
        
        return {"message": "Terminal configuration removed"}
        
    except Exception as e:
        logger.error(f"❌ Error removing terminal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === Endpoints de Status ===

@router.get("/status", response_model=TerminalStatusResponse)
async def get_terminal_status(
    tenant_id: str = Depends(get_current_tenant)
):
    """Obtém status do terminal"""
    try:
        status = await terminal_manager.get_terminal_status(tenant_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Terminal not found")
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Error getting terminal status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=List[TerminalStatusResponse])
async def list_all_terminals():
    """Lista todos os terminais (admin only)"""
    try:
        terminals = await terminal_manager.list_terminals()
        return terminals
        
    except Exception as e:
        logger.error(f"❌ Error listing terminals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_terminal_statistics():
    """Obtém estatísticas dos terminais"""
    try:
        stats = terminal_manager.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === Endpoints de Controle ===

@router.post("/connect")
async def connect_terminal(
    tenant_id: str = Depends(get_current_tenant)
):
    """Conecta terminal"""
    try:
        success = await terminal_manager.connect_terminal(tenant_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to connect terminal")
        
        return {"message": "Terminal connected successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error connecting terminal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disconnect")
async def disconnect_terminal(
    tenant_id: str = Depends(get_current_tenant)
):
    """Desconecta terminal"""
    try:
        success = await terminal_manager.disconnect_terminal(tenant_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to disconnect terminal")
        
        return {"message": "Terminal disconnected successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error disconnecting terminal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_terminal(
    tenant_id: str = Depends(get_current_tenant)
):
    """Reseta terminal"""
    try:
        success = await terminal_manager.reset_terminal(tenant_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reset terminal")
        
        return {"message": "Terminal reset successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error resetting terminal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === Endpoints de Transação ===

@router.post("/transaction")
async def start_transaction(
    request: TransactionCreateRequest,
    tenant_id: str = Depends(get_current_tenant)
):
    """Inicia transação no terminal"""
    try:
        # Converte para TransactionRequest
        transaction_request = TransactionRequest(
            amount=request.amount,
            payment_method=request.payment_method,
            installments=request.installments,
            description=request.description,
            customer_name=request.customer_name,
            customer_document=request.customer_document
        )
        
        transaction_id = await terminal_manager.start_transaction(tenant_id, transaction_request)
        
        return {
            "transaction_id": transaction_id,
            "message": "Transaction started successfully",
            "amount": request.amount,
            "payment_method": request.payment_method.value
        }
        
    except PaymentTerminalError as e:
        logger.error(f"❌ Terminal error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error starting transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transaction/{transaction_id}", response_model=TransactionStatusResponse)
async def get_transaction_status(
    transaction_id: str,
    tenant_id: str = Depends(get_current_tenant)
):
    """Obtém status da transação"""
    try:
        response = await terminal_manager.get_transaction_status(tenant_id, transaction_id)
        
        return TransactionStatusResponse(
            transaction_id=response.transaction_id,
            status=response.status.value,
            amount=response.amount,
            payment_method=response.payment_method.value,
            authorization_code=response.authorization_code,
            nsu=response.nsu,
            receipt_customer=response.receipt_customer,
            receipt_merchant=response.receipt_merchant,
            card_brand=response.card_brand,
            card_last_digits=response.card_last_digits,
            installments=response.installments,
            error_message=response.error_message,
            timestamp=response.timestamp.isoformat()
        )
        
    except PaymentTerminalError as e:
        logger.error(f"❌ Terminal error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error getting transaction status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transaction/{transaction_id}/cancel")
async def cancel_transaction(
    transaction_id: str,
    tenant_id: str = Depends(get_current_tenant)
):
    """Cancela transação"""
    try:
        success = await terminal_manager.cancel_transaction(tenant_id, transaction_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to cancel transaction")
        
        return {
            "message": "Transaction cancelled successfully",
            "transaction_id": transaction_id
        }
        
    except Exception as e:
        logger.error(f"❌ Error cancelling transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transaction/{transaction_id}/print")
async def print_receipt(
    transaction_id: str,
    receipt_type: str = "customer",
    tenant_id: str = Depends(get_current_tenant)
):
    """Imprime comprovante"""
    try:
        if receipt_type not in ["customer", "merchant"]:
            raise HTTPException(status_code=400, detail="Invalid receipt type")
        
        success = await terminal_manager.print_receipt(tenant_id, transaction_id, receipt_type)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to print receipt")
        
        return {
            "message": f"Receipt printed successfully",
            "transaction_id": transaction_id,
            "receipt_type": receipt_type
        }
        
    except Exception as e:
        logger.error(f"❌ Error printing receipt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === Endpoints de Teste ===

@router.post("/test/mock-transaction")
async def create_mock_transaction(
    amount: float = 10.0,
    tenant_id: str = Depends(get_current_tenant)
):
    """Cria transação de teste (apenas para terminais mock)"""
    try:
        terminal = terminal_manager.get_terminal(tenant_id)
        
        if not terminal or terminal.config.get("type") != "mock":
            raise HTTPException(status_code=400, detail="Mock terminal not configured")
        
        request = TransactionRequest(
            amount=amount,
            payment_method=PaymentMethod.CREDIT_CARD,
            description="Transação de teste",
            customer_name="Cliente Teste"
        )
        
        transaction_id = await terminal_manager.start_transaction(tenant_id, request)
        
        return {
            "transaction_id": transaction_id,
            "message": "Mock transaction created",
            "note": "Check status in a few seconds"
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating mock transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test/available-types")
async def get_available_terminal_types():
    """Lista tipos de terminal disponíveis"""
    try:
        from ..services.payment.terminal import TerminalAdapterFactory
        
        available = TerminalAdapterFactory.get_available_terminals()
        
        return {
            "available_terminals": available,
            "implemented": [k for k, v in available.items() if v],
            "pending": [k for k, v in available.items() if not v]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting available types: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 