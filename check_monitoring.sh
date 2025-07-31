#!/bin/bash

# Script para verificar se todos os serviços de monitoramento estão funcionando
# Execute: ./check_monitoring.sh

echo "🔍 Verificando serviços de monitoramento do Totem..."
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para verificar se um serviço está respondendo
check_service() {
    local name=$1
    local url=$2
    local port=$3
    
    echo -n "Verificando $name... "
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FALHOU${NC}"
        return 1
    fi
}

# Função para verificar métricas específicas
check_metrics() {
    local service=$1
    local metric=$2
    
    echo -n "Verificando métrica $metric em $service... "
    
    if curl -s "http://localhost:9090/api/v1/query?query=$metric" | grep -q "result"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  NÃO ENCONTRADA${NC}"
        return 1
    fi
}

# Verificar se o Docker está rodando
echo -e "${BLUE}📋 Verificando Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Docker está rodando${NC}"
fi

# Verificar containers
echo -e "\n${BLUE}🐳 Verificando containers...${NC}"
containers=("prometheus" "grafana" "jaeger" "alertmanager" "node-exporter" "api" "db")

for container in "${containers[@]}"; do
    if docker ps --format "table {{.Names}}" | grep -q "$container"; then
        echo -e "${GREEN}✅ Container $container está rodando${NC}"
    else
        echo -e "${RED}❌ Container $container não está rodando${NC}"
    fi
done

# Verificar serviços
echo -e "\n${BLUE}🌐 Verificando endpoints...${NC}"

check_service "Prometheus" "http://localhost:9090" "9090"
check_service "Grafana" "http://localhost:3000" "3000"
check_service "Jaeger UI" "http://localhost:16686" "16686"
check_service "Alertmanager" "http://localhost:9093" "9093"
check_service "Node Exporter" "http://localhost:9100/metrics" "9100"
check_service "API Health" "http://localhost:8000/health" "8000"
check_service "API Metrics" "http://localhost:8000/metrics" "8000"

# Verificar métricas específicas
echo -e "\n${BLUE}📊 Verificando métricas...${NC}"

check_metrics "API" "up{job=\"totem-api\"}"
check_metrics "Node" "up{job=\"node-exporter\"}"
check_metrics "Prometheus" "up{job=\"prometheus\"}"

# Verificar alertas
echo -e "\n${BLUE}🚨 Verificando alertas...${NC}"
if curl -s "http://localhost:9090/api/v1/alerts" | grep -q "alerts"; then
    echo -e "${GREEN}✅ Alertas configurados${NC}"
else
    echo -e "${YELLOW}⚠️  Nenhum alerta encontrado${NC}"
fi

# Verificar dashboards do Grafana
echo -e "\n${BLUE}📈 Verificando dashboards...${NC}"
if curl -s "http://localhost:3000/api/dashboards" | grep -q "dashboards"; then
    echo -e "${GREEN}✅ Dashboards configurados${NC}"
else
    echo -e "${YELLOW}⚠️  Dashboards não encontrados${NC}"
fi

# Resumo
echo -e "\n${BLUE}📋 Resumo dos serviços:${NC}"
echo "=================================================="
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000 (admin/admin)"
echo "Jaeger: http://localhost:16686"
echo "Alertmanager: http://localhost:9093"
echo "API Health: http://localhost:8000/health"
echo "API Metrics: http://localhost:8000/metrics"

echo -e "\n${GREEN}✅ Verificação concluída!${NC}" 