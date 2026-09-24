# =============================================================================
# Development Dockerfile
# This configuration is for development only (runs Vite dev server).
# Production should use a proper multi-stage build serving static files.
# =============================================================================
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
