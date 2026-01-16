# Generated migration for TraineeEvaluation model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0020_rename_core_payment_archive_payment_date_idx_core_paymen_archive_9421b1_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='TraineeEvaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('technique', models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=3, help_text='Overall technique proficiency')),
                ('speed', models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=3, help_text='Speed and reaction time')),
                ('strength', models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=3, help_text='Physical strength')),
                ('flexibility', models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=3, help_text='Flexibility and range of motion')),
                ('discipline', models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=3, help_text='Discipline and focus')),
                ('spirit', models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=3, help_text='Fighting spirit and determination')),
                ('overall_rating', models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=3, help_text='Overall performance rating')),
                ('comments', models.TextField(blank=True, help_text='Detailed comments and feedback')),
                ('strengths', models.TextField(blank=True, help_text='Key strengths to build upon')),
                ('areas_for_improvement', models.TextField(blank=True, help_text='Areas that need improvement')),
                ('recommendations', models.TextField(blank=True, help_text='Recommendations for training and development')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('archived', 'Archived')], default='pending', max_length=20)),
                ('evaluated_at', models.DateTimeField(auto_now_add=True)),
                ('next_evaluation_date', models.DateField(blank=True, help_text='Recommended date for next evaluation', null=True)),
                ('archived', models.BooleanField(default=False)),
                ('evaluator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evaluations_given', to=settings.AUTH_USER_MODEL)),
                ('trainee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='core.trainee')),
            ],
            options={
                'ordering': ['-evaluated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='traineeevaluation',
            index=models.Index(fields=['trainee', '-evaluated_at'], name='core_trainee_trainee__373947_idx'),
        ),
        migrations.AddIndex(
            model_name='traineeevaluation',
            index=models.Index(fields=['archived', '-evaluated_at'], name='core_trainee_archive_a84919_idx'),
        ),
    ]
