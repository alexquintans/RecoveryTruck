import React, { Component, ReactNode } from 'react';

interface WebSocketErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

interface WebSocketErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export class WebSocketErrorBoundary extends Component<WebSocketErrorBoundaryProps, WebSocketErrorBoundaryState> {
  constructor(props: WebSocketErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): WebSocketErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('WebSocket Error Boundary:', error, errorInfo);
    
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="text-red-800 font-semibold">Erro de Conexão</h3>
          <p className="text-red-600 text-sm">
            Houve um problema com a conexão em tempo real. 
            A aplicação continuará funcionando normalmente.
          </p>
          <button 
            onClick={this.handleRetry}
            className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
