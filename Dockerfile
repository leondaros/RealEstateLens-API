FROM python:3.12-slim

# libs nativas para GeoDjango
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin libgdal-dev libgeos-dev proj-bin proj-data libproj-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GDAL_DATA=/usr/share/gdal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Roda migrações e coleta estáticos
RUN python manage.py migrate && python manage.py collectstatic --noinput

CMD ["gunicorn","setup.wsgi:application","--bind","0.0.0.0:10000","--log-file","-"]
