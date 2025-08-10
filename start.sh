#!/usr/bin/env bash
set -e

echo "==> collectstatic"
python manage.py collectstatic --noinput

echo "==> migrate"
python manage.py migrate --noinput

echo "==> start gunicorn (ASGI)"
exec python -m gunicorn setup.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT:-8000} \
  --timeout 120
