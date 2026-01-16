# Merge migrations to consolidate conflicting branches
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0011_match_archived'),
        ('core', '0012_match_archived_FINAL'),
    ]
    operations = []
