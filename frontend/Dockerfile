# Stage 1: Build React SPA
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source code and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Remove default nginx html
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with API proxy and SPA fallback
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

