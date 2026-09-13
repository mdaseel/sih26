# ============================================================
#  SolarGrid AI — frontend (Next.js)
# ============================================================
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev || npm install --omit=dev

FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
# Cesium's Workers/Assets/Widgets must exist in public/ at build time —
# they are 7 MB of vendor binaries, gitignored, so we generate them here.
RUN node scripts/copy-cesium-assets.mjs || echo "[cesium] asset copy skipped"
# NEXT_PUBLIC_* values are inlined at build time, so they must be present here.
# Only public values: the service-role key is never passed to this stage.
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_API_BASE_URL
ARG NEXT_PUBLIC_CESIUM_ION_TOKEN
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL \
    NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY \
    NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL \
    NEXT_PUBLIC_CESIUM_ION_TOKEN=$NEXT_PUBLIC_CESIUM_ION_TOKEN
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/next.config.mjs ./next.config.mjs

RUN addgroup -g 10001 solargrid && adduser -u 10001 -G solargrid -D solargrid
USER solargrid

EXPOSE 3000
CMD ["npm", "run", "start"]
