# ---------- build ----------
FROM node:20-alpine AS build

# instala pnpm
RUN corepack enable && corepack prepare pnpm@8.15.5 --activate

WORKDIR /repo
COPY . .

# remove node_modules existentes para evitar conflitos de plataforma
RUN rm -rf node_modules apps/*/node_modules packages/*/node_modules

# instala TODAS as dependências do mono-repo
RUN pnpm install

# compila apenas o painel
# checagem de tipos antes do build (falha cedo se houver erro TS/JSX)
RUN pnpm --filter ./apps/panel-client run typecheck
RUN pnpm --filter ./apps/panel-client run build

# ---------- run ----------
FROM nginx:alpine
COPY --from=build /repo/apps/panel-client/dist /usr/share/nginx/html
COPY apps/panel-client/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
