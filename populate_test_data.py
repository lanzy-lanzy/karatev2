#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

# Setup encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "karate.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, Trainee
from decimal import Decimal

# Clear existing test users if needed
print("Populating test data...")

# Create 6 Trainees
trainees_data = [
    {
        "username": "trainee1",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@example.com",
        "weight": "75.50",
        "belt": "white",
        "dob": date.today() - timedelta(days=365*25),  # 25 years old
        "emergency_contact": "Jane Smith",
        "emergency_phone": "555-0001",
    },
    {
        "username": "trainee2",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah@example.com",
        "weight": "65.00",
        "belt": "green",
        "dob": date.today() - timedelta(days=365*28),  # 28 years old
        "emergency_contact": "Mike Johnson",
        "emergency_phone": "555-0002",
    },
    {
        "username": "trainee3",
        "first_name": "Michael",
        "last_name": "Brown",
        "email": "michael@example.com",
        "weight": "85.25",
        "belt": "brown",
        "dob": date.today() - timedelta(days=365*30),  # 30 years old
        "emergency_contact": "Lisa Brown",
        "emergency_phone": "555-0003",
    },
    {
        "username": "trainee4",
        "first_name": "Emily",
        "last_name": "Davis",
        "email": "emily@example.com",
        "weight": "62.50",
        "belt": "white",
        "dob": date.today() - timedelta(days=365*22),  # 22 years old
        "emergency_contact": "David Davis",
        "emergency_phone": "555-0004",
    },
    {
        "username": "trainee5",
        "first_name": "James",
        "last_name": "Wilson",
        "email": "james@example.com",
        "weight": "88.75",
        "belt": "black",
        "dob": date.today() - timedelta(days=365*35),  # 35 years old
        "emergency_contact": "Robert Wilson",
        "emergency_phone": "555-0005",
    },
    {
        "username": "trainee6",
        "first_name": "Jessica",
        "last_name": "Martinez",
        "email": "jessica@example.com",
        "weight": "68.00",
        "belt": "green",
        "dob": date.today() - timedelta(days=365*26),  # 26 years old
        "emergency_contact": "Carlos Martinez",
        "emergency_phone": "555-0006",
    },
]

trainee_users = []
for trainee_data in trainees_data:
    # Create User
    user, created = User.objects.get_or_create(
        username=trainee_data["username"],
        defaults={
            "first_name": trainee_data["first_name"],
            "last_name": trainee_data["last_name"],
            "email": trainee_data["email"],
        },
    )
    
    if created:
        user.set_password("password123")
        user.save()
        print(f"[+] Created user: {trainee_data['username']}")
    else:
        print(f"[*] User already exists: {trainee_data['username']}")

    # Create UserProfile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": "trainee",
            "phone": trainee_data.get("emergency_phone", ""),
            "date_of_birth": trainee_data.get("dob"),
        },
    )
    
    if created:
        print(f"[+] Created profile for: {trainee_data['username']}")

    # Create Trainee
    trainee, created = Trainee.objects.get_or_create(
        profile=profile,
        defaults={
            "belt_rank": trainee_data["belt"],
            "weight": Decimal(trainee_data["weight"]),
            "emergency_contact": trainee_data["emergency_contact"],
            "emergency_phone": trainee_data["emergency_phone"],
            "status": "active",
        },
    )
    
    if created:
        print(f"[+] Created trainee: {trainee_data['first_name']} {trainee_data['last_name']}")
    else:
        print(f"[*] Trainee already exists: {trainee_data['first_name']}")
    
    trainee_users.append(user)

# Create 4 Judges
judges_data = [
    {
        "username": "judge1",
        "first_name": "Sensei",
        "last_name": "Karate",
        "email": "judge1@example.com",
        "phone": "555-1001",
    },
    {
        "username": "judge2",
        "first_name": "Master",
        "last_name": "Kung",
        "email": "judge2@example.com",
        "phone": "555-1002",
    },
    {
        "username": "judge3",
        "first_name": "Instructor",
        "last_name": "Lee",
        "email": "judge3@example.com",
        "phone": "555-1003",
    },
    {
        "username": "judge4",
        "first_name": "Coach",
        "last_name": "Chen",
        "email": "judge4@example.com",
        "phone": "555-1004",
    },
]

for judge_data in judges_data:
    # Create User
    user, created = User.objects.get_or_create(
        username=judge_data["username"],
        defaults={
            "first_name": judge_data["first_name"],
            "last_name": judge_data["last_name"],
            "email": judge_data["email"],
        },
    )
    
    if created:
        user.set_password("password123")
        user.save()
        print(f"[+] Created judge user: {judge_data['username']}")
    else:
        print(f"[*] Judge user already exists: {judge_data['username']}")

    # Create UserProfile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            "role": "judge",
            "phone": judge_data.get("phone", ""),
        },
    )
    
    if created:
        print(f"[+] Created judge profile for: {judge_data['username']}")
    else:
        print(f"[*] Judge profile already exists: {judge_data['username']}")

print("\n" + "="*50)
print("SUMMARY")
print("="*50)
trainee_count = Trainee.objects.count()
judge_count = UserProfile.objects.filter(role="judge").count()
print(f"[+] Total Trainees: {trainee_count}")
print(f"[+] Total Judges: {judge_count}")
print("\nTest Credentials:")
print("Trainees: trainee1-trainee6 (password: password123)")
print("Judges: judge1-judge4 (password: password123)")
