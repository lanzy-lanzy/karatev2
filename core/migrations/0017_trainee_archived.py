# Generated migration for adding archived field to Trainee model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_rename_core_match_archived_scheduled_time_idx_core_match_archive_63503f_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainee',
            name='archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='trainee',
            index=models.Index(fields=['archived', '-joined_date'], name='core_trainee_archived_joined_date_idx'),
        ),
        migrations.AlterModelOptions(
            name='trainee',
            options={'ordering': ['profile__user__first_name', 'profile__user__last_name']},
        ),
    ]
