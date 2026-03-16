# Development: hot reload with proper dependency caching
FROM node:20-alpine AS dev

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json package-lock.json* ./

# Install dependencies in the image
RUN npm ci --prefer-offline --no-audit

# Copy source code (node_modules excluded via .dockerignore)
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]

# Production: optimized build with multi-stage
FROM node:20-alpine AS prod-deps

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline --no-audit --production

FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline --no-audit

COPY . .
RUN npm run build

FROM node:20-alpine AS prod

WORKDIR /app

ENV NODE_ENV=production

# Copy only production dependencies and build output
COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.js ./next.config.js

EXPOSE 3000

CMD ["npm", "start"]
