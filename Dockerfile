# Production Dockerfile for Autonomous Email Server
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    libssl-dev \
    libpq-dev \
    libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY implementation/ ./implementation/
COPY config/ ./config/
COPY hmailserver/source/ ./hmailserver/source/

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/models

# Set environment variables
ENV PYTHONPATH=/app
ENV AUTONOMOUS_MODE=production
ENV LOG_LEVEL=info

# Expose email server ports
EXPOSE 25 587 993 995 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run the autonomous email server
CMD ["python", "implementation/autonomous_email_server.py"]