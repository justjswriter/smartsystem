FROM node:24-alpine AS build

WORKDIR /app

ARG VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY smart-plant-frontend/package*.json ./
RUN npm ci

COPY smart-plant-frontend ./
RUN npm run build

FROM nginx:1.29-alpine

COPY smart-plant-frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
