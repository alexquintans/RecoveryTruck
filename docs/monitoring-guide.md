# 📊 Guia de Monitoramento - Sistema Totem

Este guia explica como usar cada serviço de monitoramento configurado no sistema Totem.

## 🏗️ Arquitetura de Monitoramento

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Totem     │    │   Node      │    │   API       │
│   Client    │    │  Exporter   │    │   Health    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌─────────────┐
                    │ Prometheus  │
                    │ (Coleta)    │
                    └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Grafana    │    │Alertmanager │    │   Jaeger    │
│(Dashboards) │    │ (Alertas)   │    │ (Tracing)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🔍 **1. Prometheus - Coleta de Métricas**

### O que faz:
- Coleta métricas de todos os serviços
- Armazena dados históricos
- Fornece linguagem de consulta (PromQL)
- Detecta problemas através de alertas

### Acessar:
- **URL**: http://localhost:9090
- **Função**: Visualizar métricas em tempo real

### Métricas Principais Monitoradas:

#### Sistema (Node Exporter):
```promql
# CPU Usage
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory Usage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100

# Disk Usage
(node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100
```

#### API (Totem):
```promql
# Taxa de requisições
rate(http_requests_total[5m])

# Tempo de resposta
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Taxa de erros
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

#### Tickets:
```promql
# Tickets criados por minuto
rate(totem_ticket_created_total[5m])

# Tempo médio de espera
rate(totem_ticket_wait_time_seconds_sum[5m]) / rate(totem_ticket_wait_time_seconds_count[5m])

# Comprimento da fila
totem_queue_length
```

#### Pagamentos:
```promql
# Taxa de sucesso de pagamentos
rate(totem_payment_processed_total{status="paid"}[5m]) / rate(totem_payment_processed_total[5m])

# Tempo de processamento
histogram_quantile(0.95, rate(totem_payment_processing_time_seconds_bucket[5m]))
```

## 📈 **2. Grafana - Dashboards e Visualização**

### O que faz:
- Cria dashboards visuais das métricas
- Permite análise de tendências
- Configura alertas visuais
- Exporta relatórios

### Acessar:
- **URL**: http://localhost:3000
- **Login**: admin / admin
- **Função**: Visualizar dashboards e configurar alertas

### Dashboards Disponíveis:

#### 1. **Dashboard Principal - Totem Overview**
- Métricas gerais do sistema
- Status dos serviços
- Performance da API
- Estatísticas de tickets e pagamentos

#### 2. **Dashboard de Performance**
- Tempo de resposta da API
- Uso de recursos do sistema
- Taxa de erros
- Throughput de requisições

#### 3. **Dashboard de Negócio**
- Tickets por serviço
- Receita por período
- Taxa de conversão
- Tempo médio de atendimento

### Como Criar Dashboards:

1. **Acesse o Grafana** (http://localhost:3000)
2. **Clique em "+" → "Dashboard"**
3. **Adicione painéis** com queries PromQL
4. **Configure alertas** nos painéis

### Exemplo de Query para Dashboard:
```promql
# Tickets criados hoje por hora
increase(totem_ticket_created_total[1h])

# Receita total do dia
sum(increase(totem_payment_amount_total{status="paid"}[24h]))
```

## 🚨 **3. Alertmanager - Gerenciamento de Alertas**

### O que faz:
- Recebe alertas do Prometheus
- Agrupa alertas similares
- Envia notificações por email/Slack
- Controla frequência de notificações

### Acessar:
- **URL**: http://localhost:9093
- **Função**: Gerenciar alertas e notificações

### Alertas Configurados:

#### Críticos (Imediatos):
- **API Down**: API não responde
- **High Error Rate**: Taxa de erro > 10%
- **Database Connection Failed**: Falha na conexão com banco

#### Avisos (5 minutos):
- **High Wait Time**: Tempo de espera > 30 min
- **Long Queue**: Fila > 10 pessoas
- **High CPU/Memory**: Uso > 80%
- **High Payment Processing Time**: Processamento > 60s

### Configurar Notificações:

#### Email:
```yaml
# Em alertmanager.yml
email_configs:
  - to: team@totem.com
    send_resolved: true
```

#### Slack:
```yaml
# Em alertmanager.yml
slack_configs:
  - channel: '#alerts'
    send_resolved: true
