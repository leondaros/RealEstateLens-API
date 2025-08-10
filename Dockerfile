# ---- Base ----
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependências do sistema (Postgres/GDAL p/ django.contrib.gis)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gdal-bin libgdal-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requisitos
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . /app/

# ---- Runtime ----
FROM base AS runtime

# Script de start
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Render injeta $PORT
ENV PORT=8000

CMD ["/app/start.sh"]
