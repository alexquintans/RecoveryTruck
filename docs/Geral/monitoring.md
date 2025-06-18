# Monitoramento do Sistema Totem

Este documento descreve a configuração e práticas de monitoramento implementadas no sistema Totem.

## Visão Geral

O sistema de monitoramento do Totem é composto por:

- **Prometheus**: Coleta e armazena métricas
- **Grafana**: Visualização e dashboards
- **AlertManager**: Gerenciamento de alertas
- **OpenTelemetry**: Rastreamento distribuído
- **Node Exporter**: Métricas do sistema

## Métricas

### 1. Métricas de Aplicação

```python
# Contadores
TICKET_CREATED = Counter(
    'totem_ticket_created_total',
    'Total de tickets criados'
)

TICKET_COMPLETED = Counter(
    'totem_ticket_completed_total',
    'Total de tickets completados'
)

# Histogramas
TICKET_WAIT_TIME = Histogram(
    'totem_ticket_wait_time_seconds',
    'Tempo de espera dos tickets',
    buckets=[30, 60, 120, 300, 600]
)

# Gauges
QUEUE_LENGTH = Gauge(
    'totem_queue_length',
    'Número de tickets na fila'
)
```

### 2. Métricas de Sistema

```yaml
# Node Exporter
node_cpu_seconds_total
node_memory_MemTotal_bytes
node_filesystem_size_bytes
node_network_transmit_bytes_total
```

### 3. Métricas de Negócio

```python
# Pagamentos
PAYMENT_PROCESSED = Counter(
    'totem_payment_processed_total',
    'Total de pagamentos processados',
    ['status', 'method']
)

PAYMENT_AMOUNT = Histogram(
    'totem_payment_amount',
    'Valor dos pagamentos',
    buckets=[10, 50, 100, 500, 1000]
)

# Serviços
SERVICE_USAGE = Counter(
    'totem_service_usage_total',
    'Uso dos serviços',
    ['service', 'status']
)
```

## Dashboards

### 1. Visão Geral

```json
{
  "dashboard": {
    "title": "Totem Overview",
    "panels": [
      {
        "title": "Tickets",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(totem_ticket_created_total[5m])",
            "legendFormat": "Criados"
          },
          {
            "expr": "rate(totem_ticket_completed_total[5m])",
            "legendFormat": "Completados"
          }
        ]
      },
      {
        "title": "Pagamentos",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(totem_payment_processed_total[5m])",
            "legendFormat": "Processados"
          }
        ]
      }
    ]
  }
}
```

### 2. Performance

```json
{
  "dashboard": {
    "title": "Performance",
    "panels": [
      {
        "title": "Tempo de Resposta",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(totem_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          }
        ]
      },
      {
        "title": "Uso de CPU",
        "type": "gauge",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)",
            "legendFormat": "CPU"
          }
        ]
      }
    ]
  }
}
```

### 3. Negócio

```json
{
  "dashboard": {
    "title": "Métricas de Negócio",
    "panels": [
      {
        "title": "Volume de Pagamentos",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(totem_payment_amount_sum)",
            "legendFormat": "Total"
          }
        ]
      },
      {
        "title": "Serviços Populares",
        "type": "table",
        "targets": [
          {
            "expr": "topk(5, sum by (service) (totem_service_usage_total))",
            "legendFormat": "{{service}}"
          }
        ]
      }
    ]
  }
}
```

## Alertas

### 1. Configuração

```yaml
groups:
  - name: totem_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(totem_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta taxa de erros"
          description: "Taxa de erros acima de 10% nos últimos 5 minutos"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(totem_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alta latência"
          description: "Latência p95 acima de 1s nos últimos 5 minutos"
```

### 2. Notificações

```yaml
receivers:
  - name: 'team-totem'
    email_configs:
      - to: 'team@totem.example.com'
        from: 'alerts@totem.example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts'
        auth_password: 'password'

    slack_configs:
      - channel: '#totem-alerts'
        api_url: 'https://hooks.slack.com/services/...'
```

## Rastreamento

### 1. OpenTelemetry

```python
# Configuração
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter

# Inicialização
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Exportador
otlp_exporter = OTLPSpanExporter(
    endpoint="localhost:4317",
    insecure=True
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
```

### 2. Instrumentação

```python
# Decorator de tracing
def trace_span(name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                span.set_attribute("service.name", "totem-api")
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator

# Uso
@trace_span("process_payment")
async def process_payment(payment: Payment):
    # Processamento
    pass
```

## Logs

### 1. Configuração

```python
# Estrutura de logs
LOG_FORMAT = {
    "timestamp": "%(asctime)s",
    "level": "%(levelname)s",
    "message": "%(message)s",
    "service": "totem-api",
    "trace_id": "%(otelTraceID)s",
    "span_id": "%(otelSpanID)s"
}

# Configuração
logging.basicConfig(
    level=logging.INFO,
    format=json.dumps(LOG_FORMAT),
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("totem.log")
    ]
)
```

### 2. Rotação

```python
# Configuração de rotação
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "totem.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

## Health Checks

### 1. API

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "checks": {
            "database": await check_database(),
            "redis": await check_redis(),
            "printer": await check_printer()
        }
    }
```

### 2. Sistema

```yaml
# Docker Compose
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Manutenção

### 1. Backup

```python
# Backup de métricas
async def backup_metrics():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = f"metrics_{timestamp}.json"
    
    # Exporta métricas
    metrics = await prometheus_client.generate_latest()
    
    # Salva backup
    with open(backup_file, "wb") as f:
        f.write(metrics)
```

### 2. Limpeza

```python
# Limpeza de dados antigos
async def cleanup_old_data():
    # Remove métricas antigas
    await prometheus_client.delete_series(
        match[]={
            "job": "totem",
            "timestamp": "< now() - 30d"
        }
    )
    
    # Remove logs antigos
    for log_file in glob.glob("totem.log.*"):
        if os.path.getmtime(log_file) < time.time() - 30*24*60*60:
            os.remove(log_file)
```

## Troubleshooting

### 1. Problemas Comuns

1. **Métricas não aparecem**
   - Verificar configuração do Prometheus
   - Verificar endpoints expostos
   - Verificar labels

2. **Alertas não funcionam**
   - Verificar regras
   - Verificar thresholds
   - Verificar notificações

3. **Logs não aparecem**
   - Verificar permissões
   - Verificar rotação
   - Verificar formato

### 2. Soluções

1. **Métricas**
   ```bash
   # Verificar endpoints
   curl localhost:8000/metrics
   
   # Verificar configuração
   promtool check config prometheus.yml
   ```

2. **Alertas**
   ```bash
   # Verificar regras
   promtool check rules alert.rules
   
   # Testar notificações
   amtool test-receivers
   ```

3. **Logs**
   ```bash
   # Verificar logs
   tail -f totem.log
   
   # Verificar rotação
   ls -l totem.log*
   ```

## Checklist

### Diário

- [ ] Verificar dashboards
- [ ] Verificar alertas
- [ ] Verificar logs
- [ ] Verificar métricas

### Semanal

- [ ] Revisar thresholds
- [ ] Atualizar dashboards
- [ ] Limpar dados antigos
- [ ] Verificar backups

### Mensal

- [ ] Revisar configuração
- [ ] Atualizar documentação
- [ ] Treinar equipe
- [ ] Relatório de performance 