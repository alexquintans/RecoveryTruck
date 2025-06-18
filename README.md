# Totem MVP

## Pré-requisitos
- Docker e Docker Compose
- (Opcional) Make

## Subindo o ambiente

```sh
cd infra/compose
# Com Docker Compose
docker-compose up --build
# Ou, se preferir Makefile
make up
```

- API: http://localhost:8000/health
- Totem: http://localhost:3000
- Operador: http://localhost:3001

## Estrutura do Projeto
- apps/api: Backend FastAPI
- apps/totem: Frontend Totem (React/Vite)
- apps/operador: Frontend Operador (React/Vite)
- infra: Infraestrutura (Docker, Compose)
- packages: Libs compartilhadas
- scripts: Scripts utilitários
- docs: Documentação

## Variáveis de Ambiente
Veja `.env.example` para configurar as variáveis necessárias. 

# 🖥️ Frontend Multi-App - Sistema RecoveryTotem

## 📋 **Visão Geral**

Sistema frontend modular com **3 aplicações React** independentes que compartilham componentes e utilitários:

### **🎯 Aplicações**

1. **🖥️ Totem Client** (`totem-client/`)
   - Interface para clientes no totem físico
   - Tela touch otimizada
   - Fluxo: Seleção de serviço → Dados → Pagamento → Ticket

2. **👨‍💼 Operator Panel** (`operator-panel/`)
   - Interface para operadores
   - Gerenciamento de fila
   - Notificações sonoras
   - Controle de tickets

3. **⚙️ Admin Dashboard** (`admin-dashboard/`)
   - Painel administrativo
   - Configurações do sistema
   - Relatórios e analytics
   - Gestão de usuários

### **🔧 Shared Library** (`shared/`)
- Componentes reutilizáveis
- Hooks customizados
- Utilitários e tipos TypeScript
- Serviços de API

## 🏗️ **Arquitetura Técnica**

### **Stack Principal**
- **React 18** + **TypeScript**
- **Vite** (build tool)
- **Tailwind CSS** + **Headless UI**
- **React Query** (estado servidor)
- **Zustand** (estado local)
- **Socket.io** (WebSocket)

### **Estrutura de Diretórios**
```
frontend/
├── shared/                    # 🔧 Biblioteca compartilhada
│   ├── src/
│   │   ├── components/       # Componentes UI reutilizáveis
│   │   ├── hooks/           # Custom hooks
│   │   ├── utils/           # Utilitários
│   │   ├── types/           # TypeScript types
│   │   └── services/        # Serviços de API
│   └── package.json
├── totem-client/             # 🖥️ Interface do cliente
│   ├── src/
│   │   ├── pages/           # Páginas do fluxo
│   │   ├── components/      # Componentes específicos
│   │   ├── store/           # Estado da aplicação
│   │   └── main.tsx
│   └── package.json
├── operator-panel/           # 👨‍💼 Interface do operador
│   ├── src/
│   │   ├── pages/           # Dashboard, fila, configurações
│   │   ├── components/      # Componentes específicos
│   │   ├── store/           # Estado da aplicação
│   │   └── main.tsx
│   └── package.json
├── admin-dashboard/          # ⚙️ Painel administrativo
│   ├── src/
│   │   ├── pages/           # Gestão, relatórios, config
│   │   ├── components/      # Componentes específicos
│   │   ├── store/           # Estado da aplicação
│   │   └── main.tsx
│   └── package.json
└── package.json             # Workspace root
```

## 🚀 **Como Executar**

### **Instalação**
```bash
# Instalar dependências de todas as apps
npm run setup

# Ou instalar individualmente
cd shared && npm install
cd ../totem-client && npm install
cd ../operator-panel && npm install
cd ../admin-dashboard && npm install
```

### **Desenvolvimento**
```bash
# Executar todas as aplicações simultaneamente
npm run dev

# Ou executar individualmente
npm run dev:totem      # http://localhost:5173
npm run dev:operator   # http://localhost:5174
npm run dev:admin      # http://localhost:5175
```

### **Build para Produção**
```bash
# Build de todas as aplicações
npm run build

# Build individual
npm run build:totem
npm run build:operator
npm run build:admin
```

## 🎨 **Design System**

