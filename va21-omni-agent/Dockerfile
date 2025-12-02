# Stage 1: Build the frontend
FROM node:18 AS build
WORKDIR /app/frontend
COPY frontend/package.json .
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Build the backend
FROM python:3.10-slim

# Install system dependencies for sandbox and PTY support
RUN apt-get update && apt-get install -y \
    bash \
    procps \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy frontend build
COPY --from=build /app/frontend/build ./frontend/build

# Copy backend
COPY backend/ ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Create necessary directories for the vault and data
RUN mkdir -p /app/data/research_vault \
    /app/data/redaction_logs \
    /app/data/self_healing

# Create a non-root user for security
RUN useradd -m -s /bin/bash va21user
RUN chown -R va21user:va21user /app
USER va21user

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV VA21_DATA_DIR=/app/data
ENV VA21_VAULT_PATH=/app/data/research_vault

# Expose the Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/research/health || exit 1

# Start the application
WORKDIR /app/backend
CMD ["python", "app.py", "--settings_path", "/app/data/settings.json"]
