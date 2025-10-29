from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .redis_manager import get_sync_redis_client
import logging
from .models import Message


logger = logging.getLogger(__name__)


@shared_task
def cleanup_stale_online_users():
    try:
        redis_client = get_sync_redis_client()
        
        all_users = redis_client.smembers("online_users")
        cleaned = 0
        
        for user_id in all_users:
            exists = redis_client.exists(f"online_user:{user_id}")
            if not exists:
                redis_client.srem("online_users", user_id)
                cleaned += 1
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} stale online users")
        
        return {"cleaned": cleaned, "remaining": len(all_users) - cleaned}
        
    except Exception as error:
        logger.error(f"Error cleaning stale users: {error}")
        return {"error": str(error)}


@shared_task
def cleanup_old_messages():
    try:
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count, _ = Message.objects.filter(timestamp__lt=cutoff_date).delete()
        logger.info(f"Deleted {deleted_count} old messages")

        return {"deleted": deleted_count}
    except Exception as error:
        logger.error(f"Error cleaning up old messages: {error}")
        return {"error": str(error)}