from abc import ABC, abstractmethod
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class BaseIntegrationService(ABC):
    cache_timeout = 300
    fallback_cache_timeout = 86400
    task_name = None

    @abstractmethod
    def get_cache_key(self):
        pass

    @abstractmethod
    def fetch_data(self):
        pass

    def get_fallback_cache_key(self):
        return f"{self.get_cache_key()}:fallback"

    def get_refresh_lock_key(self):
        return f"{self.get_cache_key()}:refreshing"

    def get_data(self):
        cache_key = self.get_cache_key()
        fallback_key = self.get_fallback_cache_key()
        
        data = cache.get(cache_key)
        if data is not None:
            return data

        fallback_data = cache.get(fallback_key)
        
        self._trigger_async_refresh()
        
        if fallback_data:
            logger.info(f"Cache miss for {cache_key}, using fallback")
            return fallback_data
        
        logger.warning(f"No cached data available for {cache_key}")
        return None

    def _trigger_async_refresh(self):
        if not self.task_name:
            return
            
        lock_key = self.get_refresh_lock_key()
        
        if cache.get(lock_key):
            return
        
        cache.set(lock_key, True, 60)
        
        try:
            from celery import current_app
            task = current_app.tasks.get(self.task_name)
            if task:
                task.delay()
                logger.info(f"Triggered async refresh for {self.get_cache_key()}")
        except Exception as e:
            logger.error(f"Failed to trigger async refresh: {e}")
            cache.delete(lock_key)

    def fetch_and_cache(self):
        cache_key = self.get_cache_key()
        fallback_key = self.get_fallback_cache_key()
        lock_key = self.get_refresh_lock_key()
        
        try:
            logger.info(f"Fetching fresh data for {cache_key}")
            data = self.fetch_data()

            if data is not None:
                cache.set(cache_key, data, self.cache_timeout)
                cache.set(fallback_key, data, self.fallback_cache_timeout)
                logger.info(f"Cached fresh data for {cache_key}")
                return data
            
            return None

        except Exception as error:
            logger.error(f"Error fetching {cache_key}: {error}")
            raise
        finally:
            cache.delete(lock_key)