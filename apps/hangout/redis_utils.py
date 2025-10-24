import redis.asyncio as redis_async
import redis as redis_sync
from decouple import config


def get_redis_url_with_ssl():
    redis_url = config("REDIS_URL", default="redis://localhost:6379")
    
    # If using SSL (rediss://), append ssl_cert_reqs parameter
    if redis_url.startswith("rediss://"):
        # Check if URL already has parameters
        if "?" in redis_url:
            redis_url += "&ssl_cert_reqs=none"
        else:
            redis_url += "?ssl_cert_reqs=none"
    
    return redis_url


def get_async_redis_client():
    redis_url = get_redis_url_with_ssl()
    
    return redis_async.from_url(
        redis_url,
        decode_responses=True
    )


def get_sync_redis_client():
    redis_url = get_redis_url_with_ssl()
    
    return redis_sync.from_url(
        redis_url,
        decode_responses=True
    )