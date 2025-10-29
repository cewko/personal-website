import redis.asyncio as redis_async
import redis as redis_sync
from decouple import config
import threading


class RedisConnectionManager:
    _instance = None
    _lock = threading.Lock()
    _async_pool = None
    _sync_pool = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._setup_pools()

    def _get_redis_url_with_ssl(self):
        redis_url = config("REDIS_URL", default="redis://localhost:6379")
        
        if redis_url.startswith("rediss://"):
            if "?" in redis_url:
                redis_url += "&ssl_cert_reqs=none"
            else:
                redis_url += "?ssl_cert_reqs=none"
        
        return redis_url

    def _setup_pools(self):
        redis_url = self._get_redis_url_with_ssl()
        
        self._async_pool = redis_async.ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
            max_connections=8,
            socket_keepalive=True,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )
        
        self._sync_pool = redis_sync.ConnectionPool.from_url(
            redis_url,
            decode_responses=True,
            max_connections=6,
            socket_keepalive=True,
            socket_connect_timeout=5,
            retry_on_timeout=True
        )

    def get_async_client(self):
        return redis_async.Redis(connection_pool=self._async_pool)
    
    def get_sync_client(self):
        return redis_sync.Redis(connection_pool=self._sync_pool)
    
    async def close_async_pool(self):
        if self._async_pool:
            await self._async_pool.disconnect()
    
    def close_sync_pool(self):
        if self._sync_pool:
            self._sync_pool.disconnect()


_redis_manager = RedisConnectionManager()


def get_async_redis_client():
    return _redis_manager.get_async_client()


def get_sync_redis_client():
    return _redis_manager.get_sync_client()