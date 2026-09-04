# Sovereign On-Premise Agentic AI Workbench - Dockerfile
# SIH 2026 Problem Statement 26117 (MRPL)
# Air-Gapped / Isolated Production Container

FROM python:3.11-slim

# System dependencies for document intelligence & PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Set Air-Gapped and Sovereign Environment Directives
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_OFFLINE=1 \
    HF_HUB_OFFLINE=1 \
    HF_DATASETS_OFFLINE=1 \
    AIR_GAPPED_MODE=true

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY . .

# Create required persistent data storage directories
RUN mkdir -p data/db data/vault data/faiss_index data/extracted data/visuals

EXPOSE 8000

# Health check probe against the sovereign health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

