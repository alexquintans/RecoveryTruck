import React from 'react';
import { useTicketQueueImproved } from '../hooks/useTicketQueueImproved';
import { WebSocketErrorBoundary } from '@totem/hooks';

const OperatorPageImproved: React.FC = () => {
  const { 
    loadingState, 
    isLoading, 
    tickets, 
    myTickets, 
    equipment, 
    operationConfig, 
    webSocket,
    refetch 
  } = useTicketQueueImproved();

  // Loading state com estados intermediários
  if (loadingState !== 'ready') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
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
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Painel do Operador
          </h1>
          
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

          {/* Status da operação */}
          <div className="bg-white rounded-lg shadow p-4 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Status da Operação
            </h2>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                operationConfig.isOperating 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {operationConfig.isOperating ? 'Operação Ativa' : 'Operação Inativa'}
              </div>
              <button
                onClick={refetch}
                className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 transition-colors"
              >
                Atualizar Dados
              </button>
            </div>
          </div>
        </div>

        {/* Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Tickets na Fila</h3>
            <p className="text-3xl font-bold text-blue-600">{tickets.length}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Meus Tickets</h3>
            <p className="text-3xl font-bold text-green-600">{myTickets.length}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Equipamentos</h3>
            <p className="text-3xl font-bold text-purple-600">{equipment.length}</p>
          </div>
        </div>

        {/* Lista de Tickets */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Tickets na Fila ({tickets.length})
            </h2>
          </div>
          
          <div className="divide-y divide-gray-200">
            {tickets.map((ticket: any) => (
              <div key={ticket.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
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

export default OperatorPageImproved;
