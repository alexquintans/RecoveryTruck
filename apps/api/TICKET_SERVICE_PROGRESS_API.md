# APIs de Progresso de Serviços do Ticket

## Visão Geral

Este documento descreve as APIs para gerenciar o progresso individual de cada serviço em um ticket com múltiplos serviços.

## Endpoints

### 1. Obter Progresso de Serviços de um Ticket

**GET** `/api/ticket-service-progress/ticket/{ticket_id}`

Obtém o progresso de todos os serviços de um ticket específico.

#### Parâmetros:
- `ticket_id` (UUID): ID do ticket

#### Resposta:
```json
{
  "items": [
    {
      "id": "uuid",
      "ticket_service_id": "uuid",
      "status": "pending|in_progress|completed|cancelled",
      "duration_minutes": 15,
      "operator_notes": "Observações do operador",
      "equipment_id": "uuid",
      "started_at": "2024-01-01T10:00:00Z",
      "completed_at": "2024-01-01T10:15:00Z",
      "created_at": "2024-01-01T09:00:00Z",
      "updated_at": "2024-01-01T10:15:00Z",
      "service_name": "Crioterapia",
      "service_price": 80.00,
      "equipment_name": "crioterapia_1"
    }
  ],
  "total": 1
}
```

### 2. Iniciar Progresso de um Serviço

**POST** `/api/ticket-service-progress/{progress_id}/start`

Inicia o progresso de um serviço específico.

#### Parâmetros:
- `progress_id` (UUID): ID do progresso do serviço
- `equipment_id` (UUID, opcional): ID do equipamento a ser usado

#### Resposta:
```json
{
  "id": "uuid",
  "ticket_service_id": "uuid",
  "status": "in_progress",
  "duration_minutes": 15,
  "operator_notes": "Iniciado por João Silva",
  "equipment_id": "uuid",
  "started_at": "2024-01-01T10:00:00Z",
  "completed_at": null,
  "created_at": "2024-01-01T09:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### 3. Completar Progresso de um Serviço

**POST** `/api/ticket-service-progress/{progress_id}/complete`

Completa o progresso de um serviço específico.

#### Parâmetros:
- `progress_id` (UUID): ID do progresso do serviço
- `operator_notes` (string, opcional): Observações do operador

#### Resposta:
```json
{
  "id": "uuid",
  "ticket_service_id": "uuid",
  "status": "completed",
  "duration_minutes": 15,
  "operator_notes": "Serviço concluído com sucesso",
  "equipment_id": "uuid",
  "started_at": "2024-01-01T10:00:00Z",
  "completed_at": "2024-01-01T10:15:00Z",
  "created_at": "2024-01-01T09:00:00Z",
  "updated_at": "2024-01-01T10:15:00Z"
}
```

### 4. Cancelar Progresso de um Serviço

**POST** `/api/ticket-service-progress/{progress_id}/cancel`

Cancela o progresso de um serviço específico.

#### Parâmetros:
- `progress_id` (UUID): ID do progresso do serviço
- `reason` (string): Motivo do cancelamento

#### Resposta:
```json
{
  "id": "uuid",
  "ticket_service_id": "uuid",
  "status": "cancelled",
  "duration_minutes": 15,
  "operator_notes": "Cancelado por João Silva: Cliente desistiu",
  "equipment_id": null,
  "started_at": null,
  "completed_at": null,
  "created_at": "2024-01-01T09:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### 5. Atualizar Progresso de um Serviço

**PATCH** `/api/ticket-service-progress/{progress_id}`

Atualiza campos específicos do progresso de um serviço.

#### Parâmetros:
- `progress_id` (UUID): ID do progresso do serviço
- Body: Objeto com campos opcionais para atualizar

#### Resposta:
```json
{
  "id": "uuid",
  "ticket_service_id": "uuid",
  "status": "in_progress",
  "duration_minutes": 15,
  "operator_notes": "Observações atualizadas",
  "equipment_id": "uuid",
  "started_at": "2024-01-01T10:00:00Z",
  "completed_at": null,
  "created_at": "2024-01-01T09:00:00Z",
  "updated_at": "2024-01-01T10:05:00Z"
}
```

## Status dos Serviços

- **pending**: Serviço aguardando para ser iniciado
- **in_progress**: Serviço em andamento
- **completed**: Serviço concluído
- **cancelled**: Serviço cancelado

## Fluxo de Trabalho

1. **Ticket criado** → Todos os serviços ficam com status `pending`
2. **Operador inicia serviço** → Status muda para `in_progress`
3. **Operador completa serviço** → Status muda para `completed`
4. **Se cancelado** → Status muda para `cancelled`

## Autenticação

Todas as APIs requerem autenticação via Bearer token e header `X-Tenant-Id`.

## Exemplo de Uso

```bash
# 1. Obter progresso de um ticket
curl -X GET "http://localhost:8000/api/ticket-service-progress/ticket/123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Tenant-Id: YOUR_TENANT_ID"

# 2. Iniciar um serviço
curl -X POST "http://localhost:8000/api/ticket-service-progress/456e7890-e89b-12d3-a456-426614174000/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Tenant-Id: YOUR_TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{"equipment_id": "789e0123-e89b-12d3-a456-426614174000"}'

# 3. Completar um serviço
curl -X POST "http://localhost:8000/api/ticket-service-progress/456e7890-e89b-12d3-a456-426614174000/complete" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Tenant-Id: YOUR_TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{"operator_notes": "Serviço concluído com sucesso"}'
``` 