from celery import shared_task
from .models import Visit


@shared_task
def record_visit_async(ip_hash):
    Visit.objects.create(ip_hash=ip_hash)