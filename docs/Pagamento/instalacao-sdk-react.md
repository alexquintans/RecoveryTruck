# 📦 Instalação SDK React Mercado Pago

## 🚀 Instalação com pnpm

### **1. Instalar dependência**

```bash
# No diretório do totem-client
cd apps/totem-client
pnpm add @mercadopago/sdk-react
```

### **2. Verificar instalação**

```bash
# Verificar se foi instalado
pnpm list @mercadopago/sdk-react
```

### **3. Rebuild do projeto**

```bash
# Rebuild para incluir a nova dependência
pnpm build
```

## 🔧 Configuração no Docker

### **Dockerfile já atualizado**

O `Dockerfile` já foi configurado para instalar automaticamente:

```dockerfile
# instala TODAS as dependências do mono-repo (incluindo @mercadopago/sdk-react)
RUN pnpm install
```

### **Rebuild da imagem Docker**

```bash
# Rebuild da imagem com a nova dependência
docker build -t totem-client .
```

## 🎯 Migração para SDK React

### **1. Substituir import no PaymentPage**

```typescript
// Em PaymentPage.tsx, substituir:
import MercadoPagoPayment from '../components/MercadoPagoPayment';
// Por:
import MercadoPagoPayment from '../components/MercadoPagoPaymentReact';
```

### **2. Testar implementação**

```bash
# Desenvolvimento
pnpm dev

# Build
pnpm build
```

## ✅ Verificação

### **1. Verificar package.json**

```json
{
  "dependencies": {
    "@mercadopago/sdk-react": "^0.0.25",
    // ... outras dependências
  }
}
```

### **2. Verificar import**

```typescript
// Deve funcionar sem erros
import { initMercadoPago, Payment } from '@mercadopago/sdk-react';
```

### **3. Testar componente**

```typescript
// Testar se o componente renderiza
<MercadoPagoPaymentReact
  preferenceId="test"
  publicKey="TEST-xxx"
  amount={50.00}
/>
```

## 🚨 Troubleshooting

### **Erro: Module not found**
```bash
# Reinstalar dependências
pnpm install
```

### **Erro: TypeScript não reconhece**
```bash
# Limpar cache do TypeScript
rm -rf node_modules/.cache
pnpm install
```

### **Erro: Build falha**
```bash
# Limpar build anterior
rm -rf dist
pnpm build
```

## 📋 Próximos Passos

1. ✅ **Instalar dependência** com pnpm
2. ✅ **Testar import** no componente
3. ✅ **Substituir componente** no PaymentPage
4. ✅ **Testar fluxo completo**
5. ✅ **Deploy em produção**

---

**📦 SDK React Mercado Pago - Instalação Completa!** 