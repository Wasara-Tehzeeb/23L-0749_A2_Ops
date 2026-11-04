FROM python:3.13-slim

WORKDIR /app

# Install dependencies before application code for layer caching
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application files
COPY app.py .
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/

# Create a non-root user and writable database directory
RUN useradd --create-home appuser && \
    mkdir -p /app/storage && \
    chown -R appuser:appuser /app

USER appuser

# Load the champion model from a mounted directory
ENV LOCAL_MODEL_PATH=/app/champion_model
ENV DATABASE_PATH=/app/storage/visionguard.db

# Flask application port
EXPOSE 5001

# Check application health
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health')" || exit 1

# Start Flask application
CMD ["python", "app.py"]