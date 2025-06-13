from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Optional
from datetime import datetime, timedelta
from ..services.metrics import MetricsService
from ..services.auth import get_current_operator
from ..models.operator import Operator
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/metrics/daily")
async def get_daily_metrics(
    date: Optional[datetime] = None,
    current_operator: Operator = Depends(get_current_operator),
    db: Session = Depends(get_db)
):
    """Obtém métricas diárias para o tenant do operador"""
    metrics_service = MetricsService(db)
    return await metrics_service.get_daily_metrics(current_operator.tenant_id, date)

@router.get("/metrics/service/{service_id}")
async def get_service_metrics(
    service_id: str,
    days: int = 30,
    current_operator: Operator = Depends(get_current_operator),
    db: Session = Depends(get_db)
):
    """Obtém métricas específicas de um serviço"""
    metrics_service = MetricsService(db)
    return await metrics_service.get_service_metrics(
        current_operator.tenant_id,
        service_id,
        days
    )

@router.get("/metrics/export")
async def export_metrics(
    start_date: datetime,
    end_date: datetime,
    current_operator: Operator = Depends(get_current_operator),
    db: Session = Depends(get_db)
):
    """Exporta métricas em formato CSV"""
    metrics_service = MetricsService(db)
    csv_data = await metrics_service.export_metrics_csv(
        current_operator.tenant_id,
        start_date,
        end_date
    )
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=metrics_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
        }
    )

@router.get("/metrics/queue")
async def get_queue_metrics(
    current_operator: Operator = Depends(get_current_operator),
    db: Session = Depends(get_db)
):
    """Obtém métricas da fila atual"""
    # Implementar lógica para obter métricas da fila
    # Por exemplo: tempo médio de espera, número de pessoas na fila, etc.
    pass

@router.get("/metrics/performance")
async def get_performance_metrics(
    current_operator: Operator = Depends(get_current_operator),
    db: Session = Depends(get_db)
):
    """Obtém métricas de performance do sistema"""
    # Implementar lógica para obter métricas de performance
    # Por exemplo: tempo de resposta da API, uso de recursos, etc.
    pass 