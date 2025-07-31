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
  reconnectInterval = 5000, // Aumentado para 5 segundos
  maxReconnectAttempts = 10, // Aumentado para 10 tentativas
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
  const isConnectingRef = useRef(false);

  // Função para conectar ao WebSocket
  const connect = useCallback(() => {
    if (isConnectingRef.current) {
      console.log('🔍 WebSocket - Já está tentando conectar, ignorando...');
      return;
    }

    try {
      console.log('🔍 WebSocket - Conectando:', url);
      isConnectingRef.current = true;
      const ws = new WebSocket(url);
      wsRef.current = ws;
      setStatus('connecting');

      ws.onopen = () => {
        console.log('🔍 WebSocket - Conectado com sucesso');
        setStatus('open');
        reconnectAttemptsRef.current = 0;
        isConnectingRef.current = false;
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

      ws.onclose = (event) => {
        console.log('🔍 WebSocket - Conexão fechada', event.code, event.reason);
        setStatus('closed');
        isConnectingRef.current = false;
        if (onClose) onClose();
        
        // Só tenta reconectar se não foi um fechamento intencional
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          console.log(`🔍 WebSocket - Tentativa de reconexão ${reconnectAttemptsRef.current}/${maxReconnectAttempts}`);
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (error) => {
        console.error('🔍 WebSocket - Erro na conexão:', error);
        setStatus('error');
        isConnectingRef.current = false;
        if (onError) onError(error);
      };
    } catch (error) {
      console.error('Erro ao conectar ao WebSocket:', error);
      setStatus('error');
      isConnectingRef.current = false;
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
      wsRef.current.close(1000, 'Disconnect requested'); // Código 1000 = fechamento normal
      wsRef.current = null;
    }
    
    if (reconnectTimeoutRef.current !== null) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    isConnectingRef.current = false;
  }, []);

  // Conectar ao montar o componente
  useEffect(() => {
    console.log('🔍 WebSocket - useEffect - Iniciando conexão');
    connect();
    
    // Limpar ao desmontar
    return () => {
      console.log('🔍 WebSocket - useEffect - Limpando conexão');
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    status,
    data,
    sendMessage,
    disconnect,
    reconnect: connect,
    isConnected: status === 'open',
  };
} 