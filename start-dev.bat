@echo off
echo ====================================
echo    SISTEMA DE TOTEM - DESENVOLVIMENTO
echo ====================================
echo.

echo [1/5] Verificando dependencias...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker nao esta instalado ou nao esta funcionando!
    echo Por favor, instale o Docker Desktop primeiro.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose nao esta instalado!
    pause
    exit /b 1
)

echo ✅ Docker e Docker Compose estao instalados

echo.
echo [2/5] Validando configuracoes...
docker-compose config >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Erro na configuracao do docker-compose.yml!
    docker-compose config
    pause
    exit /b 1
)

echo ✅ Configuracao do Docker Compose validada

echo.
echo [3/5] Parando containers existentes...
docker-compose down --remove-orphans

echo.
echo [4/5] Criando e iniciando containers...
docker-compose up --build -d

echo.
echo [5/5] Verificando status dos servicos...
timeout /t 10 /nobreak >nul
docker-compose ps

echo.
echo ====================================
echo    SERVICOS DISPONIVEIS:
echo ====================================
echo 🌐 API Backend:        http://localhost:8000
echo 📱 Totem Client:       http://localhost:5174
echo 🎛️  Panel Client:       http://localhost:5173
echo 📊 Grafana:           http://localhost:3000 (admin/admin)
echo 🔍 Jaeger:            http://localhost:16686
echo 📈 Prometheus:        http://localhost:9090
echo 🚨 Alertmanager:      http://localhost:9093
echo 📋 Node Exporter:     http://localhost:9100
echo 🗄️  PostgreSQL:        localhost:5433
echo ====================================
echo.
echo Para ver os logs: docker-compose logs -f [servico]
echo Para parar tudo: docker-compose down
echo.
pause 