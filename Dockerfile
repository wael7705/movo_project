FROM python:3.11-slim

WORKDIR /app

# Keep Python lean and logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Ensure backend package is importable (backend/core → import core)
ENV PYTHONPATH=/app/backend:${PYTHONPATH}

# System deps (curl for healthchecks)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App source
COPY . .

# Gunicorn workers (can be overridden at runtime)
ENV WORKERS=4

# Start Gunicorn with Uvicorn workers
CMD ["bash","-lc","exec gunicorn ${APP_MODULE:-backend.app:app} -k uvicorn.workers.UvicornWorker --workers ${WORKERS:-4} --bind 0.0.0.0:8000 --timeout 60"]
