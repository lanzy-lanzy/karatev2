#!/usr/bin/env python
"""
Link existing judge UserProfiles to Judge model records.
"""
import os
import sys
import django
from datetime import date

# Setup encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karate.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import UserProfile, Judge

print("\n" + "=" * 80)
print("LINKING JUDGE USERPROFILES TO JUDGE MODEL")
print("=" * 80 + "\n")

# Get all judge profiles that don't have a Judge record
judge_profiles = UserProfile.objects.filter(role='judge').exclude(judge__isnull=False)

print(f"[+] Found {judge_profiles.count()} judge profiles to link\n")

if judge_profiles.count() == 0:
    print("[-] All judge profiles already linked!")
    sys.exit(0)

linked_count = 0
for profile in judge_profiles:
    judge, created = Judge.objects.get_or_create(
        profile=profile,
        defaults={
            'certification_level': 'regional',
            'certification_date': date.today(),
            'is_active': True
        }
    )
    
    if created:
        judge_name = profile.user.get_full_name()
        print(f"[+] Linked judge: {judge_name:25} | Level: Regional | Active: Yes")
        linked_count += 1
    else:
        print(f"[*] Already linked: {profile.user.get_full_name()}")

print(f"\n[+] Total judges linked: {linked_count}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80 + "\n")

all_judges = Judge.objects.all()
print(f"Total Active Judges: {all_judges.filter(is_active=True).count()}")
print(f"Total Judges: {all_judges.count()}\n")

for judge in all_judges:
    print(f"  - {judge.profile.user.get_full_name():25} | {judge.get_certification_level_display():12} | Active: {judge.is_active}")

print("\n[+] Judges are now visible in Judge Management!")
