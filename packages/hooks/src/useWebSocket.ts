import { useEffect, useRef, useState, useCallback } from 'react';

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

  const connect = useCallback(() => {
    try {
      const socket = new WebSocket(url);
      
      socket.onopen = () => {
        setIsConnected(true);
        attemptRef.current = 0;
        if (onOpen) onOpen();
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          if (onMessage) onMessage(data);
        } catch (error) {
          setLastMessage(event.data);
          if (onMessage) onMessage(event.data);
        }
      };

      socket.onclose = () => {
        setIsConnected(false);
        if (onClose) onClose();
        
        // Reconexão exponencial
        if (attemptRef.current < reconnectAttempts) {
          const timeout = reconnectInterval * Math.pow(1.5, attemptRef.current);
          attemptRef.current++;
          
          if (reconnectTimeoutRef.current) {
            window.clearTimeout(reconnectTimeoutRef.current);
          }
          
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, timeout);
        }
      };

      socket.onerror = (error) => {
        if (onError) onError(error);
      };

      socketRef.current = socket;
    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
    }
  }, [url, reconnectInterval, reconnectAttempts, onMessage, onOpen, onClose, onError]);

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

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    connect,
    disconnect
  };
} 