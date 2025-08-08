# 🔌 Como Usar o Novo WebSocket no Projeto

## 🎯 **Problema Identificado e Solucionado**

### **❌ Problema Original:**
```
WebSocket connection to 'wss://recoverytruck-production.up.railway.app/?tenant_id=7f02a566-2406-436d-b10d-90ecddd3fe2d&client_type=operator&token=...' failed
```

### **✅ Solução Aplicada:**
- **URL Corrigida:** `wss://recoverytruck-production.up.railway.app/ws?tenant_id=...`
- **Proteções Robustas:** Error boundaries, reconexão automática, validação de dados
- **Reabilitação Gradual:** WebSocket só conecta após dados estarem prontos

## 🚀 **3 Níveis de Implementação**

### **1. 🎯 Implementação Rápida (Recomendada)**

```typescript
// apps/panel-client/src/pages/OperatorPage.tsx
import { useTicketQueueComplete } from '../hooks/useTicketQueueComplete';
import { WebSocketErrorBoundary } from '@totem/hooks';

const OperatorPage: React.FC = () => {
  const { 
    loadingState, 
    tickets, 
    myTickets, 
    equipment, 
    operationConfig, 
    webSocket,
    refetch 
  } = useTicketQueueComplete();

  // Loading state automático
  if (loadingState !== 'ready') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">
            {loadingState === 'initial' && 'Inicializando...'}
            {loadingState === 'loading' && 'Carregando dados...'}
            {loadingState === 'error' && 'Erro ao carregar dados'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <WebSocketErrorBoundary>
      <div className="p-6">
        {/* Status do WebSocket */}
        <div className="flex items-center space-x-4 mb-4">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              webSocket.isConnected ? 'bg-green-500' : 
              webSocket.isConnecting ? 'bg-yellow-500' : 
              webSocket.isError ? 'bg-red-500' : 'bg-gray-400'
            }`}></div>
            <span className="text-sm text-gray-600">
              {webSocket.isConnected && 'Conectado'}
              {webSocket.isConnecting && 'Conectando...'}
              {webSocket.isError && 'Erro de conexão'}
              {webSocket.isReconnecting && 'Reconectando...'}
              {!webSocket.isConnected && !webSocket.isConnecting && !webSocket.isError && 'Desconectado'}
            </span>
          </div>
          
          {webSocket.isError && (
            <button
              onClick={webSocket.reconnect}
              className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
            >
              Reconectar
            </button>
          )}
        </div>

        {/* Seu conteúdo aqui */}
        <h1 className="text-2xl font-bold mb-4">Painel do Operador</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold mb-2">Tickets na Fila</h3>
            <p className="text-3xl font-bold text-blue-600">{tickets.length}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold mb-2">Meus Tickets</h3>
            <p className="text-3xl font-bold text-green-600">{myTickets.length}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold mb-2">Equipamentos</h3>
            <p className="text-3xl font-bold text-purple-600">{equipment.length}</p>
          </div>
        </div>

        {/* Lista de Tickets */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">
              Tickets na Fila ({tickets.length})
            </h2>
          </div>
          
          <div className="divide-y divide-gray-200">
            {tickets.map((ticket: any) => (
              <div key={ticket.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium">
                      Ticket #{ticket.ticket_number || ticket.number}
                    </h3>
                    <p className="text-sm text-gray-600">
                      Status: {ticket.status}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">
                      {ticket.created_at ? new Date(ticket.created_at).toLocaleTimeString() : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
            
            {tickets.length === 0 && (
              <div className="px-6 py-8 text-center">
                <p className="text-gray-500">Nenhum ticket na fila</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </WebSocketErrorBoundary>
  );
};

export default OperatorPage;
```

### **2. 🔧 Implementação Personalizada**

```typescript
// apps/panel-client/src/hooks/useCustomWebSocket.ts
import { useWebSocketGradual } from '@totem/hooks';
import { useQueryClient } from '@tanstack/react-query';

export function useCustomWebSocket() {
  const queryClient = useQueryClient();
  
  const webSocket = useWebSocketGradual({
    url: 'wss://recoverytruck-production.up.railway.app/ws',
    enableAfterDelay: 2000, // Delay de 2 segundos
    requireDataReady: true, // Aguardar dados prontos
    onMessage: (data) => {
      try {
        const { type, data: messageData } = data;
        
        if (type === 'queue_update') {
          queryClient.setQueryData(['tickets', 'queue'], messageData);
        }
        
        if (type === 'ticket_update') {
          queryClient.invalidateQueries({ queryKey: ['tickets'] });
        }
      } catch (error) {
        console.error('Erro ao processar mensagem WebSocket:', error);
      }
    },
    onError: (error) => {
      console.error('Erro no WebSocket:', error);
    },
  });

  return webSocket;
}
```

### **3. 🛠️ Implementação Manual**

```typescript
// apps/panel-client/src/hooks/useManualWebSocket.ts
import { useWebSocket } from '@totem/hooks';

export function useManualWebSocket() {
  const webSocket = useWebSocket({
    url: 'wss://recoverytruck-production.up.railway.app/ws',
    enabled: true,
    reconnectInterval: 5000,
    reconnectAttempts: 5,
    onMessage: (data) => {
      console.log('Mensagem recebida:', data);
    },
  });

  return webSocket;
}
```

## 📁 **Migração dos Arquivos Existentes**

### **Substituir o WebSocket Atual:**

**Antes:**
```typescript
// apps/panel-client/src/hooks/useTicketQueue.ts
const { isConnected, lastMessage } = useWebSocket({
  url: wsUrl,
  onMessage: (data) => {
    // Sem proteções
    queryClient.setQueryData(['tickets', 'queue'], data);
  },
});
```

**Depois:**
```typescript
// apps/panel-client/src/hooks/useTicketQueue.ts
import { useTicketQueueComplete } from './useTicketQueueComplete';

export function useTicketQueue() {
  return useTicketQueueComplete();
}
```

### **Atualizar Componentes:**

**Antes:**
```typescript
// apps/panel-client/src/pages/OperatorPage.tsx
const { tickets, isConnected } = useTicketQueue();

return (
  <div>
    {isConnected ? 'Conectado' : 'Desconectado'}
    {tickets.map(ticket => (
      <TicketCard key={ticket.id} ticket={ticket} />
    ))}
  </div>
);
```

**Depois:**
```typescript
// apps/panel-client/src/pages/OperatorPage.tsx
import { useTicketQueueComplete } from '../hooks/useTicketQueueComplete';
import { WebSocketErrorBoundary } from '@totem/hooks';

const OperatorPage: React.FC = () => {
  const { 
    loadingState, 
    tickets, 
    webSocket 
  } = useTicketQueueComplete();

  if (loadingState !== 'ready') {
    return <LoadingSpinner />;
  }

  return (
    <WebSocketErrorBoundary>
      <div>
        <div>
          Status: {webSocket.isConnected ? 'Conectado' : 'Desconectado'}
          {webSocket.isError && (
            <button onClick={webSocket.reconnect}>
              Reconectar
            </button>
          )}
        </div>
        
        {tickets.map(ticket => (
          <TicketCard key={ticket.id} ticket={ticket} />
        ))}
      </div>
    </WebSocketErrorBoundary>
  );
};
```

## 🔄 **Plano de Migração Gradual**

### **Fase 1: Teste em Desenvolvimento**
```bash
# 1. Instalar dependências atualizadas
cd packages/hooks
pnpm install

# 2. Testar o novo hook
cd apps/panel-client
# Usar useTicketQueueComplete em um componente de teste
```

### **Fase 2: Migração por Componente**
```typescript
// 1. Substituir um componente por vez
// 2. Testar cada substituição
// 3. Monitorar logs e performance
```

### **Fase 3: Deploy Gradual**
```typescript
// Usar feature flag para alternar entre versões
const useTicketQueue = process.env.USE_NEW_WEBSOCKET 
  ? useTicketQueueComplete 
  : useTicketQueueOriginal;
```

## 🎯 **Benefícios Imediatos**

### **1. Estabilidade**
- ✅ **Sem erros React #310**
- ✅ **Reconexão automática**
- ✅ **Error boundaries**

### **2. Performance**
- ✅ **Debounce automático**
- ✅ **Memoização otimizada**
- ✅ **Loading states inteligentes**

### **3. UX**
- ✅ **Feedback visual**
- ✅ **Estados intermediários**
- ✅ **Recuperação automática**

## 📊 **Monitoramento**

### **Logs Importantes:**
```typescript
// Console do navegador
🔌 WebSocket conectado com sucesso!
❌ WebSocket error: [erro]
🔌 WebSocket - Tentativa de reconexão 1/5
```

### **Métricas a Acompanhar:**
- Taxa de reconexão
- Tempo de resposta
- Erros de conexão
- Estados de loading

## 🚀 **Recomendação Final**

**Use a implementação rápida** com `useTicketQueueComplete`:

```typescript
// apps/panel-client/src/pages/OperatorPage.tsx
import { useTicketQueueComplete } from '../hooks/useTicketQueueComplete';
import { WebSocketErrorBoundary } from '@totem/hooks';

const OperatorPage: React.FC = () => {
  const { 
    loadingState, 
    tickets, 
    webSocket 
  } = useTicketQueueComplete();

  return (
    <WebSocketErrorBoundary>
      {/* Seu componente aqui */}
    </WebSocketErrorBoundary>
  );
};
```

Isso dará a você **todos os benefícios** da implementação completa com **mínimo esforço** de migração!

## 🔧 **Configuração de Ambiente**

### **Variáveis de Ambiente:**
```bash
# apps/panel-client/frontend.env
VITE_API_URL=https://recoverytruck-production.up.railway.app
VITE_WS_URL=wss://recoverytruck-production.up.railway.app/ws
VITE_TENANT_ID=7f02a566-2406-436d-b10d-90ecddd3fe2d
```

### **URLs Corretas:**
- **Panel:** `wss://recoverytruck-production.up.railway.app/ws?tenant_id=...&client_type=operator&token=...`
- **Totem:** `wss://recoverytruck-production.up.railway.app/ws?tenant_id=...&client_type=totem`
- **Display:** `wss://recoverytruck-production.up.railway.app/ws?tenant_id=...&client_type=display`
