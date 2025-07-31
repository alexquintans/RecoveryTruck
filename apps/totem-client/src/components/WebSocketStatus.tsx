import React from 'react';

interface WebSocketStatusProps {
  isConnected: boolean;
  status: 'connecting' | 'open' | 'closed' | 'error';
}

const WebSocketStatus: React.FC<WebSocketStatusProps> = ({ isConnected, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'open':
        return 'bg-green-500';
      case 'connecting':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      case 'closed':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'open':
        return 'Conectado';
      case 'connecting':
        return 'Conectando...';
      case 'error':
        return 'Erro';
      case 'closed':
        return 'Desconectado';
      default:
        return 'Desconhecido';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50">
      <div className="flex items-center gap-2 bg-white rounded-lg shadow-lg px-3 py-2 border">
        <div className={`w-2 h-2 rounded-full ${getStatusColor()} animate-pulse`}></div>
        <span className="text-xs font-medium text-gray-700">
          {getStatusText()}
        </span>
      </div>
    </div>
  );
};

export default WebSocketStatus; 