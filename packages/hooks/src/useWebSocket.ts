import { useEffect, useRef, useState, useCallback, useMemo } from 'react';

interface UseWebSocketOptions {
  url: string;
  reconnectInterval?: number;
  reconnectAttempts?: number;
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
}

export function useWebSocket({
  url,
  reconnectInterval = 2000,
  reconnectAttempts = 10,
  onMessage,
  onOpen,
  onClose,
  onError,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const attemptRef = useRef(0);

  // Memoizar as callbacks para evitar recriações desnecessárias
  const memoizedOnMessage = useCallback(onMessage || (() => {}), [onMessage]);
  const memoizedOnOpen = useCallback(onOpen || (() => {}), [onOpen]);
  const memoizedOnClose = useCallback(onClose || (() => {}), [onClose]);
  const memoizedOnError = useCallback(onError || (() => {}), [onError]);

  const connect = useCallback(() => {
    try {
      console.log('🔍 Panel WebSocket - Conectando:', url);
      const socket = new WebSocket(url);
      
      socket.onopen = () => {
        console.log('🔍 Panel WebSocket - Conectado com sucesso');
        setIsConnected(true);
        attemptRef.current = 0;
        memoizedOnOpen();
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          memoizedOnMessage(data);
        } catch (error) {
          setLastMessage(event.data);
          memoizedOnMessage(event.data);
        }
      };

      socket.onclose = () => {
        console.log('🔍 Panel WebSocket - Conexão fechada');
        setIsConnected(false);
        memoizedOnClose();
        
        // Reconexão exponencial
        if (attemptRef.current < reconnectAttempts) {
          const timeout = reconnectInterval * Math.pow(1.5, attemptRef.current);
          attemptRef.current++;
          console.log(`🔍 Panel WebSocket - Tentativa de reconexão ${attemptRef.current}/${reconnectAttempts}`);
          
          if (reconnectTimeoutRef.current) {
            window.clearTimeout(reconnectTimeoutRef.current);
          }
          
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, timeout);
        }
      };

      socket.onerror = (error) => {
        console.error('🔍 Panel WebSocket - Erro na conexão:', error);
        memoizedOnError(error);
      };

      socketRef.current = socket;
    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
    }
  }, [url, reconnectInterval, reconnectAttempts, memoizedOnOpen, memoizedOnClose, memoizedOnError, memoizedOnMessage]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((data: any) => {
    if (socketRef.current && isConnected) {
      socketRef.current.send(typeof data === 'string' ? data : JSON.stringify(data));
      return true;
    }
    return false;
  }, [isConnected]);

  // Memoizar a URL para evitar reconexões desnecessárias
  const memoizedUrl = useMemo(() => url, [url]);

  useEffect(() => {
    console.log('🔍 Panel WebSocket - useEffect - Iniciando conexão');
    connect();
    
    return () => {
      console.log('🔍 Panel WebSocket - useEffect - Limpando conexão');
      disconnect();
    };
  }, [memoizedUrl, connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect
  };
} 