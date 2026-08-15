# Stage 1: Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund

# Stage 2: Build application
FROM node:20-alpine AS builder
WORKDIR /app
ARG BACKEND_INTERNAL_URL=http://backend:8000
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV NEXT_TELEMETRY_DISABLED=1
ENV BACKEND_INTERNAL_URL=${BACKEND_INTERNAL_URL}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN mkdir -p public
RUN npm run build

# Stage 3: Production runner
FROM node:20-alpine AS runner
WORKDIR /app
ARG BACKEND_INTERNAL_URL=http://backend:8000
ARG NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV BACKEND_INTERNAL_URL=${BACKEND_INTERNAL_URL}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN apk add --no-cache curl

# Copy only necessary files from builder
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["npm", "run", "start", "--", "-H", "0.0.0.0", "-p", "3000"]
