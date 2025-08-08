import { useCallback, useMemo, useState } from 'react';
import { useWebSocket, WebSocketStatus } from './useWebSocket';
import { useDebounce } from './useDebounce';

interface UseProtectedWebSocketOptions {
  url: string | null;
  enabled?: boolean;
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onReconnect?: (attempt: number) => void;
}

interface UseProtectedWebSocketReturn {
  // Estados de conexão
  status: WebSocketStatus;
  isConnected: boolean;
  isConnecting: boolean;
  isError: boolean;
  isReconnecting: boolean;
  
  // Dados
  lastMessage: any;
  
  // Funções
  sendMessage: (data: any) => boolean;
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;
  
  // Informações de debug
  connectionAttempts: number;
  lastError: Event | null;
}

export function useProtectedWebSocket({
  url,
  enabled = true,
  onMessage,
  onOpen,
  onClose,
  onError,
  onReconnect,
}: UseProtectedWebSocketOptions): UseProtectedWebSocketReturn {
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

  // WebSocket condicional baseado no estado
  const shouldConnectWebSocket = enabled && 
                                url && 
                                url.startsWith('ws') && 
                                wsConnectionState !== 'error';

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

  return webSocket;
}
