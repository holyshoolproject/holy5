import os
import pandas as pd
import random
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import StudentProfile
from django.contrib import messages

User = get_user_model()

CLASS_NAME_TO_NUMBER = {
    'creche': 1, 'nursery 1': 2, 'nursery 2': 3,
    'kg 1': 4, 'kg1': 4, 'kg 2': 5, 'kg2': 5,
    'class 1': 6, 'class1': 6, 'class 2': 7, 'class2': 7,
    'class 3': 8, 'class3': 8, 'class 4': 9, 'class4': 9,
    'class 5': 10, 'class5': 10, 'class 6': 11, 'class6': 11,
    'jhs 1': 12, 'jhs1': 12, 'jhs 2': 13, 'jhs2': 13,
    'jhs 3': 14, 'jhs3': 14,
}

def safe_date(value):
    if pd.isna(value) or value is pd.NaT:
        return None
    return value

def clean_phone(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    if value.endswith('.0'):
        value = value[:-2]
    if not value.startswith('0') and len(value) == 9:
        value = '0' + value
    return value

def import_students_from_excel(file_path):
    print(f"Importing students fromeeeeeeeeee: {file_path}")
    """Import or update students from an Excel file."""
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"

    df = pd.read_excel(file_path)
    df = df.where(pd.notnull(df), None)

    log_file_path = os.path.join(settings.BASE_DIR, 'student_import_log.txt')
    messages_list = []
    count = 0

    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write("\nStudent Import Log\n" + "="*50 + "\n\n")

        for _, row in df.iterrows():
            full_name = str(row.get('full_name', '')).strip()
            if not full_name or full_name.lower() in ['nan', 'nat', 'none']:
                print(f"Reached empty row. Import stopped at row with full_name='{full_name}'")
                break

            user = User.objects.filter(full_name__iexact=full_name).first()

            if user:
                # Update existing user
                user.gender = row.get('gender', user.gender)
                user.date_of_birth = safe_date(row.get('date_of_birth')) or user.date_of_birth
                user.nationality = row.get('nationality', user.nationality)
                user.role = row.get('role', user.role)
                user.save()
            else:
                # Create new user
                while True:
                    user_id = str(random.randint(10000001, 99999999))
                    if not User.objects.filter(user_id=user_id).exists():
                        break
                password = str(random.randint(1000, 9999))
                user = User.objects.create(
                    user_id=user_id,
                    full_name=full_name,
                    gender=row.get('gender'),
                    date_of_birth=safe_date(row.get('date_of_birth')),
                    nationality=row.get('nationality'),
                    role=row.get('role', 'student'),
                )
                user.set_password(password)
                user.save()
                log_file.write(f"Name: {user.full_name}. ID: {user.user_id} PIN: {password}\n")

            # Create or update StudentProfile
            profile, _ = StudentProfile.objects.get_or_create(user=user)
            profile.last_school_attended = row.get('last_school_attended')
            profile.class_seeking_admission_to = row.get('class_seeking_admission_to')
            profile.is_immunized = row.get('is_immunized')
            profile.has_allergies = row.get('has_allergies')
            profile.allergic_foods = row.get('allergic_foods')
            profile.has_peculiar_health_issues = row.get('has_peculiar_health_issues')
            profile.health_issues = row.get('health_issues')
            profile.other_related_info = row.get('other_related_info')
            profile.name_of_father = row.get('name_of_father')
            profile.name_of_mother = row.get('name_of_mother')
            profile.occupation_of_father = row.get('occupation_of_father')
            profile.occupation_of_mother = row.get('occupation_of_mother')
            profile.nationality_of_father = row.get('nationality_of_father')
            profile.nationality_of_mother = row.get('nationality_of_mother')
            profile.contact_of_father = clean_phone(row.get('contact_of_father'))
            profile.contact_of_mother = clean_phone(row.get('contact_of_mother'))
            profile.house_number = row.get('house_number')

            current_class_name = str(row.get('current_class', '')).strip().lower()
            profile.current_class = CLASS_NAME_TO_NUMBER.get(current_class_name) if current_class_name else None

            profile.save()
            count += 1

              # Final summary message
        summary = f"✅ Successfully imported or updated {count} students."
        messages_list.append(summary)
        log_file.write("\nImport Completed.\n")
        log_file.write(summary + "\n")

    return "\n".join(messages_list)

    