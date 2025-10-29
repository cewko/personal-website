# deprecated, keeping for backward compatibility

from .redis_manager import get_async_redis_client, get_sync_redis_client

__all__ = ['get_async_redis_client', 'get_sync_redis_client']