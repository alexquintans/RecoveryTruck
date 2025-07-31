FROM python:3.9-slim

WORKDIR /app

# Instalar curl para health checks
RUN apt-get update && apt-get install -y curl postgresql-client && rm -rf /var/lib/apt/lists/*

# Copiar requirements mínimo primeiro para cache do Docker
COPY apps/api/requirements_minimal.txt requirements.txt

# Instalar dependências Python mínimas
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar apenas a API mínima
COPY apps/api/minimal_api.py ./apps/api/

# Garante que os imports absolutos funcionem
ENV PYTHONPATH=/app

# Expor a porta (Railway usa $PORT)
EXPOSE 8000

# Comando de inicialização com porta dinâmica - usando API mínima
CMD uvicorn apps.api.minimal_api:app --host 0.0.0.0 --port $PORT 