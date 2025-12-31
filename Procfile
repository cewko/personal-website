release: python manage.py warm_caches
web: daphne -b 0.0.0.0 -p $PORT core.asgi:application & celery -A core worker --loglevel=info -B --concurrency=2