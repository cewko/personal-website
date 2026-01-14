from celery import shared_task
from .models import Visit


@shared_task
def record_visit_async(ip_address):
    Visit.objects.create(ip_address=ip_address)