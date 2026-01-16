# Generated migration for adding archived field to Match model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_match_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='match',
            index=models.Index(fields=['archived', 'scheduled_time'], name='core_match_archived_scheduled_time_idx'),
        ),
    ]
