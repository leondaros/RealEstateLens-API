#!/usr/bin/env bash
set -e

# Espera opcional pelo banco (se precisar, adicione um wait-for-it aqui)
python manage.py migrate --noinput

# Gunicorn + UvicornWorker (ASGI)
exec python -m gunicorn setup.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT:-8000} \
  --timeout 120
