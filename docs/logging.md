# Sistema de Logs do Totem

Este documento descreve a configuração e uso do sistema de logs do Totem.

## Arquitetura de Logs

O sistema utiliza uma abordagem estruturada para logs:

- **StructuredLogger**: Classe principal para logging
- **OpenTelemetry**: Integração para tracing
- **JSON Format**: Logs em formato estruturado
- **Rotação de Logs**: Gerenciamento automático

## Níveis de Log

- **DEBUG**: Informações detalhadas para debugging
- **INFO**: Informações gerais de operação
- **WARNING**: Situações que requerem atenção
- **ERROR**: Erros que não impedem a operação
- **CRITICAL**: Erros que impedem a operação

## Estrutura do Log

```json
{
  "timestamp": "2024-03-14T10:00:00Z",
  "level": "INFO",
  "message": "Ticket created",
  "service": "totem-api",
  "environment": "production",
  "trace_id": "abc123",
  "span_id": "def456",
  "system": {
    "hostname": "totem-01",
    "pid": 1234,
    "thread_id": 5678
  },
  "context": {
    "ticket_id": "T123",
    "service_id": "S456",
    "user_id": "U789"
  }
}
```

## Configuração

### Variáveis de Ambiente

```env
LOG_LEVEL=INFO
SERVICE_NAME=totem-api
ENVIRONMENT=production
```

### OpenTelemetry

- Endpoint: Configurável via `OTLP_ENDPOINT`
- Insecure: Configurável via `OTLP_INSECURE`
- Service Name: Configurável via `SERVICE_NAME`

## Uso do Logger

### Exemplo Básico

```python
from services.logging import logger

logger.info("Ticket created", ticket_id="T123")
```

### Com Contexto

```python
logger.info(
    "Payment processed",
    payment_id="P123",
    amount=100.00,
    status="success"
)
```

### Com Exceção

```python
try:
    process_payment()
except PaymentError as e:
    logger.error(
        "Payment failed",
        payment_id="P123",
        error=str(e),
        exc_info=True
    )
```

### Com Span

```python
@logger.with_span("process_payment")
def process_payment(payment_id: str):
    logger.info("Processing payment", payment_id=payment_id)
    # ... processamento ...
```

## Rotação de Logs

- **Tamanho Máximo**: 100MB por arquivo
- **Backups**: 5 arquivos de backup
- **Compressão**: Gzip
- **Frequência**: Diária

## Integração com Monitoramento

### Métricas de Log

- `log_entries_total`: Total de entradas de log
- `log_errors_total`: Total de erros
- `log_warnings_total`: Total de warnings

### Alertas

- Taxa de erros > 10%
- Taxa de warnings > 20%
- Falha na rotação de logs

## Boas Práticas

1. **Contexto**
   - Sempre incluir IDs relevantes
   - Adicionar métricas quando apropriado
   - Usar campos consistentes

2. **Níveis**
   - DEBUG: Desenvolvimento local
   - INFO: Operação normal
   - WARNING: Situações anormais
   - ERROR: Falhas recuperáveis
   - CRITICAL: Falhas críticas

3. **Performance**
   - Evitar logging excessivo
   - Usar níveis apropriados
   - Incluir apenas dados necessários

4. **Segurança**
   - Não logar dados sensíveis
   - Sanitizar inputs
   - Usar máscaras quando necessário

## Troubleshooting

### Problemas Comuns

1. **Logs não aparecem**
   - Verificar nível de log
   - Confirmar permissões
   - Validar configuração

2. **Performance**
   - Verificar rotação
   - Otimizar formato
   - Ajustar buffer

3. **Espaço em Disco**
   - Verificar retenção
   - Ajustar rotação
   - Limpar logs antigos

### Comandos Úteis

```bash
# Ver logs em tempo real
tail -f /var/log/totem/app.log

# Contar erros
grep -c "ERROR" /var/log/totem/app.log

# Buscar por ID
grep "T123" /var/log/totem/app.log

# Analisar distribuição de níveis
awk '{print $3}' /var/log/totem/app.log | sort | uniq -c
```

## Manutenção

### Backup
- Logs: Diário
- Configurações: Versionadas
- Rotação: Automática

### Limpeza
- Logs antigos: 30 dias
- Backups: 90 dias
- Métricas: 15 dias 