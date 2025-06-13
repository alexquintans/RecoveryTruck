# Padrões de Resiliência do Totem

Este documento descreve os padrões de resiliência implementados no sistema Totem.

## Circuit Breaker

O Circuit Breaker é um padrão que previne falhas em cascata, isolando serviços problemáticos.

### Configuração

```python
circuit_breaker = CircuitBreaker(
    name="payment_processor",
    failure_threshold=5,
    reset_timeout=60,
    half_open_timeout=30
)
```

### Estados

1. **CLOSED**: Operação normal
2. **OPEN**: Bloqueia requisições
3. **HALF-OPEN**: Permite requisições de teste

### Métricas

- `circuit_breaker_state`: Estado atual
- `circuit_breaker_failures`: Total de falhas
- `circuit_breaker_success_rate`: Taxa de sucesso

## Retry

O padrão Retry permite tentativas automáticas em caso de falhas temporárias.

### Configuração

```python
retry = Retry(
    name="payment_retry",
    max_attempts=3,
    initial_delay=1,
    max_delay=10,
    backoff_factor=2
)
```

### Estratégias

1. **Exponential Backoff**: Aumenta o delay exponencialmente
2. **Jitter**: Adiciona aleatoriedade ao delay
3. **Max Attempts**: Limita o número de tentativas

### Métricas

- `retry_attempts_total`: Total de tentativas
- `retry_success_total`: Total de sucessos
- `retry_delay_seconds`: Tempo de espera

## Uso

### Circuit Breaker

```python
@circuit_breaker.execute
async def process_payment(payment_id: str):
    # ... processamento ...
```

### Retry

```python
@retry.execute
async def send_notification(user_id: str):
    # ... envio ...
```

### Combinando Padrões

```python
@circuit_breaker.execute
@retry.execute
async def critical_operation():
    # ... operação crítica ...
```

## Monitoramento

### Alertas

1. **Circuit Breaker**
   - Estado OPEN por > 5 minutos
   - Taxa de sucesso < 80%
   - Falhas consecutivas > 10

2. **Retry**
   - Tentativas > 5 em 1 minuto
   - Taxa de sucesso < 50%
   - Delay médio > 30 segundos

### Dashboards

1. **Circuit Breaker**
   - Estado atual
   - Taxa de sucesso
   - Total de falhas
   - Tempo em cada estado

2. **Retry**
   - Tentativas por minuto
   - Taxa de sucesso
   - Delay médio
   - Distribuição de erros

## Boas Práticas

1. **Configuração**
   - Ajustar thresholds baseado em métricas
   - Monitorar impactos
   - Documentar decisões

2. **Logging**
   - Registrar mudanças de estado
   - Incluir contexto
   - Rastrear tentativas

3. **Testes**
   - Simular falhas
   - Verificar recuperação
   - Validar métricas

4. **Manutenção**
   - Revisar configurações
   - Ajustar thresholds
   - Limpar métricas antigas

## Troubleshooting

### Problemas Comuns

1. **Circuit Breaker**
   - Falso positivo
   - Falso negativo
   - Oscilação de estado

2. **Retry**
   - Muitas tentativas
   - Delay muito longo
   - Falha persistente

### Soluções

1. **Circuit Breaker**
   - Ajustar thresholds
   - Implementar fallback
   - Melhorar detecção

2. **Retry**
   - Otimizar backoff
   - Adicionar jitter
   - Limitar tentativas

## Manutenção

### Backup
- Configurações: Versionadas
- Métricas: 15 dias
- Logs: 30 dias

### Limpeza
- Métricas antigas: 15 dias
- Logs: 30 dias
- Estados: Reset diário

## Exemplos

### Circuit Breaker

```python
# Configuração
circuit_breaker = CircuitBreaker(
    name="payment_processor",
    failure_threshold=5,
    reset_timeout=60
)

# Uso
@circuit_breaker.execute
async def process_payment(payment_id: str):
    try:
        result = await payment_processor.process(payment_id)
        return result
    except PaymentError as e:
        logger.error("Payment failed", payment_id=payment_id, error=str(e))
        raise
```

### Retry

```python
# Configuração
retry = Retry(
    name="notification_retry",
    max_attempts=3,
    initial_delay=1,
    max_delay=10
)

# Uso
@retry.execute
async def send_notification(user_id: str):
    try:
        await notification_service.send(user_id)
    except NotificationError as e:
        logger.warning("Notification failed", user_id=user_id, error=str(e))
        raise
```

### Combinando Padrões

```python
# Configuração
circuit_breaker = CircuitBreaker(name="critical_operation")
retry = Retry(name="critical_operation")

# Uso
@circuit_breaker.execute
@retry.execute
async def critical_operation():
    try:
        result = await service.execute()
        return result
    except ServiceError as e:
        logger.error("Operation failed", error=str(e))
        raise
``` 