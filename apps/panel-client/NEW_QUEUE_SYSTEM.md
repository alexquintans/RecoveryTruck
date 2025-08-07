# Nova Implementação de Filas por Serviço

## Resumo da Implementação

Implementamos uma nova estrutura de filas divididas por serviço, substituindo a fila única por múltiplas filas organizadas por serviço ativo. Esta abordagem é mais eficiente e fácil de manter do que criar subtickets.

## Principais Mudanças

### 1. **Novas Interfaces**

```typescript
interface ServiceQueue {
  serviceId: string;
  serviceName: string;
  tickets: Ticket[];
}

interface TicketPriority {
  isFirstService: boolean;
  isLastService: boolean;
  serviceOrder: number;
  totalServices: number;
}
```

### 2. **Funções Utilitárias**

#### **`organizeTicketsByService(tickets, activeServices)`**
- Organiza tickets por serviço ativo
- Filtra tickets que contêm cada serviço específico
- Retorna array de `ServiceQueue`

#### **`getTicketPriority(ticket, currentServiceId)`**
- Calcula prioridade do ticket em relação ao serviço atual
- Identifica se é primeiro/último serviço
- Retorna ordem e total de serviços

#### **`getTicketsForService(serviceId)`**
- Obtém tickets de um serviço específico
- Usado para renderizar conteúdo das tabs

#### **`handleCallTicket(ticket, serviceId)`**
- Lógica de chamada inteligente
- Verifica se é primeiro serviço do ticket
- Chama ticket completo ou serviço específico

### 3. **Componente TicketCard Melhorado**

```jsx
const TicketCard = ({ 
  ticket, 
  currentService, 
  onCall, 
  selectedEquipment, 
  callLoading 
}) => {
  const priority = getTicketPriority(ticket, currentService);
  const services = ticket.services || [ticket.service];
  const currentServiceData = services.find(s => s.id === currentService);
  
  return (
    <div className={`ticket-card ${priority.isFirstService ? 'first-service' : ''}`}>
      {/* Indicadores visuais */}
      {services.length > 1 && (
        <div className="service-indicator">
          <span>{priority.serviceOrder}/{priority.totalServices}</span>
          {priority.isFirstService && <span>Primeiro</span>}
        </div>
      )}
      
      {/* Informações do cliente */}
      <div className="customer-info">
        <div>{ticket.customer_name}</div>
        <div>{currentServiceData.name}</div>
      </div>
      
      {/* Outros serviços */}
      {services.length > 1 && (
        <div className="other-services">
          <span>TAMBÉM AGUARDA:</span>
          {services.filter(s => s.id !== currentService).map(service => (
            <span key={service.id}>{service.name}</span>
          ))}
        </div>
      )}
      
      {/* Botão de chamada */}
      <button onClick={() => onCall(ticket, currentService)}>
        Chamar
      </button>
    </div>
  );
};
```

### 4. **Nova Estrutura Visual**

#### **Tabs dos Serviços**
```jsx
<div className="queue-tabs flex flex-wrap gap-2 mb-4">
  {serviceQueues.map(service => (
    <button 
      key={service.serviceId}
      className={`tab ${activeServiceTab === service.serviceId ? 'active' : ''}`}
      onClick={() => setActiveServiceTab(service.serviceId)}
    >
      {service.serviceName}
      <span className="ticket-count">{service.tickets.length}</span>
    </button>
  ))}
</div>
```

#### **Conteúdo da Fila Ativa**
```jsx
<div className="queue-content">
  {activeTickets.map((ticket) => (
    <TicketCard 
      key={ticket.id}
      ticket={ticket}
      currentService={activeServiceTab}
      onCall={handleCallTicket}
      selectedEquipment={selectedEquipment}
      callLoading={callLoading}
    />
  ))}
</div>
```

## Benefícios da Nova Implementação

### 1. **Organização Clara**
- Cada serviço tem sua própria fila
- Fácil identificação de tickets por serviço
- Contagem de tickets por fila

### 2. **Indicadores Visuais**
- Badge mostrando ordem do serviço (1/3, 2/3, etc.)
- Indicador "Primeiro" para primeiro serviço
- Lista de outros serviços aguardando

### 3. **Lógica Inteligente**
- Identifica se é primeiro serviço do ticket
- Chama ticket completo ou serviço específico
- Mantém referência original aos tickets

### 4. **UX Melhorada**
- Tabs para navegar entre serviços
- Contadores de tickets por fila
- Design responsivo e intuitivo

## Fluxo de Funcionamento

### 1. **Organização Inicial**
```typescript
useEffect(() => {
  const activeServices = services.filter(s => s.isActive);
  const queues = organizeTicketsByService(tickets, activeServices);
  setServiceQueues(queues);
  
  if (queues.length > 0 && !activeServiceTab) {
    setActiveServiceTab(queues[0].serviceId);
  }
}, [tickets, services, activeServiceTab]);
```

### 2. **Renderização das Tabs**
- Uma tab para cada serviço ativo
- Contador de tickets em cada tab
- Tab ativa destacada

### 3. **Renderização dos Tickets**
- Filtra tickets do serviço ativo
- Aplica componente TicketCard
- Mostra indicadores de prioridade

### 4. **Chamada de Tickets**
- Verifica se é primeiro serviço
- Chama ticket completo ou específico
- Atualiza filas após chamada

## Exemplo de Uso

### Cenário: Alice com 2 Serviços
1. **Alice compra**: Crioterapia + Massoterapia
2. **Fila Crioterapia**: Mostra ticket da Alice com badge "1/2" e "Primeiro"
3. **Fila Massoterapia**: Mostra ticket da Alice com badge "2/2"
4. **Indicadores**: "TAMBÉM AGUARDA: Massoterapia" na fila de Crioterapia
5. **Chamada**: Clicar "Chamar" na Crioterapia chama o ticket completo

## Arquivos Modificados

- `src/pages/OperatorPage.tsx`
  - Adicionadas interfaces `ServiceQueue` e `TicketPriority`
  - Implementadas funções utilitárias
  - Criado componente `TicketCard` melhorado
  - Substituída seção "Fila" por "Filas por Serviço"
  - Adicionada lógica de tabs e navegação

## Próximos Passos

1. **Testar implementação** com dados reais
2. **Ajustar estilos** conforme necessário
3. **Implementar chamada específica por serviço** quando backend suportar
4. **Adicionar animações** de transição entre tabs
5. **Otimizar performance** para grandes volumes de tickets

## Vantagens sobre Subtickets

1. **Simplicidade**: Não cria objetos complexos
2. **Performance**: Menos processamento
3. **Manutenibilidade**: Código mais limpo
4. **Flexibilidade**: Fácil de modificar
5. **Compatibilidade**: Mantém estrutura existente
