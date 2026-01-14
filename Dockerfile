# Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build backend
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist ./static

# Create uploads directory
RUN mkdir -p uploads

# Railway provides PORT env variable
ENV PORT=8000

# Run the application (uses $PORT from environment)
CMD gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
