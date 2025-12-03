# 🛡️ Cyber Mirage v5.0 - Main Dockerfile
# Production-ready multi-stage build

FROM python:3.10-slim as builder

# Build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements
WORKDIR /tmp
COPY requirements.txt .
COPY requirements-production.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-production.txt

# ============================================================
# Production stage
# ============================================================
FROM python:3.10-slim

# Create non-root user
RUN groupadd -r cybermirage && useradd -r -g cybermirage -u 1000 cybermirage && \
    mkdir -p /app /app/data /app/logs /app/config && \
    chown -R cybermirage:cybermirage /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=cybermirage:cybermirage ./src ./src
COPY --chown=cybermirage:cybermirage ./data ./data
COPY --chown=cybermirage:cybermirage ./config ./config

# Create necessary directories
RUN mkdir -p \
    /app/logs \
    /app/data/models \
    /app/data/captures \
    /app/data/sessions && \
    chown -R cybermirage:cybermirage /app

# Switch to non-root user
USER cybermirage

# Expose ports
EXPOSE 8080 8001 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command (can be overridden)
CMD ["python", "-u", "src/honeypots/honeypot_manager.py"]