### **Cores Principais**
```css
/* Cores do RecoveryTruck */
--primary: #1e40af;      /* Azul principal */
--secondary: #f59e0b;    /* Amarelo/laranja */
--success: #10b981;      /* Verde sucesso */
--warning: #f59e0b;      /* Amarelo alerta */
--error: #ef4444;        /* Vermelho erro */
--gray: #6b7280;         /* Cinza neutro */
```

### **Componentes Compartilhados**
- **Button** - Botões com variantes
- **Modal** - Modais responsivos
- **Table** - Tabelas com paginação
- **Form** - Formulários com validação
- **Card** - Cards informativos
- **Badge** - Status badges
- **Loading** - Indicadores de carregamento

## 📱 **Responsividade**

### **Breakpoints Tailwind**
- `sm`: 640px+ (tablet pequeno)
- `md`: 768px+ (tablet)
- `lg`: 1024px+ (desktop)
- `xl`: 1280px+ (desktop grande)

### **Estratégia por App**
- **Totem**: Otimizado para telas touch 15-24"
- **Operator**: Responsivo desktop-first
- **Admin**: Responsivo completo

## 🔌 **Integração com Backend**

### **API Client**
```typescript
// Configuração base
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptors para auth
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### **WebSocket Client**
```typescript
// Hook para WebSocket
const useWebSocket = (options: UseWebSocketOptions) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    const ws = io(WS_BASE_URL, {
      query: {
        tenant_id: options.tenant_id,
        client_type: options.client_type,
        operator_id: options.operator_id
      }
    });
    
    ws.on('connect', () => setIsConnected(true));
    ws.on('disconnect', () => setIsConnected(false));
    
    setSocket(ws);
    return () => ws.close();
  }, []);
  
  return { socket, isConnected };
};
```

## 🔊 **Sistema de Notificações Sonoras**

### **Reprodução de Sons**
```typescript
// Hook para notificações sonoras
const useSoundNotifications = (operatorId: string) => {
  const { socket } = useWebSocket({
    tenant_id: 'current-tenant',
    client_type: 'operator',
    operator_id: operatorId
  });
  
  useEffect(() => {
    if (!socket) return;
    
    socket.on('sound_notification', (notification: SoundNotification) => {
      playSound(notification.sound);
    });
  }, [socket]);
  
  const playSound = (config: SoundConfig) => {
    soundUtils.playBeep(
      getSoundFrequency(config.type),
      getSoundDuration(config.type),
      config.volume
    );
  };
};
```

## 🧪 **Testes**

### **Estratégia de Testes**
- **Unit Tests**: Vitest + Testing Library
- **Integration Tests**: Cypress
- **E2E Tests**: Playwright

### **Executar Testes**
```bash
# Testes unitários
npm run test

# Testes por aplicação
npm run test:shared
npm run test:totem
npm run test:operator
npm run test:admin
```

## 📦 **Deploy**

### **Build Otimizado**
```bash
# Build com otimizações
npm run build

# Análise do bundle
npm run analyze
```

### **Configuração de Ambiente**
```env
# .env.production
REACT_APP_API_BASE_URL=https://api.recoverytotem.com
REACT_APP_WS_BASE_URL=wss://ws.recoverytotem.com
REACT_APP_TENANT_ID=recovery-truck-premium
REACT_APP_VERSION=1.0.0
```

## 🔧 **Próximos Passos**

### **Implementação Sugerida**
1. **Fase 1**: Configurar shared library e totem-client
2. **Fase 2**: Implementar operator-panel com notificações
3. **Fase 3**: Desenvolver admin-dashboard
4. **Fase 4**: Testes e otimizações

### **Funcionalidades Prioritárias**
- ✅ Sistema de tipos TypeScript
- ✅ Utilitários compartilhados
- 🔄 Componentes base (Button, Modal, etc.)
- 🔄 Hooks de WebSocket e API
- 🔄 Interface do totem
- 🔄 Painel do operador
- ⏳ Dashboard administrativo

## 📚 **Documentação Adicional**

- [Guia de Componentes](./docs/components.md)
- [Hooks Customizados](./docs/hooks.md)
- [Padrões de Código](./docs/patterns.md)
- [Deploy e CI/CD](./docs/deploy.md)

---

**🎯 Objetivo**: Interface moderna, responsiva e performática para o sistema de totens RecoveryTruck, com foco na experiência do usuário e facilidade de manutenção. 