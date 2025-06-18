# 🎯 Sistema de Fila Avançado - Totem RecoveryTruck

## Visão Geral

O **Sistema de Fila Avançado** é uma solução completa para gerenciamento inteligente de tickets no sistema Totem. Ele resolve os problemas identificados na análise inicial e implementa funcionalidades avançadas de priorização, ordenação e monitoramento.

## 🔧 Problemas Resolvidos

### ❌ Problema Original
```python
# Sistema antigo - muito simples
@router.get("/queue")
async def get_queue():
    tickets = db.query(Ticket).filter(
        Ticket.status == "paid",  # ❌ Muito simples
        Ticket.called_at == None
    )
    # ❌ FALTA: priorização, ordenação por serviço, etc.
```

### ✅ Solução Implementada
- **Priorização inteligente** baseada em regras de negócio
- **Múltiplas ordenações** (FIFO, prioridade, serviço, tempo de espera)
- **Filtros avançados** por serviço, prioridade e status
- **Estimativas de tempo** precisas
- **Estatísticas em tempo real**
- **Atribuição de operadores**
- **Auto-expiração** de tickets antigos

## 🏗️ Arquitetura

### Componentes Principais

1. **QueueManager** (`services/queue_manager.py`)
   - Gerenciador central da fila
   - Lógica de priorização e ordenação
   - Cálculo de estimativas

2. **Constantes de Fila** (`constants.py`)
   - Configurações e regras
   - Enums de prioridade e ordenação
   - Tempos de referência

3. **Modelos Estendidos** (`models.py`)
   - Campos de prioridade e fila
   - Timestamps detalhados
   - Relacionamentos com operadores

4. **Schemas Avançados** (`schemas.py`)
   - `TicketInQueue` com informações enriquecidas
   - `QueueSettings` para configuração
   - Validações automáticas

## 🎯 Funcionalidades

### 1. Sistema de Priorização

```python
class QueuePriority(str, Enum):
    HIGH = "high"      # Alta prioridade (problemas, reimpressões)
    NORMAL = "normal"  # Prioridade normal
    LOW = "low"        # Baixa prioridade (expirados reativados)
```

**Regras de Priorização:**
- **Alta**: Tickets com erro de impressão, múltiplas tentativas
- **Normal**: Tickets regulares na fila
- **Baixa**: Tickets reativados após expiração
- **Boost automático**: Tickets antigos ganham prioridade

### 2. Ordenações Disponíveis

```python
class QueueSortOrder(str, Enum):
    FIFO = "fifo"                   # First In, First Out (padrão)
    PRIORITY = "priority"           # Por prioridade
    SERVICE = "service"             # Por tipo de serviço
    WAITING_TIME = "waiting_time"   # Por tempo de espera
```

### 3. Estimativas Inteligentes

- **Tempo de espera** baseado na posição na fila
- **Capacidade paralela** considerando equipamentos disponíveis
- **Duração do serviço** específica por tipo
- **Tickets em progresso** afetam estimativas

### 4. Monitoramento e Estatísticas

```json
{
  "total_active": 15,
  "by_status": {
    "in_queue": 8,
    "called": 3,
    "in_progress": 4
  },
  "by_priority": {
    "high": 2,
    "normal": 11,
    "low": 2
  },
  "waiting_times": {
    "average_minutes": 12.5,
    "maximum_minutes": 35.0,
    "total_estimated_minutes": 180
  },
  "queue_health": {
    "status": "healthy",
    "message": "Fila funcionando normalmente",
    "recommendations": ["✅ Fila funcionando bem"]
  }
}
```

## 🚀 Endpoints da API

### 1. Fila Principal
```http
GET /tickets/queue?sort_order=priority&service_id=uuid&priority_filter=high
```

**Parâmetros:**
- `sort_order`: Ordenação (fifo, priority, service, waiting_time)
- `service_id`: Filtrar por serviço específico
- `priority_filter`: Filtrar por prioridade
- `include_called`: Incluir tickets chamados
- `include_in_progress`: Incluir tickets em progresso

### 2. Próximo Ticket
```http
GET /tickets/queue/next
```
Retorna o próximo ticket para o operador atual baseado em prioridade e disponibilidade.

### 3. Atribuir Ticket
```http
POST /tickets/queue/assign/{ticket_id}?operator_id=uuid
```
Atribui um ticket específico a um operador.

### 4. Auto-Expiração
```http
POST /tickets/queue/auto-expire
```
Expira automaticamente tickets antigos baseado na configuração.

### 5. Estatísticas
```http
GET /tickets/queue/statistics
```
Retorna estatísticas detalhadas da fila e saúde do sistema.

## ⚙️ Configurações

### Configurações da Fila (`QUEUE_CONFIG`)
```python
QUEUE_CONFIG = {
    "max_waiting_time_minutes": 60,        # Tempo máximo na fila
    "priority_boost_minutes": 30,          # Tempo para boost de prioridade
    "service_parallel_limit": 3,           # Máximo simultâneo por serviço
    "operator_concurrent_limit": 2,        # Máximo por operador
    "auto_expire_enabled": True,           # Auto-expirar tickets
    "priority_enabled": True               # Sistema de prioridades ativo
}
```

