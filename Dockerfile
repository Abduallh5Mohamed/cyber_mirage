# 🐳 Docker build for Honeypot Application

FROM python:3.10-slim

# Create non-root user
RUN useradd -m -u 1000 honeypot && \
    mkdir -p /app /app/data /app/logs && \
    chown -R honeypot:honeypot /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    git \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=honeypot:honeypot . .

# Install Python dependencies in stages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install core dependencies first
RUN pip install --no-cache-dir \
    fastapi==0.120.0 \
    uvicorn==0.38.0 \
    pydantic==2.12.3 \
    psycopg2-binary==2.9.9 \
    redis==5.0.1 \
    requests==2.31.0 \
    python-dotenv==1.0.0 \
    --timeout=300

# Install ML/data science dependencies
RUN pip install --no-cache-dir \
    numpy==2.0.0 \
    pandas==2.1.4 \
    scikit-learn==1.3.2 \
    --timeout=300

# Install remaining dependencies
RUN pip install --no-cache-dir \
    streamlit==1.28.0 \
    plotly==5.17.0 \
    matplotlib==3.8.2 \
    seaborn==0.13.0 \
    --timeout=300 || true

# Set environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production

# Switch to non-root user
USER honeypot

# Expose ports
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "src/api/main.py"]
