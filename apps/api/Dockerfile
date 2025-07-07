FROM python:3.9-slim

WORKDIR /app

# Instalar curl para health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para cache do Docker
COPY requirements.txt .

# Instalar dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Garante que os imports absolutos funcionem
ENV PYTHONPATH=/app

# Expor a porta
EXPOSE 8000

# Comando de inicialização (ajuste o caminho se necessário)
CMD ["uvicorn", "apps.api.full_api:app", "--host", "0.0.0.0", "--port", "8000"] 