```

## 🔍 **4. Jaeger - Rastreamento Distribuído**

### O que faz:
- Rastreia requisições através de todos os serviços
- Identifica gargalos de performance
- Debug de problemas complexos
- Análise de dependências

### Acessar:
- **URL**: http://localhost:16686
- **Função**: Analisar traces de requisições

### Como Usar:

1. **Buscar Traces**:
   - Por serviço
   - Por operação
   - Por tempo
   - Por tags

2. **Analisar Spans**:
   - Tempo gasto em cada operação
   - Dependências entre serviços
   - Erros e exceções

3. **Identificar Gargalos**:
   - Operações lentas
   - Chamadas desnecessárias
   - Problemas de rede

### Exemplo de Trace:
```
POST /tickets
├── Validate Request (2ms)
├── Create Ticket (15ms)
│   ├── Database Insert (12ms)
│   └── Generate QR Code (3ms)
├── Create Payment Session (45ms)
│   ├── Call Payment Provider (40ms)
│   └── Save Session (5ms)
└── Send WebSocket Notification (1ms)
```

## 🛠️ **5. Como Configurar e Usar**

### Iniciar Todos os Serviços:
```bash
# Iniciar todos os containers
docker-compose up -d

# Verificar status
./check_monitoring.sh
```

### Configurar Variáveis de Ambiente:
```bash
# Copiar arquivo de exemplo
cp monitoring.env.example monitoring.env

# Editar configurações
nano monitoring.env
```

### Principais Configurações:

#### Email (Alertmanager):
```env
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=alerts@totem.com
SMTP_TO=team@totem.com
```

#### Slack (Opcional):
```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
SLACK_CHANNEL=#alerts
```

### Verificar Funcionamento:

1. **Execute o script de verificação**:
   ```bash
   chmod +x check_monitoring.sh
   ./check_monitoring.sh
   ```

2. **Acesse cada serviço**:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000
   - Jaeger: http://localhost:16686
   - Alertmanager: http://localhost:9093

3. **Teste métricas da API**:
   ```bash
   curl http://localhost:8000/metrics
   curl http://localhost:8000/health
   ```

## 📊 **6. Métricas de Negócio Importantes**

### KPIs Principais:
- **Tickets por hora**: `rate(totem_ticket_created_total[1h])`
- **Taxa de conversão**: `rate(totem_payment_processed_total{status="paid"}[1h]) / rate(totem_ticket_created_total[1h])`
- **Tempo médio de atendimento**: `histogram_quantile(0.5, rate(totem_ticket_wait_time_seconds_bucket[1h]))`
- **Receita por hora**: `rate(totem_payment_amount_total{status="paid"}[1h])`

### Alertas de Negócio:
- **Baixa conversão**: < 50% de tickets pagos
- **Fila muito longa**: > 10 pessoas esperando
- **Tempo de espera alto**: > 30 minutos
- **Falhas de pagamento**: > 10% de falhas

## 🔧 **7. Troubleshooting**

### Problemas Comuns:

#### Prometheus não coleta métricas:
```bash
# Verificar se a API está respondendo
curl http://localhost:8000/metrics

# Verificar configuração do Prometheus
docker logs prometheus
```

#### Grafana não conecta ao Prometheus:
```bash
# Verificar datasource
curl http://localhost:3000/api/datasources

# Verificar se Prometheus está acessível
curl http://prometheus:9090/api/v1/query?query=up
```

#### Alertmanager não envia emails:
```bash
# Verificar logs
docker logs alertmanager

# Testar configuração SMTP
telnet smtp.gmail.com 587
```

#### Jaeger não mostra traces:
```bash
# Verificar se OpenTelemetry está configurado
curl http://localhost:8000/health

# Verificar logs da API
docker logs api
```

## 📚 **8. Próximos Passos**

1. **Configurar notificações** (email/Slack)
2. **Criar dashboards personalizados** no Grafana
3. **Definir alertas específicos** para seu negócio
4. **Configurar retenção de dados** (Prometheus)
5. **Implementar métricas customizadas** na API
6. **Configurar backup** dos dados de monitoramento

---

**💡 Dica**: Comece monitorando as métricas básicas (CPU, memória, API) e gradualmente adicione métricas de negócio mais específicas conforme necessário. 