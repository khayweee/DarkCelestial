# Client Dockerfile
FROM node:25-slim AS builder
WORKDIR /app

# Copy package.json
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Build NEXT JS App
RUN npm run build

# Runner stage
FROM node:25-slim AS runner
WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

CMD ["npm", "start"]
