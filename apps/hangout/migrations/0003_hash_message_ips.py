import hmac
import hashlib
from django.db import migrations, models
from django.conf import settings


def hash_existing_ips(apps, schema_editor):
    Message = apps.get_model("hangout", "Message")
    
    batch_size = 1000
    messages = Message.objects.filter(ip_hash__isnull=True).exclude(
        ip_address__isnull=True
    ).iterator(chunk_size=batch_size)
    
    to_update = []
    for msg in messages:
        msg.ip_hash = hmac.new(
            key=settings.SECRET_KEY.encode(),
            msg=msg.ip_address.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()[:32]
        
        to_update.append(msg)
        
        if len(to_update) >= batch_size:
            Message.objects.bulk_update(to_update, ["ip_hash"])
            to_update = []
    
    if to_update:
        Message.objects.bulk_update(to_update, ["ip_hash"])


class Migration(migrations.Migration):

    dependencies = [
        ("hangout", "0002_message_discord_user_id_message_is_from_discord_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="ip_hash",
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.RunPython(hash_existing_ips, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="message",
            name="ip_address",
        ),
    ]