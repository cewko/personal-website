from pathlib import Path
from decouple import config, Csv
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# Application definition
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    
    # Third-party apps
    "channels",

    # Local apps
    "apps.pages",
    "apps.weblog",
    "apps.analytics",
    "apps.integrations",
    "apps.hangout",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.analytics.middleware.AnalyticsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Chanells
ASGI_APPLICATION = "core.asgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Sitemaps
SITE_ID = 1


# Celery Configuration
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_EXPIRES = 3600

CELERY_BEAT_SCHEDULE = {
    "refresh-discord-status": {
        "task": "apps.integrations.tasks.refresh_discord_status",
        "schedule": 240.0,  # 4 minutes (cache: 5 min)
    },
    "refresh-lastfm-track": {
        "task": "apps.integrations.tasks.refresh_lastfm_track",
        "schedule": 50.0,  # 50 seconds (cache: 1 min)
    },
    "refresh-weather-data": {
        "task": "apps.integrations.tasks.refresh_weather_data",
        "schedule": 10500.0,  # 2h 55min (cache: 3 hours)
    },
    "refresh-wakatime-stats": {
        "task": "apps.integrations.tasks.refresh_wakatime_stats",
        "schedule": 3300.0,  # 55 minutes (cache: 1 hour)
    },
    "refresh-bluesky-status": {
        "task": "apps.integrations.tasks.refresh_bluesky_status",
        "schedule": 1650.0,  # 27.5 minutes (cache: 30 min)
    },
    "refresh-github-contributions": {
        "task": "apps.integrations.tasks.refresh_github_contributions",
        "schedule": 7020.0,  # 1h 57min (cache: 2 hours)
    },
    "cleanup-stale-online-users": {
        "task": "apps.hangout.tasks.cleanup_stale_online_users",
        "schedule": 120.0,
    },
    "cleanup-old-messages": {
        "task": "apps.hangout.tasks.cleanup_old_messages",
        "schedule": crontab(day_of_month="29", hour="20", minute="58"),
    },
}