# frontend/Dockerfile
# --- Stage 1: Build React Client ---
FROM node:20-alpine AS build-stage

WORKDIR /app

# Copy package configurations
COPY package*.json ./
RUN npm install

# Copy source code files
COPY . .

# Set production API URL during build if needed
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# Build client files
RUN npm run build

# --- Stage 2: Serve using Nginx ---
FROM nginx:stable-alpine AS production-stage

# Copy compiled assets from Stage 1
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration to support HTML5 history API Routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose Nginx port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
