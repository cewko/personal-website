import hmac
import hashlib
from django.db import migrations 
from django.conf import settings


def hash_existing_ips(apps, schema_editor):
    Visit = apps.get_model("analytics", "Visit")

    batch_size = 1000
    visits = Visit.objects.filter(ip_hash__isnull=True).exclude(
        ip_address__isnull=True
    ).iterator(chunk_size=batch_size)

    to_update = []
    for visit in visits:
        if visit.ip_address:
            visit.ip_hash = hmac.new(
                key=settings.SECRET_KEY.encode(),
                msg=visit.ip_address.encode(),
                digestmod=hashlib.sha256
            ).hexdigest()[:32]

        to_update.append(visit)

        if len(to_update) >= batch_size:
            Visit.objects.bulk_update(to_update, ["ip_hash"])
            to_update = []

    if to_update:
        Visit.objects.bulk_update(to_update, ["ip_hash"])

    
class Migration(migrations.Migration):
    dependencies = [
        ("analytics", "0002_visit_ip_hash"),
    ]

    operations = [
        migrations.RunPython(hash_existing_ips, migrations.RunPython.noop)
    ]
