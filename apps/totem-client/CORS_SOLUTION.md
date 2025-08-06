# Solução para Problemas de CORS no Totem-Client

## Problema Identificado

O totem-client estava enfrentando erros de CORS ao tentar criar tickets:

```
Access to XMLHttpRequest at 'https://recoverytruck-production.up.railway.app/tickets' 
from origin 'https://recovery-truck-totem-client-7ynj.vercel.app' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## Soluções Implementadas

### 1. Configuração de API Específica (`api-config.ts`)

Criamos uma configuração específica para o totem-client que:
- Usa axios com timeout de 30 segundos
- Adiciona headers necessários automaticamente
- Trata erros de CORS e servidor especificamente
- Inclui funções de debug e verificação de saúde da API

### 2. Proxy de Desenvolvimento (Vite)

Configuramos um proxy no Vite para desenvolvimento local:
```typescript
proxy: {
  '/api': {
    target: 'https://recoverytruck-production.up.railway.app',
    changeOrigin: true,
    secure: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

### 3. Componente de Tratamento de Erros (`ErrorHandler.tsx`)

Criamos um componente que:
- Verifica a saúde da API ao carregar
- Captura eventos de erro de CORS
- Exibe interface amigável para erros de conexão
- Fornece informações de debug

### 4. Interceptors de Erro

Implementamos interceptors que:
- Detectam erros de CORS automaticamente
- Emitem eventos customizados para tratamento
- Fornecem informações detalhadas de debug

## Como Usar

### Para Desenvolvimento Local

1. O proxy do Vite será usado automaticamente
2. As requisições serão feitas para `/api` que será redirecionado para o servidor

### Para Produção

1. O totem-client usa a URL completa da API
2. O ErrorHandler captura e trata erros de CORS
3. Informações de debug estão disponíveis

### Debug de Problemas

Para debugar problemas de CORS:

1. Abra o console do navegador
2. Procure por eventos `cors:error` ou `server:error`
3. Use o botão "Informações de Debug" no ErrorHandler
4. Verifique as informações de CORS no console

## Configurações de Ambiente

### frontend.env
```
VITE_API_URL=https://recoverytruck-production.up.railway.app
VITE_WS_URL=wss://recoverytruck-production.up.railway.app/ws
VITE_TENANT_ID=7f02a566-2406-436d-b10d-90ecddd3fe2d
VITE_DISABLE_KIOSK_MODE=false
```

## Próximos Passos

Se o problema persistir:

1. **Verificar configuração do servidor**: O servidor precisa permitir requisições do domínio do totem-client
2. **Configurar CORS no backend**: Adicionar headers de CORS apropriados
3. **Usar CDN ou proxy**: Considerar usar um proxy reverso para evitar problemas de CORS

## Monitoramento

O sistema agora:
- Monitora automaticamente a saúde da API
- Captura e reporta erros de CORS
- Fornece informações de debug detalhadas
- Permite retry automático em caso de falha 