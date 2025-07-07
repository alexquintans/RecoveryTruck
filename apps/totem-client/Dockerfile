# ---------- build ----------
    FROM node:20-alpine AS build

    # instala pnpm
    RUN corepack enable && corepack prepare pnpm@8.15.5 --activate
    
    WORKDIR /repo
    COPY . .
    
    COPY apps/totem-client/.env apps/totem-client/.env
    
    # Debug: veja se o arquivo está lá
    RUN ls -l /repo/apps/totem-client/
    
    # instala TODAS as dependências do mono-repo
    RUN pnpm install
    
    # compila apenas o totem
    RUN pnpm --filter ./apps/totem-client run build
    
    # ---------- run ----------
    FROM nginx:alpine
    COPY --from=build /repo/apps/totem-client/dist /usr/share/nginx/html
    # encurta logs
    RUN sed -i 's|access_log .*;|access_log  /dev/stdout;|' /etc/nginx/conf.d/default.conf
    EXPOSE 80
    CMD ["nginx", "-g", "daemon off;"]
    