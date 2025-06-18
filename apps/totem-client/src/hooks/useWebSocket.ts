import { useState, useEffect, useCallback, useRef } from 'react';

type WebSocketStatus = 'connecting' | 'open' | 'closed' | 'error';

interface UseWebSocketOptions {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
}

export function useWebSocket({
  url,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
  onMessage,
  onOpen,
  onClose,
  onError,
}: UseWebSocketOptions) {
  const [status, setStatus] = useState<WebSocketStatus>('connecting');
  const [data, setData] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // Função para conectar ao WebSocket
  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      setStatus('connecting');

      ws.onopen = () => {
        setStatus('open');
        reconnectAttemptsRef.current = 0;
        if (onOpen) onOpen();
      };

      ws.onmessage = (event) => {
        try {
          const parsedData = JSON.parse(event.data);
          setData(parsedData);
          if (onMessage) onMessage(parsedData);
        } catch (error) {
          console.error('Erro ao processar mensagem do WebSocket:', error);
          setData(event.data);
          if (onMessage) onMessage(event.data);
        }
      };

      ws.onclose = () => {
        setStatus('closed');
        if (onClose) onClose();
        
        // Tenta reconectar se não excedeu o número máximo de tentativas
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        setStatus('error');
        if (onError) onError(error);
        ws.close();
      };
    } catch (error) {
      console.error('Erro ao conectar ao WebSocket:', error);
      setStatus('error');
    }
  }, [url, reconnectInterval, maxReconnectAttempts, onMessage, onOpen, onClose, onError]);

  // Função para enviar mensagens
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const messageString = typeof message === 'string' ? message : JSON.stringify(message);
      wsRef.current.send(messageString);
      return true;
    }
    return false;
  }, []);

  // Função para fechar a conexão
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    if (reconnectTimeoutRef.current !== null) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  // Conectar ao montar o componente
  useEffect(() => {
    connect();
    
    // Limpar ao desmontar
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    status,
    data,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
} 