import { useCallback, useMemo, useState, useEffect } from 'react';
import { useWebSocket, WebSocketStatus } from './useWebSocket';
import { useDebounce } from './useDebounce';

interface UseWebSocketGradualOptions {
  url: string | null;
  enabled?: boolean;
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onReconnect?: (attempt: number) => void;
  // Opções para reabilitação gradual
  enableAfterDelay?: number; // Delay em ms antes de habilitar WebSocket
  requireDataReady?: boolean; // Se deve aguardar dados estarem prontos
}

interface UseWebSocketGradualReturn {
  // Estados de conexão
  status: WebSocketStatus;
  isConnected: boolean;
  isConnecting: boolean;
  isError: boolean;
  isReconnecting: boolean;
  
  // Estados de reabilitação gradual
  wsEnabled: boolean;
  dataReady: boolean;
  
  // Dados
  lastMessage: any;
  
  // Funções
  sendMessage: (data: any) => boolean;
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;
  enableWebSocket: () => void;
  disableWebSocket: () => void;
  markDataReady: () => void;
  
  // Informações de debug
  connectionAttempts: number;
  lastError: Event | null;
}

export function useWebSocketGradual({
  url,
  enabled = true,
  onMessage,
  onOpen,
  onClose,
  onError,
  onReconnect,
  enableAfterDelay = 1000,
  requireDataReady = true,
}: UseWebSocketGradualOptions): UseWebSocketGradualReturn {
  // Estados para reabilitação gradual
  const [wsEnabled, setWsEnabled] = useState(false);
  const [dataReady, setDataReady] = useState(false);
  const [wsConnectionState, setWsConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');

  // Callbacks protegidos com try-catch
  const protectedOnMessage = useCallback((data: any) => {
    try {
      if (!data || typeof data !== 'object') {
        console.warn('WebSocket: mensagem inválida recebida:', data);
        return;
      }
      
      const { type, data: messageData } = data as any;
      
      if (!type || !messageData) {
        console.warn('WebSocket: mensagem sem type ou data:', data);
        return;
      }
      
      console.log('🔌 WebSocket message received:', { type, data: messageData });
      
      if (onMessage) {
        onMessage(data);
      }
    } catch (error) {
      console.error('Erro no callback onMessage:', error);
    }
  }, [onMessage]);

  const protectedOnOpen = useCallback(() => {
    try {
      console.log('🔌 WebSocket conectado com sucesso!');
      setWsConnectionState('connected');
      if (onOpen) {
        onOpen();
      }
    } catch (error) {
      console.error('Erro no callback onOpen:', error);
    }
  }, [onOpen]);

  const protectedOnClose = useCallback(() => {
    try {
      console.log('🔌 WebSocket fechado');
      setWsConnectionState('disconnected');
      if (onClose) {
        onClose();
      }
    } catch (error) {
      console.error('Erro no callback onClose:', error);
    }
  }, [onClose]);

  const protectedOnError = useCallback((error: Event) => {
    try {
      console.log('❌ WebSocket error:', error);
      setWsConnectionState('error');
      if (onError) {
        onError(error);
      }
    } catch (callbackError) {
      console.error('Erro no callback onError:', callbackError);
    }
  }, [onError]);

  const protectedOnReconnect = useCallback((attempt: number) => {
    try {
      console.log(`🔌 WebSocket - Tentativa de reconexão ${attempt}`);
      if (onReconnect) {
        onReconnect(attempt);
      }
    } catch (error) {
      console.error('Erro no callback onReconnect:', error);
    }
  }, [onReconnect]);

  // Debounce para reconexão
  const debouncedReconnect = useDebounce((attempt: number) => {
    protectedOnReconnect(attempt);
  }, 1000);

  // WebSocket condicional baseado no estado e reabilitação gradual
  const shouldConnectWebSocket = enabled && 
                                wsEnabled && 
                                url && 
                                url.startsWith('ws') && 
                                wsConnectionState !== 'error' &&
                                (!requireDataReady || dataReady);

  // Hook WebSocket com proteções
  const webSocket = useWebSocket({
    url,
    enabled: shouldConnectWebSocket,
    reconnectInterval: 5000,
    reconnectAttempts: 5,
    onMessage: protectedOnMessage,
    onOpen: protectedOnOpen,
    onClose: protectedOnClose,
    onError: protectedOnError,
    onReconnect: debouncedReconnect,
  });

  // Funções para controle de reabilitação gradual
  const enableWebSocket = useCallback(() => {
    console.log('🔌 Habilitando WebSocket gradualmente...');
    setWsEnabled(true);
  }, []);

  const disableWebSocket = useCallback(() => {
    console.log('🔌 Desabilitando WebSocket...');
    setWsEnabled(false);
  }, []);

  // Reabilitação gradual - habilitar WebSocket após delay
  useEffect(() => {
    if (enabled && url && !wsEnabled) {
      console.log(`🔌 Agendando habilitação do WebSocket em ${enableAfterDelay}ms...`);
      const timer = setTimeout(() => {
        console.log('🔌 Habilitando WebSocket após delay...');
        setWsEnabled(true);
      }, enableAfterDelay);
      
      return () => clearTimeout(timer);
    }
  }, [enabled, url, wsEnabled, enableAfterDelay]);

  // Marcar dados como prontos (pode ser chamado externamente)
  const markDataReady = useCallback(() => {
    console.log('🔌 Marcando dados como prontos...');
    setDataReady(true);
  }, []);

  return {
    // Estados de conexão
    status: webSocket.status,
    isConnected: webSocket.isConnected,
    isConnecting: webSocket.isConnecting,
    isError: webSocket.isError,
    isReconnecting: webSocket.isReconnecting,
    
    // Estados de reabilitação gradual
    wsEnabled,
    dataReady,
    
    // Dados
    lastMessage: webSocket.lastMessage,
    
    // Funções
    sendMessage: webSocket.sendMessage,
    connect: webSocket.connect,
    disconnect: webSocket.disconnect,
    reconnect: webSocket.reconnect,
    enableWebSocket,
    disableWebSocket,
    
    // Informações de debug
    connectionAttempts: webSocket.connectionAttempts,
    lastError: webSocket.lastError,
    
    // Função para marcar dados como prontos
    markDataReady,
  };
}
