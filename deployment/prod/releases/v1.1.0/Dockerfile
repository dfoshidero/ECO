# ECO Embodied Carbon Model API
# Production Dockerfile - model and app are copied in by build script
FROM python:3.11-slim

# Upgrade system packages to address base image CVEs (e.g. tar, binutils)
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip/setuptools/wheel to address PyPI CVEs before installing app deps
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model at build time
RUN python -m spacy download en_core_web_md

# Copy application, model, and version (build context is assembled by build.sh)
COPY app/ ./app/
COPY model/ ./model/
COPY version.json ./

# Ensure appuser owns the app
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

# Health check - only OK when model is loaded (start-period allows time for model load)
HEALTHCHECK --interval=15s --timeout=10s --start-period=90s --retries=3 \
    CMD python -c "import urllib.request; r=urllib.request.urlopen('http://localhost:8080/health'); exit(0 if r.getcode()==200 else 1)" || exit 1

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8080"]
