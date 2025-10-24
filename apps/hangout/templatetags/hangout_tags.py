from django import template
import redis
from decouple import config
from ..redis_utils import get_sync_redis_client

register = template.Library()


@register.inclusion_tag('hangout/hangout_widget.html')
def hangout_widget():
    try:
        redis_client = get_sync_redis_client()
        online_count = redis_client.scard("online_users")
        redis_client.close()
    except Exception as e:
        print(f"Redis error: {e}")
        online_count = 0
    
    return {"online_count": online_count}