# RecoveryTruck - Totem de Autoatendimento

Aplicação para totem de autoatendimento para serviços de recuperação física.

## Configuração do Modo Quiosque (PWA)

Esta aplicação foi configurada para funcionar como um Progressive Web App (PWA), oferecendo uma experiência de tela cheia semelhante a um aplicativo nativo.

### Vantagens do Modo PWA para Quiosques

1. **Tela cheia automática**: Quando instalado como PWA, abre automaticamente em modo tela cheia
2. **Experiência offline**: Funciona mesmo com conexão instável
3. **Sem barra de navegação**: Remove elementos do navegador
4. **Melhor segurança**: Mais difícil sair da aplicação

### Como instalar como PWA

1. Acesse a aplicação no navegador Chrome ou Edge
2. Aguarde o prompt de instalação ou clique no botão "Instalar como PWA" na página de administração
3. Confirme a instalação
4. A aplicação será instalada como um aplicativo e abrirá automaticamente em tela cheia

### Configuração para inicialização automática no Windows

Para configurar o totem para iniciar automaticamente no modo quiosque:

1. Crie um arquivo batch (`.bat`) com o seguinte conteúdo:

```batch
@echo off
start chrome --kiosk https://seu-dominio.com.br
```

2. Adicione este arquivo à pasta de inicialização do Windows:
   - Pressione `Win + R`
   - Digite `shell:startup`
   - Copie o arquivo batch para esta pasta

### Variáveis de ambiente

- `VITE_DISABLE_KIOSK_MODE`: Define se o modo quiosque deve ser desativado (útil para desenvolvimento)
  - `true`: Desativa o modo quiosque
  - `false`: Ativa o modo quiosque (padrão)

## Desenvolvimento

### Requisitos

- Node.js 16+
- npm ou yarn

### Instalação

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev

# Construir para produção
npm run build

# Visualizar versão de produção localmente
npm run preview
```

### Estrutura do projeto

- `src/`: Código fonte da aplicação
  - `components/`: Componentes reutilizáveis
  - `pages/`: Páginas da aplicação
  - `App.tsx`: Componente principal
  - `main.tsx`: Ponto de entrada da aplicação
- `public/`: Arquivos estáticos
  - `manifest.json`: Configuração do PWA
  - `sw.js`: Service Worker para PWA

## Recursos PWA

- Instalável como aplicativo
- Funciona offline
- Modo tela cheia
- Atualizações automáticas

## Funcionalidades Implementadas

- ✅ Seleção de serviços
- ✅ Coleta de dados do cliente com validações
- ✅ Integração com pagamentos (QR Code)
- ✅ Geração de tickets
- ✅ Notificações sonoras
- ✅ Fluxo completo de atendimento
- ✅ Modo quiosque (tela cheia e bloqueio de saída)

## Estrutura do Projeto

```
src/
├── assets/        # Recursos estáticos (imagens, sons)
├── components/    # Componentes reutilizáveis
├── hooks/         # Hooks personalizados
├── pages/         # Páginas da aplicação
├── store/         # Gerenciamento de estado (Zustand)
├── types.ts       # Definições de tipos
└── utils/         # Utilitários (API, validações, formatadores)
```

## Tecnologias

- React 18
- TypeScript
- Tailwind CSS
- Zustand (gerenciamento de estado)
- React Query (requisições à API)
- Framer Motion (animações)

## Páginas

1. **WelcomePage** - Página inicial
2. **SelectServicePage** - Seleção de serviços
3. **CustomerInfoPage** - Coleta de dados do cliente
4. **TermsPage** - Termos de responsabilidade
5. **PaymentPage** - Processamento de pagamento
6. **TicketPage** - Exibição do ticket/comprovante

## Desenvolvimento

```bash
# Instalar dependências
pnpm install

# Iniciar servidor de desenvolvimento
pnpm dev

# Construir para produção
pnpm build
```

## Modo Quiosque

O aplicativo inclui um modo quiosque que:

- Solicita ao usuário para ativar o modo tela cheia (requisito de segurança dos navegadores)
- Ativa automaticamente o modo tela cheia após interação do usuário
- Bloqueia teclas de sistema (Alt+F4, Alt+Tab, etc.)
- Impede a saída acidental da aplicação
- Desativa o menu de contexto (clique direito)
- Suporte especial para dispositivos iOS (que não têm API Fullscreen nativa)

### Compatibilidade

O modo quiosque foi projetado para funcionar em:

- Navegadores desktop modernos (Chrome, Firefox, Edge)
- Dispositivos móveis Android (Chrome, Samsung Internet)
- Dispositivos iOS (Safari) - com suporte limitado devido às restrições da plataforma

### Acessando o Painel Administrativo

Para acessar o painel administrativo e desativar o modo quiosque:

1. **Em dispositivos touch**: Toque nos 4 cantos da tela em sequência (superior esquerdo → superior direito → inferior direito → inferior esquerdo → superior esquerdo)
2. **Em dispositivos com teclado**: Pressione Ctrl + Alt + A

### Desenvolvimento

Para desativar o modo quiosque durante o desenvolvimento:

1. Crie um arquivo `.env` na pasta `apps/totem-client`
2. Adicione `VITE_DISABLE_KIOSK_MODE=true`

## Próximos Passos

- Implementar testes unitários
- Adicionar mais opções de pagamento
- Melhorar a acessibilidade
- Implementar modo offline 