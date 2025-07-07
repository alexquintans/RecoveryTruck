# 🐛 Troubleshooting Docker - Sistema de Totem

## ✅ Problemas Resolvidos

### 1. Erro de Sintaxe YAML (Resolvido)
**Problema:** `yaml: line 10: could not find expected ':'`
**Solução:** Corrigido o formato do comando multi-linha no `docker-compose.yml`

### 2. Arquivo alertmanager.yml Faltando (Resolvido)
**Problema:** Arquivo de configuração do Alertmanager estava faltando
**Solução:** Criado `alertmanager.yml` a partir do backup existente

### 3. Dependências da API Incompletas (Resolvido)
**Problema:** Dependências essenciais faltando no `requirements.txt`
**Solução:** Adicionadas dependências para OpenTelemetry, Prometheus e outras funcionalidades

## 🚀 Como Usar

### Início Rápido
```bash
# Execute o script de desenvolvimento
start-dev.bat

# OU manualmente:
docker-compose up --build
```

### Verificar Status
```bash
docker-compose ps
docker-compose logs -f api
```

## 🔧 Problemas Comuns

### 1. Erro de Porta em Uso
**Sintoma:** `bind: address already in use`
**Soluções:**
```bash
# Verificar portas em uso
netstat -an | findstr :8000
netstat -an | findstr :5173
netstat -an | findstr :5174

# Parar containers conflitantes
docker-compose down
docker container prune
```

### 2. Falha na Build dos Containers
**Sintoma:** Erro durante `docker-compose build`
**Soluções:**
```bash
# Limpar cache do Docker
docker system prune -a

# Rebuild forçado
docker-compose build --no-cache --pull
```

### 3. Container da API Não Inicia
**Sintoma:** Container da API fica reiniciando
**Diagnóstico:**
```bash
docker-compose logs api
```
**Soluções Comuns:**
- Verificar se PostgreSQL está funcionando: `docker-compose logs db`
- Verificar variáveis de ambiente no `env.example`
- Aguardar inicialização completa do banco: ~30 segundos

### 4. Frontend Não Carrega
**Sintoma:** Erro 502 ou páginas em branco
**Soluções:**
```bash
# Verificar build dos frontends
docker-compose logs panel
docker-compose logs totem

# Rebuildar apenas frontends
docker-compose up --build panel totem
```

### 5. Problemas de Permissão (Windows)
**Sintoma:** Erro de acesso a arquivos
**Soluções:**
- Executar PowerShell como Administrador
- Verificar se Docker Desktop está funcionando
- Reiniciar Docker Desktop

## 📋 Checklist de Verificação

### Pré-requisitos
- [ ] Docker Desktop instalado e funcionando
- [ ] WSL2 habilitado (Windows)
- [ ] Portas 8000, 5173, 5174, 3000, 9090 livres
- [ ] Pelo menos 4GB RAM disponível

### Arquivos Essenciais
- [ ] `docker-compose.yml` (sintaxe válida)
- [ ] `apps/api/requirements.txt` (completo)
- [ ] `apps/api/main.py` (existe)
- [ ] `alertmanager_config/alertmanager.yml` (existe)
- [ ] `prom_configs/prometheus.yml` (existe)

### Verificação dos Serviços
- [ ] PostgreSQL: http://localhost:5433
- [ ] API Backend: http://localhost:8000/health
- [ ] Totem Client: http://localhost:5174
- [ ] Panel Client: http://localhost:5173
- [ ] Grafana: http://localhost:3000
- [ ] Prometheus: http://localhost:9090
- [ ] Jaeger: http://localhost:16686

## 🚨 Em Caso de Problemas

### Reset Completo
```bash
# Para tudo e limpa
docker-compose down --volumes --remove-orphans
docker system prune -a --volumes

# Inicia novamente
docker-compose up --build
```

### Logs Detalhados
```bash
# Logs de todos os serviços
docker-compose logs

# Logs de um serviço específico
docker-compose logs -f api
docker-compose logs -f db
docker-compose logs -f panel
```

### Verificar Saúde dos Containers
```bash
# Status dos containers
docker-compose ps

# Inspecionar container específico
docker inspect <container_name>

# Entrar no container para debug
docker-compose exec api bash
docker-compose exec db psql -U postgres -d totem
```

## 📞 Suporte

Se os problemas persistirem, colete as seguintes informações:
1. Logs completos: `docker-compose logs > logs.txt`
2. Status dos containers: `docker-compose ps`
3. Versão do Docker: `docker --version`
4. Sistema operacional e versão
5. Configuração de proxy/firewall se aplicável 