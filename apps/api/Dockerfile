FROM python:3.9-slim

WORKDIR /app

# Instalar curl para health checks
RUN apt-get update && apt-get install -y curl postgresql-client && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para cache do Docker
COPY apps/api/requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar workspace pnpm
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml ./

# Copiar packages compartilhados
COPY packages/ ./packages/

# Copiar apps
COPY apps/ ./apps/

# Garante que os imports absolutos funcionem
ENV PYTHONPATH=/app

# Expor a porta (Railway usa $PORT)
EXPOSE 8000

# Comando de inicialização com porta dinâmica
CMD uvicorn apps.api.full_api:app --host 0.0.0.0 --port 8000 