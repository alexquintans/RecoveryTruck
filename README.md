# Totem MVP

## Pré-requisitos
- Docker e Docker Compose
- (Opcional) Make

## Subindo o ambiente

```sh
cd infra/compose
# Com Docker Compose
docker-compose up --build
# Ou, se preferir Makefile
make up
```

- API: http://localhost:8000/health
- Totem: http://localhost:3000
- Operador: http://localhost:3001

## Estrutura do Projeto
- apps/api: Backend FastAPI
- apps/totem: Frontend Totem (React/Vite)
- apps/operador: Frontend Operador (React/Vite)
- infra: Infraestrutura (Docker, Compose)
- packages: Libs compartilhadas
- scripts: Scripts utilitários
- docs: Documentação

## Variáveis de Ambiente
Veja `.env.example` para configurar as variáveis necessárias. 