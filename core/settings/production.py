from .base import *
from decouple import config, Csv
import dj_database_url
import ssl

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Redis Configuration
REDIS_URL = config('REDIS_URL')

# Cache Configuration with SSL support
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "ssl_cert_reqs": None,
        } if REDIS_URL.startswith('rediss://') else {},
    }
}

# Channel Layers - add SSL parameters to Redis URL if needed
CHANNEL_REDIS_URL = REDIS_URL
if REDIS_URL.startswith('rediss://'):
    # Add SSL parameters to disable certificate verification
    CHANNEL_REDIS_URL = f"{REDIS_URL}?ssl_cert_reqs=none"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [CHANNEL_REDIS_URL],
        },
    },
}

# Celery Configuration with SSL support
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_USE_SSL = {'ssl_cert_reqs': ssl.CERT_NONE} if REDIS_URL.startswith('rediss://') else None
CELERY_REDIS_BACKEND_USE_SSL = {'ssl_cert_reqs': ssl.CERT_NONE} if REDIS_URL.startswith('rediss://') else None

# Additional Celery settings for stability
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
CELERY_REDIS_SOCKET_CONNECT_TIMEOUT = 30
CELERY_REDIS_SOCKET_TIMEOUT = 30
CELERY_BROKER_POOL_LIMIT = None
CELERY_BROKER_CONNECTION_TIMEOUT = 30
CELERY_RESULT_BACKEND_CONNECTION_RETRY = True
CELERY_RESULT_BACKEND_CONNECTION_MAX_RETRIES = 10

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True