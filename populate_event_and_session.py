#!/usr/bin/env python
"""
Populate an Event and Training Session for matching testing.
Uses the 6 trainees created in populate_test_data.py
"""
import os
import sys
import django
from datetime import date, datetime, timedelta

# Setup encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karate.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from core.models import Trainee, Event, EventRegistration, TrainingSession, Attendance

print("\n" + "=" * 80)
print("POPULATING EVENT AND TRAINING SESSION FOR MATCHING")
print("=" * 80 + "\n")

# Get existing trainees
trainees = Trainee.objects.filter(profile__user__username__startswith='trainee').order_by('profile__user__first_name')
print(f"[+] Found {trainees.count()} trainees for event registration")

if trainees.count() == 0:
    print("[-] No trainees found. Run populate_test_data.py first.")
    sys.exit(1)

# ============================================================================
# CREATE EVENT
# ============================================================================
print("\n" + "=" * 80)
print("CREATING EVENT FOR MATCHING")
print("=" * 80 + "\n")

event_date = date.today() + timedelta(days=7)
event, created = Event.objects.get_or_create(
    name='Sparring Tournament - Matching Test',
    defaults={
        'event_date': event_date,
        'location': 'Main Dojo - Competition Arena',
        'description': 'Test event for sparring matches and auto-matching. Trainees will be paired for competition.',
        'registration_deadline': date.today() + timedelta(days=5),
        'max_participants': 50,
        'status': 'open'
    }
)

if created:
    print(f"[+] Created event: {event.name}")
else:
    print(f"[*] Event already exists: {event.name}")

print(f"    Date: {event.event_date}")
print(f"    Location: {event.location}")
print(f"    Status: {event.status}")
print(f"    Max Participants: {event.max_participants}")

# ============================================================================
# REGISTER TRAINEES TO EVENT
# ============================================================================
print("\n" + "=" * 80)
print("REGISTERING TRAINEES TO EVENT")
print("=" * 80 + "\n")

registered_count = 0
for trainee in trainees:
    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        trainee=trainee,
        defaults={'status': 'registered'}
    )
    
    if created:
        trainee_name = trainee.profile.user.get_full_name()
        belt = trainee.get_belt_rank_display()
        weight = trainee.weight
        weight_class = trainee.weight_class
        print(f"[+] {trainee_name:25} | Belt: {belt:12} | Weight: {weight:6.1f}kg | {weight_class:18}")
        registered_count += 1
    else:
        print(f"[*] Already registered: {trainee.profile.user.get_full_name()}")

print(f"\n[+] Total registered: {registered_count}/{trainees.count()}")

# ============================================================================
# CREATE TRAINING SESSION
# ============================================================================
print("\n" + "=" * 80)
print("CREATING TRAINING SESSION")
print("=" * 80 + "\n")

# Create a training session for sparring practice
session_date = date.today() + timedelta(days=3)
session_start = datetime.combine(session_date, datetime.min.time().replace(hour=18, minute=0))
session_end = datetime.combine(session_date, datetime.min.time().replace(hour=19, minute=30))

session, created = TrainingSession.objects.get_or_create(
    title='Sparring Practice Session',
    date=session_date,
    defaults={
        'session_type': 'special',
        'start_time': session_start.time(),
        'end_time': session_end.time(),
        'location': 'Main Dojo - Sparring Area',
        'instructor': 'Master Karate Sensei',
        'description': 'Sparring practice session for event preparation. All trainees should attend.',
        'max_capacity': len(trainees),
        'status': 'scheduled'
    }
)

if created:
    print(f"[+] Created training session: {session.title}")
else:
    print(f"[*] Training session already exists: {session.title}")

print(f"    Date: {session.date}")
print(f"    Time: {session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}")
print(f"    Duration: {session.duration_minutes} minutes")
print(f"    Location: {session.location}")
print(f"    Instructor: {session.instructor}")
print(f"    Max Capacity: {session.max_capacity}")

# ============================================================================
# RECORD ATTENDANCE FOR SESSION
# ============================================================================
print("\n" + "=" * 80)
print("RECORDING ATTENDANCE FOR TRAINING SESSION")
print("=" * 80 + "\n")

attendance_count = 0
for trainee in trainees:
    attendance, created = Attendance.objects.get_or_create(
        trainee=trainee,
        session=session,
        date=session_date,
        defaults={
            'status': 'present',
            'check_in_time': session_start.time()
        }
    )
    
    if created:
        trainee_name = trainee.profile.user.get_full_name()
        print(f"[+] {trainee_name:25} | Status: Present | Check-in: {session_start.time().strftime('%H:%M')}")
        attendance_count += 1
    else:
        print(f"[*] Attendance already recorded: {trainee.profile.user.get_full_name()}")

print(f"\n[+] Total attendance records: {attendance_count}/{trainees.count()}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80 + "\n")

print(f"Event: {event.name}")
print(f"  - Date: {event.event_date}")
print(f"  - Registered Participants: {event.participant_count}")
print(f"  - Status: {event.status}")

print(f"\nTraining Session: {session.title}")
print(f"  - Date: {session.date}")
print(f"  - Time: {session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}")
print(f"  - Attendance Count: {session.attendance_count}")
print(f"  - Total Marked: {session.total_marked}")
print(f"  - Attendance Rate: {session.attendance_rate}%")

print("\nTrainees by Belt Rank:")
belt_groups = {}
for trainee in trainees:
    belt = trainee.get_belt_rank_display()
    if belt not in belt_groups:
        belt_groups[belt] = 0
    belt_groups[belt] += 1

for belt, count in sorted(belt_groups.items()):
    print(f"  - {belt:15}: {count} trainees")

print("\nTrainees by Weight Class:")
weight_groups = {}
for trainee in trainees:
    wc = trainee.weight_class
    if wc not in weight_groups:
        weight_groups[wc] = 0
    weight_groups[wc] += 1

for wc, count in sorted(weight_groups.items()):
    print(f"  - {wc:18}: {count} trainees")

# ============================================================================
# NEXT STEPS
# ============================================================================
print("\n" + "=" * 80)
print("NEXT STEPS FOR MATCHING")
print("=" * 80 + "\n")

print("1. Admin Dashboard:")
print("   - Go to http://localhost:8000/admin/dashboard/")
print("   - Navigate to 'Events' section")

print("\n2. Find Event:")
print(f"   - Look for event: '{event.name}'")
print(f"   - Event date: {event.event_date}")

print("\n3. Auto-Matching:")
print("   - Click 'Auto Matchmaking' button")
print("   - System will propose matches based on:")
print("     * Belt rank similarity")
print("     * Weight class similarity")
print("     * Age proximity")

print("\n4. Review & Confirm Matches:")
print("   - Review proposed matches")
print("   - Confirm to create official matches")

print("\n5. View Matches:")
print("   - All matches will appear in the event's match list")
print("   - Each match shows competitors and scheduling info")

print("\n" + "=" * 80)
print("SETUP COMPLETE!")
print("=" * 80 + "\n")
