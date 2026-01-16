# Generated migration for Payment archiving

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_rename_core_match_archived_scheduled_time_idx_core_match_archive_63503f_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['archived', '-payment_date'], name='core_payment_archive_payment_date_idx'),
        ),
    ]
