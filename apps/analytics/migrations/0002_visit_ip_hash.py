from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("analytics", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="visit",
            name="ip_hash",
            field=models.CharField(max_length=32, null=True, blank=True)
        ),
    ]