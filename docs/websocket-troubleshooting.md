# 🔌 Solução para Problemas de WebSocket

## 📋 Problema Identificado

O erro que você está enfrentando indica que o WebSocket não está conseguindo se conectar ao servidor. O erro `readyState: 3` significa que a conexão está fechada.

## 🔧 Soluções Implementadas

### 1. **Correção do Endpoint WebSocket**

**Problema:** O endpoint estava configurado incorretamente para receber parâmetros.

**Solução:** Modificado o endpoint para aceitar parâmetros de path:

```python
# Antes
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str = None,
    client_type: str = None,
    ...
)

# Depois
@router.websocket("/ws/{tenant_id}/{client_type}")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str,
    client_type: str,
    ...
)
```

### 2. **Configuração do Nginx**

**Problema:** O nginx do panel-client não tinha configuração para WebSocket.

**Solução:** Adicionada configuração completa:

```nginx
# WebSocket em um local específico
location /ws {
    proxy_pass http://api:8000/ws;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Timeouts para WebSocket
    proxy_read_timeout 86400;
    proxy_send_timeout 86400;
    proxy_connect_timeout 60;
    
    # Buffer settings
    proxy_buffering off;
    proxy_cache off;
}
```

### 3. **Melhoria da Configuração do Docker Compose**

**Problema:** Variáveis de ambiente faltando e configurações inadequadas.

**Solução:** Adicionadas variáveis necessárias:

```yaml
api:
  environment:
    - CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000
  command: >
    sh -c "
      until pg_isready -h db -U postgres ; do echo 'Aguardando DB...' && sleep 2 ; done &&
      uvicorn apps.api.full_api:app --host 0.0.0.0 --port 8000 --reload
    "

panel:
  environment:
    - VITE_API_URL=http://localhost:8000
    - VITE_WS_URL=ws://localhost:8000/ws
    - VITE_TENANT_ID=7f02a566-2406-436d-b10d-90ecddd3fe2d
```

## 🧪 Como Testar

### 1. **Reiniciar os Containers**

```bash
# Parar todos os containers
docker-compose down

# Reconstruir e iniciar
docker-compose up --build
```

### 2. **Testar com Script Python**

```bash
# Instalar dependência
pip install websockets

# Executar teste
python test_websocket.py
```

### 3. **Verificar Logs**

```bash
# Logs da API
docker-compose logs api

# Logs do totem
docker-compose logs totem

# Logs do panel
docker-compose logs panel
```

## 🔍 URLs de Teste

### **Totem Client**
- **URL:** `ws://localhost:8000/ws/7f02a566-2406-436d-b10d-90ecddd3fe2d/totem`
- **Frontend:** http://localhost:5174

### **Panel Client**
- **URL:** `ws://localhost:8000/ws/7f02a566-2406-436d-b10d-90ecddd3fe2d/operator?token={jwt_token}`
- **Frontend:** http://localhost:5175

### **Display**
- **URL:** `ws://localhost:8000/ws/7f02a566-2406-436d-b10d-90ecddd3fe2d/display`

## 🐛 Debugging

### 1. **Verificar se a API está rodando**

```bash
curl http://localhost:8000/health
```

### 2. **Verificar se o WebSocket está acessível**

```bash
# Teste direto no navegador
# Abra o console e execute:
const ws = new WebSocket('ws://localhost:8000/ws/7f02a566-2406-436d-b10d-90ecddd3fe2d/totem');
ws.onopen = () => console.log('Conectado!');
ws.onerror = (e) => console.error('Erro:', e);
```

### 3. **Verificar logs do nginx**

```bash
docker-compose exec totem tail -f /var/log/nginx/error.log
docker-compose exec panel tail -f /var/log/nginx/error.log
```

## 📊 Monitoramento

### **Grafana Dashboard**
- **URL:** http://localhost:3000
- **Login:** admin/admin
- **Dashboard:** Totem System

### **Prometheus**
- **URL:** http://localhost:9090
- **Métricas:** WebSocket connections

## 🔄 Próximos Passos

1. **Reiniciar todos os containers**
2. **Testar com o script Python**
3. **Verificar logs para erros**
4. **Testar no navegador**
5. **Monitorar métricas no Grafana**

## 📞 Suporte

Se o problema persistir:

1. Verifique se todas as portas estão livres
2. Confirme se o Docker está rodando
3. Verifique se não há conflitos de rede
4. Teste com diferentes browsers
5. Verifique logs detalhados

## 🎯 Resultado Esperado

Após as correções, você deve ver:

- ✅ WebSocket conectando sem erros
- ✅ Mensagens sendo trocadas
- ✅ Atualizações em tempo real funcionando
- ✅ Notificações sonoras ativas
- ✅ Status de conexão verde no frontend 