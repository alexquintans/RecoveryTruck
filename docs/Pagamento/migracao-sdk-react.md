# 🔄 Migração para SDK React Mercado Pago

## 📋 Visão Geral

Este guia mostra como migrar da implementação atual (SDK JavaScript) para o **SDK React oficial do Mercado Pago** que oferece componentes mais modernos e integrados.

## ✅ Vantagens do SDK React

### **Payment Brick**
- ✅ Interface única para todos os métodos de pagamento
- ✅ Design responsivo e moderno
- ✅ Validação automática de campos
- ✅ Suporte nativo a PIX, cartão, boleto
- ✅ Customização avançada

### **Wallet Brick**
- ✅ Pagamentos com conta Mercado Pago
- ✅ Salvar cartões para compras futuras
- ✅ Interface otimizada para usuários registrados

### **Status Screen Brick**
- ✅ Tela de status automática
- ✅ Feedback visual em tempo real
- ✅ Integração com webhooks

## 🚀 Passos para Migração

### **1. Instalar SDK React**

```bash
# No diretório do totem-client
cd apps/totem-client
npm install @mercadopago/sdk-react
```

### **2. Atualizar Dockerfile**

```dockerfile
# Adicionar ao Dockerfile do totem-client
RUN npm install @mercadopago/sdk-react
```

### **3. Substituir Componente**

**Antes (SDK JavaScript):**
```typescript
import MercadoPagoPayment from './components/MercadoPagoPayment';
```

**Depois (SDK React):**
```typescript
import MercadoPagoPayment from './components/MercadoPagoPaymentReact';
```

### **4. Atualizar PaymentPage**

```typescript
// Em PaymentPage.tsx, substituir:
import MercadoPagoPayment from '../components/MercadoPagoPayment';
// Por:
import MercadoPagoPayment from '../components/MercadoPagoPaymentReact';
```

## 🔧 Implementação Completa

### **Componente MercadoPagoPaymentReact.tsx**

```typescript
import React, { useEffect, useState, useCallback } from 'react';
import { initMercadoPago, Payment } from '@mercadopago/sdk-react';

interface MercadoPagoPaymentReactProps {
  preferenceId: string;
  publicKey: string;
  amount: number;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
}

const MercadoPagoPaymentReact: React.FC<MercadoPagoPaymentReactProps> = ({ 
  preferenceId, 
  publicKey, 
  amount,
  onSuccess, 
  onError, 
  onCancel 
}) => {
  const [isInitialized, setIsInitialized] = useState(false);

  // Inicializar SDK
  useEffect(() => {
    initMercadoPago(publicKey);
    setIsInitialized(true);
  }, [publicKey]);

  // Callbacks do Payment Brick
  const initialization = useCallback(() => ({
    amount: amount,
    preferenceId: preferenceId,
  }), [amount, preferenceId]);

  const onReady = useCallback(() => {
    console.log('✅ Payment Brick pronto');
  }, []);

  const onSubmit = useCallback(({ formData }: any) => {
    console.log('📤 Formulário enviado:', formData);
  }, []);

  const onError = useCallback((error: any) => {
    console.error('❌ Erro no Payment Brick:', error);
    onError?.(error.message || 'Erro desconhecido');
  }, [onError]);

  const onBinChange = useCallback(({ bin }: any) => {
    console.log('💳 BIN alterado:', bin);
  }, []);

  if (!isInitialized) {
    return <div>Carregando...</div>;
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Pagamento Seguro - R$ {amount.toFixed(2)}
          </h3>
          <p className="text-sm text-gray-600">
            Escolha sua forma de pagamento preferida
          </p>
        </div>
        
        <Payment
          initialization={initialization}
          onReady={onReady}
          onSubmit={onSubmit}
          onError={onError}
          onBinChange={onBinChange}
          locale="pt-BR"
          customization={{
            visual: {
              style: {
                theme: 'default'
              }
            },
            paymentMethods: {
              creditCard: 'all',
              debitCard: 'all',
              bankTransfer: 'all',
              ticket: 'all'
            }
          }}
        />
      </div>
    </div>
  );
};

export default MercadoPagoPaymentReact;
```

## 🎨 Customização Avançada

### **Tema Personalizado**

```typescript
customization={{
  visual: {
    style: {
      theme: 'dark', // ou 'light'
      customVariables: {
        baseColor: '#1F526B',
        baseColorSecondary: '#2D7DD2',
        borderRadius: '8px'
      }
    }
  }
}}
```

### **Métodos de Pagamento Específicos**

```typescript
paymentMethods: {
  creditCard: 'all', // ou ['visa', 'mastercard']
  debitCard: 'all',
  bankTransfer: 'all',
  ticket: 'all',
  atm: 'all',
  digitalWallet: 'all'
}
```

### **Validação Personalizada**

```typescript
const onSubmit = useCallback(({ formData, additionalData }: any) => {
  // Validar dados antes de enviar
  if (formData.amount < 1) {
    onError?.('Valor mínimo não atingido');
    return;
  }
  
  // Processar pagamento
  console.log('📤 Dados do formulário:', formData);
}, [onError]);
```

## 🔄 Fluxo de Migração

### **Fase 1: Preparação**
1. ✅ Instalar SDK React
2. ✅ Criar componente alternativo
3. ✅ Testar em ambiente de desenvolvimento

### **Fase 2: Implementação**
1. ✅ Substituir componente no PaymentPage
2. ✅ Testar fluxo completo
3. ✅ Validar callbacks e webhooks

### **Fase 3: Produção**
1. ✅ Atualizar Dockerfile
2. ✅ Deploy em produção
3. ✅ Monitorar métricas

## 🧪 Testes

### **Sandbox**
```bash
# Credenciais de teste
MERCADOPAGO_PUBLIC_KEY=TEST-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### **Cartões de Teste**
- **Visa**: 4509 9535 6623 3704
- **Mastercard**: 5031 4332 1540 6351
- **PIX**: Automático no sandbox

## 📊 Comparação

| Feature | SDK JavaScript | SDK React |
|---------|----------------|-----------|
| **Instalação** | Script tag | npm install |
| **Interface** | Checkout básico | Payment Brick |
| **Customização** | Limitada | Avançada |
| **Responsividade** | Básica | Nativa |
| **Validação** | Manual | Automática |
| **PIX** | Suporte básico | Suporte nativo |
| **Manutenção** | Mais código | Menos código |

## 🚨 Troubleshooting

### **Erro: Module not found**
```bash
# Verificar instalação
npm list @mercadopago/sdk-react
```

### **Erro: initMercadoPago not found**
```typescript
// Verificar import
import { initMercadoPago, Payment } from '@mercadopago/sdk-react';
```

### **Erro: Payment Brick não renderiza**
```typescript
// Verificar initialization
const initialization = useCallback(() => ({
  amount: amount,
  preferenceId: preferenceId,
}), [amount, preferenceId]);
```

## 🎯 Próximos Passos

1. **Instalar SDK React** no ambiente Docker
2. **Testar componente** em desenvolvimento
3. **Migrar gradualmente** em produção
4. **Monitorar performance** e UX
5. **Atualizar documentação** da equipe

---

**🔄 Migração SDK React - Preparada para implementação!** 