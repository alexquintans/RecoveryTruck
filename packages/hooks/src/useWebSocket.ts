import { useEffect, useRef, useState, useCallback, useMemo } from 'react';

// Tipos para estados de conexão
export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error' | 'reconnecting';

// Interface para opções do WebSocket
interface UseWebSocketOptions {
  url: string | null;
  enabled?: boolean;
  reconnectInterval?: number;
  reconnectAttempts?: number;
  onMessage?: (data: any) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onReconnect?: (attempt: number) => void;
}

// Interface para retorno do hook
interface UseWebSocketReturn {
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

export function useWebSocket({
  url,
  enabled = true,
  reconnectInterval = 5000,
  reconnectAttempts = 5,
  onMessage,
  onOpen,
  onClose,
  onError,
  onReconnect,
}: UseWebSocketOptions): UseWebSocketReturn {
  // Estados de conexão
  const [status, setStatus] = useState<WebSocketStatus>('disconnected');
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [lastError, setLastError] = useState<Event | null>(null);
  const [connectionAttempts, setConnectionAttempts] = useState(0);
  
  // Refs para controle interno
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const attemptRef = useRef(0);
  const isConnectingRef = useRef(false);
  const shouldConnectRef = useRef(false);

  // Memoizar callbacks para evitar recriações desnecessárias
  const memoizedOnMessage = useCallback((data: any) => {
    try {
      if (onMessage) {
        onMessage(data);
      }
    } catch (error) {
      console.error('Erro no callback onMessage:', error);
    }
  }, [onMessage]);

  const memoizedOnOpen = useCallback(() => {
    try {
      console.log('🔌 WebSocket conectado com sucesso!');
      setStatus('connected');
      setConnectionAttempts(0);
      attemptRef.current = 0;
      if (onOpen) {
        onOpen();
      }
    } catch (error) {
      console.error('Erro no callback onOpen:', error);
    }
  }, [onOpen]);

  const memoizedOnClose = useCallback(() => {
    try {
      console.log('🔌 WebSocket fechado');
      setStatus('disconnected');
      if (onClose) {
        onClose();
      }
    } catch (error) {
      console.error('Erro no callback onClose:', error);
    }
  }, [onClose]);

  const memoizedOnError = useCallback((error: Event) => {
    try {
      console.error('❌ WebSocket error:', error);
      setStatus('error');
      setLastError(error);
      if (onError) {
        onError(error);
      }
    } catch (callbackError) {
      console.error('Erro no callback onError:', callbackError);
    }
  }, [onError]);

  // Função de conexão com proteções robustas
  const connect = useCallback(() => {
    // Verificações de segurança
    if (!url || !url.startsWith('ws')) {
      console.warn('WebSocket: URL inválida:', url);
      setStatus('error');
      return;
    }

    if (isConnectingRef.current) {
      console.log('WebSocket: Já está tentando conectar, ignorando...');
      return;
    }

    if (!enabled) {
      console.log('WebSocket: Desabilitado, não conectando');
      return;
    }

    try {
      console.log('🔌 WebSocket - Conectando:', url);
      isConnectingRef.current = true;
      setStatus('connecting');
      setConnectionAttempts((prev: number) => prev + 1);

      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        console.log('🔌 WebSocket - Conectado com sucesso!');
        isConnectingRef.current = false;
        memoizedOnOpen();
      };

      socket.onmessage = (event) => {
        try {
          let data;
          if (typeof event.data === 'string') {
            data = JSON.parse(event.data);
          } else {
            data = event.data;
          }
          
          setLastMessage(data);
          memoizedOnMessage(data);
        } catch (error) {
          console.error('Erro ao processar mensagem do WebSocket:', error);
          setLastMessage(event.data);
          memoizedOnMessage(event.data);
        }
      };

      socket.onclose = (event) => {
        console.log('🔌 WebSocket - Conexão fechada', event.code, event.reason);
        isConnectingRef.current = false;
        memoizedOnClose();
        
        // Reconexão apenas se não foi fechamento intencional e ainda há tentativas
        if (event.code !== 1000 && attemptRef.current < reconnectAttempts && shouldConnectRef.current) {
          setStatus('reconnecting');
          attemptRef.current++;
          
          console.log(`🔌 WebSocket - Tentativa de reconexão ${attemptRef.current}/${reconnectAttempts}`);
          
          if (onReconnect) {
            onReconnect(attemptRef.current);
          }
          
          // Reconexão exponencial
          const timeout = reconnectInterval * Math.pow(1.5, attemptRef.current - 1);
          
          if (reconnectTimeoutRef.current) {
            window.clearTimeout(reconnectTimeoutRef.current);
          }
          
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, timeout);
        } else {
          setStatus('disconnected');
        }
      };

      socket.onerror = (error) => {
        console.error('❌ WebSocket - Erro na conexão:', error);
        isConnectingRef.current = false;
        memoizedOnError(error);
      };

    } catch (error) {
      console.error('Erro ao conectar WebSocket:', error);
      isConnectingRef.current = false;
      setStatus('error');
      setLastError(error as Event);
    }
  }, [url, enabled, reconnectInterval, reconnectAttempts, memoizedOnOpen, memoizedOnClose, memoizedOnError, memoizedOnMessage, onReconnect]);

  // Função de desconexão
  const disconnect = useCallback(() => {
    console.log('🔌 WebSocket - Desconectando...');
    shouldConnectRef.current = false;
    
    if (socketRef.current) {
      socketRef.current.close(1000, 'Disconnect requested');
      socketRef.current = null;
    }
    
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    isConnectingRef.current = false;
    attemptRef.current = 0;
    setStatus('disconnected');
  }, []);

  // Função de reconexão manual
  const reconnect = useCallback(() => {
    console.log('🔌 WebSocket - Reconectando manualmente...');
    disconnect();
    attemptRef.current = 0;
    shouldConnectRef.current = true;
    connect();
  }, [connect, disconnect]);

  // Função para enviar mensagens
  const sendMessage = useCallback((data: any) => {
    if (socketRef.current && status === 'connected') {
      try {
        const messageString = typeof data === 'string' ? data : JSON.stringify(data);
        socketRef.current.send(messageString);
        return true;
      } catch (error) {
        console.error('Erro ao enviar mensagem WebSocket:', error);
        return false;
      }
    }
    return false;
  }, [status]);

  // Memoizar URL para evitar reconexões desnecessárias
  const memoizedUrl = useMemo(() => url, [url]);

  // useEffect para gerenciar conexão
  useEffect(() => {
    if (enabled && memoizedUrl && memoizedUrl.startsWith('ws')) {
      console.log('🔌 WebSocket - useEffect - Iniciando conexão');
      shouldConnectRef.current = true;
      connect();
    } else {
      console.log('🔌 WebSocket - useEffect - Desabilitado ou URL inválida');
      disconnect();
    }
    
    return () => {
      console.log('🔌 WebSocket - useEffect - Limpando conexão');
      disconnect();
    };
  }, [memoizedUrl, enabled, connect, disconnect]);

  // Computed values para facilitar uso
  const isConnected = status === 'connected';
  const isConnecting = status === 'connecting';
  const isError = status === 'error';
  const isReconnecting = status === 'reconnecting';

  return {
    // Estados de conexão
    status,
    isConnected,
    isConnecting,
    isError,
    isReconnecting,
    
    // Dados
    lastMessage,
    
    // Funções
    sendMessage,
    connect,
    disconnect,
    reconnect,
    
    // Informações de debug
    connectionAttempts,
    lastError,
  };
} 