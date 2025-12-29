from celery import shared_task
from django.core.cache import cache
import logging

from .services import (
    DiscordService,
    LastFmService,
    WeatherService,
    WakatimeService,
    BlueskyService,
    GithubService
)

logger = logging.getLogger(__name__)


def _refresh_integration_data(service_class, service_name):
    try:
        service = service_class()
        data = service.fetch_data()

        if data is not None:
            cache_key = service.get_cache_key()
            fallback_key = service.get_fallback_cache_key()

            cache.set(cache_key, data, service.cache_timeout)
            cache.set(fallback_key, data, service.fallback_cache_timeout)

            logger.info(f"{service_name} refreshed successfully")
            return {"status": "success", "data": data}
        
        logger.warning(f"{service_name} fetch returned None")
        return {"status": "no_data"}

    except Exception as error:
        logger.error(f"Error refreshing {service_name}: {error}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_discord_status(self):
    return _refresh_integration_data(DiscordService, "Discord Status")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_lastfm_track(self):
    return _refresh_integration_data(LastFmService, "Last.fm Track")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_weather_data(self):
    return _refresh_integration_data(WeatherService, "Weather")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_wakatime_stats(self):
    return _refresh_integration_data(WakatimeService, "WakaTime Stats")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_bluesky_status(self):
    return _refresh_integration_data(MastodonService, "Mastodon Status")


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_github_contributions(self):
    return _refresh_integration_data(GithubService, "GitHub contributions")