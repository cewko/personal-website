from django import template
from decouple import config
from ..redis_manager import get_sync_redis_client

register = template.Library()


@register.inclusion_tag('hangout/hangout_widget.html')
def hangout_widget():
    return {"online_count": "..."}