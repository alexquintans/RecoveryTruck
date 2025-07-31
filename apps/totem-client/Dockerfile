# ---------- build ----------
    FROM node:20-alpine AS build

    # instala pnpm
    RUN corepack enable && corepack prepare pnpm@10.12.4 --activate
    
    WORKDIR /repo
    COPY . .
    
    # Copia o arquivo de ambiente específico e o renomeia para .env, que é o padrão que o Vite procura
COPY apps/totem-client/frontend.env apps/totem-client/.env

# Debug: veja se o arquivo está lá
RUN ls -l /repo/

# instala TODAS as dependências do mono-repo (incluindo @mercadopago/sdk-react)
RUN pnpm install

# compila apenas o totem
RUN pnpm --filter ./apps/totem-client run build

# ---------- run ----------
FROM nginx:alpine
# Copiar o build da aplicação para o diretório do Nginx
COPY --from=build /repo/apps/totem-client/dist /usr/share/nginx/html

# Copiar a configuração personalizada do Nginx
COPY apps/totem-client/nginx.conf /etc/nginx/conf.d/default.conf

    # Expor a porta 80
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]
    