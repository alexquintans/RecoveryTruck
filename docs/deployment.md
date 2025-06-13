# Deploy do Sistema Totem

Este documento descreve o processo de deploy e configuração do sistema Totem.

## Arquitetura

### Componentes

- **API**: FastAPI + Uvicorn
- **Database**: PostgreSQL
- **Cache**: Redis
- **Message Queue**: RabbitMQ
- **Monitoring**: Prometheus + Grafana
- **Logging**: OpenTelemetry + Jaeger

### Infraestrutura

- **Container**: Docker
- **Orchestration**: Docker Compose
- **CI/CD**: GitHub Actions
- **Registry**: Docker Hub

## Ambiente de Desenvolvimento

### Requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+
- Node.js 16+

### Setup

1. **Clone do Repositório**
   ```bash
   git clone https://github.com/totem/totem.git
   cd totem
   ```

2. **Configuração do Ambiente**
   ```bash
   cp .env.example .env
   # Edite .env com suas configurações
   ```

3. **Build dos Containers**
   ```bash
   docker-compose build
   ```

4. **Inicialização**
   ```bash
   docker-compose up -d
   ```

## Ambiente de Produção

### Requisitos

- Servidor Linux (Ubuntu 20.04+)
- 4+ CPUs
- 8GB+ RAM
- 100GB+ SSD

### Setup

1. **Preparação do Servidor**
   ```bash
   # Instalar Docker
   curl -fsSL https://get.docker.com | sh
   
   # Instalar Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Configuração do Ambiente**
   ```bash
   # Criar diretório
   mkdir -p /opt/totem
   cd /opt/totem
   
   # Copiar arquivos
   scp totem.tar.gz user@server:/opt/totem/
   tar xzf totem.tar.gz
   
   # Configurar ambiente
   cp .env.example .env
   # Edite .env com configurações de produção
   ```

3. **Deploy**
   ```bash
   # Build e deploy
   docker-compose -f docker-compose.prod.yml build
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Configuração

### Variáveis de Ambiente

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=false

# Database
DB_HOST=db
DB_PORT=5432
DB_NAME=totem
DB_USER=postgres
DB_PASSWORD=secret

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Monitoring
PROMETHEUS_HOST=prometheus
PROMETHEUS_PORT=9090
GRAFANA_HOST=grafana
GRAFANA_PORT=3000
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: 
      context: .
      dockerfile: apps/api/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/totem
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - db
      - redis
      - rabbitmq
    networks:
      - totem-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=totem
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - totem-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7
    volumes:
      - redis_data:/data
    networks:
      - totem-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - totem-network
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "check_port_connectivity"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:

networks:
  totem-network:
    driver: bridge
```

## CI/CD

### GitHub Actions

```yaml
name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t totem/api .
      - name: Push to Docker Hub
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push totem/api

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          ssh ${{ secrets.SSH_HOST }} 'cd /opt/totem && docker-compose pull && docker-compose up -d'
```

## Monitoramento

### Health Checks

- API: `/health`
- Database: `pg_isready`
- Redis: `PING`
- RabbitMQ: `check_port_connectivity`

### Métricas

- Prometheus: `/metrics`
- Grafana: Dashboards
- Jaeger: Traces

## Backup

### Database

```bash
# Backup
pg_dump -U postgres totem > backup.sql

# Restore
psql -U postgres totem < backup.sql
```

### Volumes

```bash
# Backup
tar czf volumes.tar.gz /var/lib/docker/volumes/totem_*

# Restore
tar xzf volumes.tar.gz -C /var/lib/docker/volumes/
```

## Troubleshooting

### Problemas Comuns

1. **Container não inicia**
   - Verificar logs: `docker-compose logs`
   - Verificar health checks
   - Validar configurações

2. **Database não conecta**
   - Verificar credenciais
   - Validar network
   - Checar volumes

3. **API não responde**
   - Verificar logs
   - Validar dependências
   - Checar configurações

### Soluções

1. **Container não inicia**
   ```bash
   # Rebuild
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Database não conecta**
   ```bash
   # Reset
   docker-compose down -v
   docker-compose up -d
   ```

3. **API não responde**
   ```bash
   # Restart
   docker-compose restart api
   ```

## Manutenção

### Atualizações

```bash
# Pull latest
git pull origin main

# Rebuild
docker-compose build

# Restart
docker-compose up -d
```

### Limpeza

```bash
# Remove unused
docker system prune

# Clean volumes
docker volume prune
```

### Logs

```bash
# View logs
docker-compose logs -f

# Rotate logs
docker-compose exec api logrotate -f /etc/logrotate.conf
``` 