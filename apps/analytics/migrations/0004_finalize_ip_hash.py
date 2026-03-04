from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("analytics", "0003_hash_existing_ips"),
    ]

    operations = [
        # make ip_hash non nullable cause all rows were populated
        migrations.AlterField(
            model_name="visit",
            name="ip_hash",
            field=models.CharField(max_length=32, db_index=True)
        ),
        # remove old ip field
        migrations.RemoveField(
            model_name="visit",
            name="ip_address",
        ),
    ]