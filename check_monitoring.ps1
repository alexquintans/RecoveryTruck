# Script PowerShell para verificar serviços de monitoramento do Totem
# Execute: .\check_monitoring.ps1

Write-Host "🔍 Verificando serviços de monitoramento do Totem..." -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue

# Função para verificar se um serviço está respondendo
function Test-Service {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Port
    )
    
    Write-Host "Verificando $Name... " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ FALHOU" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ FALHOU" -ForegroundColor Red
        return $false
    }
}

# Função para verificar métricas específicas
function Test-Metric {
    param(
        [string]$Service,
        [string]$Metric
    )
    
    Write-Host "Verificando métrica $Metric em $Service... " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/query?query=$Metric" -UseBasicParsing
        $data = $response.Content | ConvertFrom-Json
        if ($data.data.result) {
            Write-Host "✅ OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️  NÃO ENCONTRADA" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "⚠️  NÃO ENCONTRADA" -ForegroundColor Yellow
        return $false
    }
}

# Verificar se o Docker está rodando
Write-Host "📋 Verificando Docker... " -ForegroundColor Blue -NoNewline
try {
    docker info | Out-Null
    Write-Host "✅ Docker está rodando" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker não está rodando" -ForegroundColor Red
    exit 1
}

# Verificar containers
Write-Host "`n🐳 Verificando containers..." -ForegroundColor Blue
$containers = @("prometheus", "grafana", "jaeger", "alertmanager", "node-exporter", "api", "db")

foreach ($container in $containers) {
    $running = docker ps --format "table {{.Names}}" | Select-String $container
    if ($running) {
        Write-Host "✅ Container $container está rodando" -ForegroundColor Green
    } else {
        Write-Host "❌ Container $container não está rodando" -ForegroundColor Red
    }
}

# Verificar serviços
Write-Host "`n🌐 Verificando endpoints..." -ForegroundColor Blue

Test-Service "Prometheus" "http://localhost:9090" "9090"
Test-Service "Grafana" "http://localhost:3000" "3000"
Test-Service "Jaeger UI" "http://localhost:16686" "16686"
Test-Service "Alertmanager" "http://localhost:9093" "9093"
Test-Service "Node Exporter" "http://localhost:9100/metrics" "9100"
Test-Service "API Health" "http://localhost:8000/health" "8000"
Test-Service "API Metrics" "http://localhost:8000/metrics" "8000"

# Verificar métricas específicas
Write-Host "`n📊 Verificando métricas..." -ForegroundColor Blue

Test-Metric "API" "up{job=`"totem-api`"}"
Test-Metric "Node" "up{job=`"node-exporter`"}"
Test-Metric "Prometheus" "up{job=`"prometheus`"}"

# Verificar alertas
Write-Host "`n🚨 Verificando alertas..." -ForegroundColor Blue -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/alerts" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    if ($data.data.alerts) {
        Write-Host "✅ Alertas configurados" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Nenhum alerta encontrado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Nenhum alerta encontrado" -ForegroundColor Yellow
}

# Verificar dashboards do Grafana
Write-Host "`n📈 Verificando dashboards..." -ForegroundColor Blue -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/dashboards" -UseBasicParsing
    $data = $response.Content | ConvertFrom-Json
    if ($data.dashboards) {
        Write-Host "✅ Dashboards configurados" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Dashboards não encontrados" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Dashboards não encontrados" -ForegroundColor Yellow
}

# Resumo
Write-Host "`n📋 Resumo dos serviços:" -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue
Write-Host "Prometheus: http://localhost:9090"
Write-Host "Grafana: http://localhost:3000 (admin/admin)"
Write-Host "Jaeger: http://localhost:16686"
Write-Host "Alertmanager: http://localhost:9093"
Write-Host "API Health: http://localhost:8000/health"
Write-Host "API Metrics: http://localhost:8000/metrics"

Write-Host "`n✅ Verificação concluída!" -ForegroundColor Green 