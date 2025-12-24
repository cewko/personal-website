from celery import shared_task
from django.core.cache import cache
import logging

from .services import (
    DiscordService,
    LastFmService,
    WeatherService,
    WakatimeService,
    MastodonService,
    GithubService
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_discord_status(self):
    try:
        service = DiscordService()
        data = service.fetch_data()
        if data is not None:
            cache_key = service.get_cache_key()
            fallback_key = service.get_fallback_cache_key()
            
            cache.set(cache_key, data, service.cache_timeout)
            cache.set(fallback_key, data, service.fallback_cache_timeout)
            
            logger.info(f"Discord status refreshed: {data['status']}")
            return {"status": "success", "data": data}
        logger.warning("Discord status fetch returned None")
        return {"status": "no_data"}
    except Exception as error:
        logger.error(f"Error refreshing Discord status: {error}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_lastfm_track(self):
    try:
        service = LastFmService()
        data = service.fetch_data()
        if data is not None:
            cache_key = service.get_cache_key()
            fallback_key = service.get_fallback_cache_key()
            
            cache.set(cache_key, data, service.cache_timeout)
            cache.set(fallback_key, data, service.fallback_cache_timeout)
            
            logger.info(f"Last.fm track refreshed: {data['artist']} - {data['name']}")
            return {"status": "success", "data": data}
        logger.warning("Last.fm track fetch returned None")
        return {"status": "no_data"}
    except Exception as error:
        logger.error(f"Error refreshing Last.fm track: {error}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_weather_data(self):
    try:
        service = WeatherService()
        data = service.fetch_data()
        if data is not None:
            cache_key = service.get_cache_key()
            fallback_key = service.get_fallback_cache_key()
            
            cache.set(cache_key, data, service.cache_timeout)
            cache.set(fallback_key, data, service.fallback_cache_timeout)
            
            logger.info(f"Weather data refreshed: {data['temperature']}°C, {data['description']}")
            return {"status": "success", "data": data}
        logger.warning("Weather data fetch returned None")
        return {"status": "no_data"}
    except Exception as error:
        logger.error(f"Error refreshing weather data: {error}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_wakatime_stats(self):
    try:
        service = WakatimeService()
        data = service.fetch_data()
        if data is not None:
            cache_key = service.get_cache_key()
            fallback_key = service.get_fallback_cache_key()
            
            cache.set(cache_key, data, service.cache_timeout)
            cache.set(fallback_key, data, service.fallback_cache_timeout)
            
            logger.info(f"Wakatime stats refreshed: {data['total_hours']}h {data['total_minutes']}m")
            return {"status": "success", "data": data}
        logger.warning("Wakatime stats fetch returned None")
        return {"status": "no_data"}
    except Exception as error:
        logger.error(f"Error refreshing Wakatime stats: {error}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_mastodon_status(self):
    try:
        service = MastodonService()
        data = service.fetch_data()
        if data is not None:
            cache_key = service.get_cache_key()
            fallback_key = service.get_fallback_cache_key()
            
            cache.set(cache_key, data, service.cache_timeout)
            cache.set(fallback_key, data, service.fallback_cache_timeout)
            
            logger.info(f"Mastodon status refreshed: {data['username']}")
            return {"status": "success", "data": data}
        logger.warning("Mastodon status fetch returned None")
        return {"status": "no_data"}
    except Exception as error:
        logger.error(f"Error refreshing Mastodon status: {error}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    retry_backoff=True,
    retry_jitter=True
)
def refresh_github_contributions(self):
    try:
        service = GithubService()
        data = service.fetch_data()
        if data is not None:
            cache_key = service.get_cache_key()
            fallback_key = service.get_fallback_cache_key()
            
            cache.set(cache_key, data, service.cache_timeout)
            cache.set(fallback_key, data, service.fallback_cache_timeout)
            
            logger.info(f"GitHub contributions refreshed: {data['total_contributions']} total")
            return {"status": "success", "data": data}
        logger.warning("GitHub contributions fetch returned None")
        return {"status": "no_data"}
    except Exception as error:
        logger.error(f"Error refreshing GitHub contributions: {error}")
        raise