### Tempos de Referência (`QUEUE_TIMINGS`)
```python
QUEUE_TIMINGS = {
    "normal_waiting": 15,           # Tempo normal de espera
    "warning_waiting": 30,          # Tempo de alerta
    "critical_waiting": 45,         # Tempo crítico
    "auto_expire": 60,              # Auto-expirar após este tempo
    "service_duration": {           # Duração por serviço
        "default": 10,
        "banheira_gelo": 10,
        "bota_compressao": 10
    }
}
```

## 🔄 Fluxo de Funcionamento

### 1. Entrada na Fila
```
Pagamento Confirmado → Ticket Criado → Impressão → IN_QUEUE
```

### 2. Priorização Automática
```python
def calculate_priority(ticket_status, waiting_minutes, print_attempts):
    if ticket_status == PRINT_ERROR or print_attempts > 1:
        return QueuePriority.HIGH
    
    if waiting_minutes > CRITICAL_WAITING:
        return QueuePriority.HIGH
    
    return QueuePriority.NORMAL
```

### 3. Ordenação e Posicionamento
```
1. Aplicar filtros (serviço, prioridade)
2. Ordenar conforme critério escolhido
3. Calcular posições na fila
4. Estimar tempos de espera
5. Atualizar estatísticas
```

### 4. Atendimento
```
IN_QUEUE → CALLED → IN_PROGRESS → COMPLETED
```

## 📊 Monitoramento

### Saúde da Fila
- **Healthy**: Tempo médio ≤ 15min, sem tickets críticos
- **Warning**: Tempo médio ≤ 30min, poucos tickets críticos
- **Critical**: Tempo médio > 30min ou muitos tickets críticos

### Métricas Importantes
- **Taxa de conversão**: Tickets que chegam ao atendimento
- **Tempo médio de espera**: Performance geral
- **Tickets críticos**: Problemas que precisam atenção
- **Capacidade utilizada**: Eficiência dos equipamentos

### Recomendações Automáticas
- 🚨 Ação imediata necessária
- ⚠️ X tickets com alta prioridade
- ⏰ X tickets esperando há muito tempo
- 📈 Considere adicionar mais operadores
- ✅ Fila funcionando bem

## 🎨 Interface do Operador

### Dashboard da Fila
```json
{
  "next_ticket": {
    "ticket_number": 1001,
    "customer_name": "João Silva",
    "service": "Banheira de Gelo",
    "priority": "high",
    "waiting_time": "25 minutos",
    "estimated_service": "10 minutos"
  },
  "queue_summary": {
    "total_waiting": 8,
    "high_priority": 2,
    "average_wait": "12 minutos",
    "estimated_clear_time": "2 horas"
  }
}
```

### Filtros e Ordenação
- **Por Serviço**: Mostrar apenas Banheira de Gelo
- **Por Prioridade**: Focar em tickets críticos
- **Por Tempo**: Ver quem está esperando mais
- **Chamados**: Incluir tickets já chamados

## 🔧 Manutenção

### Tarefas Automáticas
- **Auto-expiração**: Tickets antigos são expirados automaticamente
- **Boost de prioridade**: Tickets antigos ganham prioridade
- **Limpeza de atribuições**: Remove atribuições de operadores inativos
- **Recálculo de estimativas**: Atualiza tempos baseado na situação atual

### Comandos Úteis
```python
# Expirar tickets antigos manualmente
queue_manager.auto_expire_old_tickets(tenant_id)

# Obter próximo ticket para operador
next_ticket = queue_manager.get_next_ticket_for_operator(tenant_id, operator_id)

# Atualizar prioridades
queue_manager._update_queue_priorities(tickets)

# Estatísticas completas
stats = queue_manager.get_queue_statistics(tenant_id)
```

## 🚀 Benefícios Implementados

### Para Operadores
- **Visão clara** da fila com prioridades
- **Próximo ticket** sugerido automaticamente
- **Estimativas precisas** de tempo
- **Filtros úteis** para organização
- **Estatísticas** para tomada de decisão

### Para Clientes
- **Tempo de espera** mais previsível
- **Priorização justa** com regras claras
- **Atendimento eficiente** com menos espera
- **Transparência** no processo

### Para o Sistema
- **Performance otimizada** com ordenação inteligente
- **Monitoramento completo** da operação
- **Escalabilidade** para múltiplos operadores
- **Manutenção automática** da fila
- **Métricas detalhadas** para análise

## 📈 Próximos Passos

1. **Interface Web** para visualização da fila
2. **Notificações push** para operadores
3. **Integração com displays** para clientes
4. **Machine Learning** para otimização de estimativas
5. **Relatórios avançados** de performance

---

**Status**: ✅ **Implementado e Funcional**

O Sistema de Fila Avançado resolve completamente o problema identificado na análise inicial, fornecendo uma solução robusta, inteligente e escalável para gerenciamento de tickets no sistema Totem. 