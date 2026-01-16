# Generated migration for adding archived field to Event model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_registration'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['archived', '-event_date'], name='core_event_archived_event_date_idx'),
        ),
    ]
