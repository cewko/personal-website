from abc import ABC, abstractmethod
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class BaseIntegrationService(ABC):
    cache_timeout = 300
    fallback_cache_timeout = 86400

    @abstractmethod
    def get_cache_key(self):
        pass

    @abstractmethod
    def fetch_data(self):
        pass

    def get_fallback_cache_key(self):
        return f"{self.get_cache_key()}:fallback"

    def get_data(self):
        cache_key = self.get_cache_key()
        fallback_key = self.get_fallback_cache_key()
        data = cache.get(cache_key)

        if data is not None:
            return data

        logger.info(f"Cache miss for {cache_key}, fetching data...")

        try:
            data = self.fetch_data()

            if data is not None:
                cache.set(cache_key, data, self.cache_timeout)
                cache.set(fallback_key, data, self.fallback_cache_timeout)
                logger.info(f"Cached fresh data for {cache_key}")

                return data

        except Exception as error:
            logger.error(f"Error fetching {cache_key}: {error}")
        
        fallback_data = cache.get(fallback_key)

        if fallback_data:
            logger.warning(f"Using fallback cache for {cache_key}")
            return fallback_data
        
        logger.error(f"No data available for {cache_key}")

        return None