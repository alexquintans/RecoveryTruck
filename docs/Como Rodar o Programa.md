Read file: apps/totem-client/package.json
Read file: apps/panel-client/package.json

Read file: apps/api/main.py

Comandos (modo desenvolvimento)
===============================

1. Backend – FastAPI  
```bash
# a partir da raiz do repositório
cd apps/api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
• `--reload` recarrega a API quando salvar arquivos.  
• Porta 8000 é a usada nos .env dos front-ends (`VITE_API_URL=http://localhost:8000`).

2. Totem (apps/totem-client)  
```bash
cd apps/totem-client
npm install        # 1ª vez
npm run dev -- --host --port 5173      # abre em http://localhost:5173
```
(o `--host` permite acesso da rede local caso o tablet esteja na mesma LAN).

3. Painel/Operador (apps/panel-client)  
```bash
cd apps/panel-client
npm install
npm run dev -- --host --port 5174      # http://localhost:5174
```

Observações
-----------

• Se usar **pnpm** (projeto é monorepo), basta:

```bash
pnpm install          # instala tudo de uma vez

# janela 1
pnpm --filter api dev           # roda uvicorn (script mapeado no package.json raiz, se criar)

# janela 2
pnpm --filter totem-client dev

# janela 3
pnpm --filter panel-client dev
```

• Variáveis de ambiente estão em `apps/api/backend.env`, `apps/totem-client/frontend.env` e `apps/panel-client/frontend.env`.  
  Certifique-se de copiá-las para `.env` (ou `set VAR=value` no Windows) antes de iniciar.

• Para build de produção:  
```bash
# API (imagem Docker)
docker build -t totem-api ./apps/api

# Front-ends (geram dist/)
cd apps/totem-client && npm run build
cd apps/panel-client && npm run build
```

Pronto: com esses três comandos em terminais diferentes você tem backend, totem e painel rodando em tempo-real.