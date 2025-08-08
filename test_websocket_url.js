#!/usr/bin/env node
/**
 * Script para testar a construção da URL do WebSocket
 */

// Simular variáveis de ambiente
const mockEnv = {
  VITE_WS_URL: 'ws://recoverytruck-production.up.railway.app', // Como está no Vercel
  VITE_TENANT_ID: '7f02a566-2406-436d-b10d-90ecddd3fe2d'
};

// Simular localStorage
const mockLocalStorage = {
  getItem: (key) => {
    if (key === 'auth_token') {
      return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNGU1ZGYxZi1kNTM4LTQ5ZWItOTE1ZS1lYzk5ZjA0OTZkYzIiLCJleHAiOjE3NTQ2NzkyMzF9.zer1UjEEkaS54-n9-BM2xzi8X6dfdmGAZ5jTyap3i_o';
    }
    return null;
  }
};

// Função para construir URL do WebSocket (baseada no código real)
function buildWebSocketUrl(env, localStorage, tenantId) {
  try {
    // Construir URL base do WebSocket
    let baseWs = env?.VITE_WS_URL || 'wss://recoverytruck-production.up.railway.app/ws';
    
    console.log('🔍 DEBUG - VITE_WS_URL:', env?.VITE_WS_URL);
    console.log('🔍 DEBUG - baseWs inicial:', baseWs);
    
    // Garantir que a URL base termina com /ws
    if (!baseWs.endsWith('/ws')) {
      if (baseWs.endsWith('/')) {
        baseWs = baseWs + 'ws';
      } else {
        baseWs = baseWs + '/ws';
      }
    }
    
    console.log('🔍 DEBUG - baseWs após correção:', baseWs);
    
    // Forçar uso de wss:// em produção (simulando HTTPS)
    if (baseWs.startsWith('ws://') && true) { // true = simulando HTTPS
      baseWs = baseWs.replace('ws://', 'wss://');
      console.log('🔍 DEBUG - baseWs após forçar wss:', baseWs);
    }
    
    const token = localStorage.getItem('auth_token');
    const url = `${baseWs}?tenant_id=${tenantId}&client_type=operator${token ? `&token=${token}` : ''}`;
    
    console.log('🔍 DEBUG - WebSocket URL final construída:', url);
    return url;
  } catch (error) {
    console.error('Erro ao construir URL do WebSocket:', error);
    return null;
  }
}

// Testar diferentes cenários
console.log('🧪 Testando construção da URL do WebSocket...\n');

// Cenário 1: Vercel (URL sem /ws)
console.log('📋 CENÁRIO 1: Vercel (URL sem /ws)');
const url1 = buildWebSocketUrl(mockEnv, mockLocalStorage, mockEnv.VITE_TENANT_ID);
console.log('✅ URL resultante:', url1);
console.log('');

// Cenário 2: Desenvolvimento local
console.log('📋 CENÁRIO 2: Desenvolvimento local');
const devEnv = {
  VITE_WS_URL: 'ws://localhost:8000/ws',
  VITE_TENANT_ID: '7f02a566-2406-436d-b10d-90ecddd3fe2d'
};
const url2 = buildWebSocketUrl(devEnv, mockLocalStorage, devEnv.VITE_TENANT_ID);
console.log('✅ URL resultante:', url2);
console.log('');

// Cenário 3: Produção com wss
console.log('📋 CENÁRIO 3: Produção com wss');
const prodEnv = {
  VITE_WS_URL: 'wss://recoverytruck-production.up.railway.app/ws',
  VITE_TENANT_ID: '7f02a566-2406-436d-b10d-90ecddd3fe2d'
};
const url3 = buildWebSocketUrl(prodEnv, mockLocalStorage, prodEnv.VITE_TENANT_ID);
console.log('✅ URL resultante:', url3);
console.log('');

// Cenário 4: URL com barra no final
console.log('📋 CENÁRIO 4: URL com barra no final');
const slashEnv = {
  VITE_WS_URL: 'ws://recoverytruck-production.up.railway.app/',
  VITE_TENANT_ID: '7f02a566-2406-436d-b10d-90ecddd3fe2d'
};
const url4 = buildWebSocketUrl(slashEnv, mockLocalStorage, slashEnv.VITE_TENANT_ID);
console.log('✅ URL resultante:', url4);
console.log('');

console.log('🎯 RESULTADO ESPERADO:');
console.log('Todas as URLs devem terminar com /ws?tenant_id=...&client_type=operator&token=...');
console.log('E devem usar wss:// em produção (HTTPS)');
