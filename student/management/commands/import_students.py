import os
import pandas as pd
import random
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
from student.models import StudentProfile


def safe_date(value):
    import pandas as pd
    if pd.isna(value) or value is pd.NaT:
        return None
    return value



CLASS_NAME_TO_NUMBER = {
    'creche': 1,
    'nursery 1': 2,
    'nursery 2': 3,
    'kg 1': 4,
    'kg1': 4,
    'kg 2': 5,
    'kg2': 5,
    'class 1': 6,
    'class1': 6,
    'class 2': 7,
    'class2': 7,
    'class 3': 8,
    'class3': 8,
    'class 4': 9,
    'class4': 9,
    'class 5': 10,
    'class5': 10,
    'class 6': 11,
    'class6': 11,
    'jhs 1': 12,
    'jhs1': 12,
    'jhs 2': 13,
    'jhs2': 13,
    'jhs 3': 14,
    'jhs3': 14,
}


def clean_phone(value):
    if pd.isna(value):
        return None
    # Convert to string and strip decimals
    value = str(value).strip()
    if value.endswith('.0'):
        value = value[:-2]
    # Ensure it keeps the leading zero if missing
    if not value.startswith('0') and len(value) == 9:
        value = '0' + value
    return value


class Command(BaseCommand):
    help = 'Import students from Excel and update their profiles'

    def handle(self, *args, **kwargs):
        # Path to Excel file inside app folder
        excel_file = os.path.join(settings.BASE_DIR, 'student', 'kogdata.xlsx')

        if not os.path.exists(excel_file):
            self.stdout.write(self.style.ERROR(f"Excel file not found: {excel_file}"))
            return

        df = pd.read_excel(excel_file)
        df = df.where(pd.notnull(df), None)


        # Open a log file to write the output
        log_file_path = os.path.join(settings.BASE_DIR, 'student_import_log.txt')
        with open(log_file_path, 'a', encoding='utf-8') as log_file:

            log_file.write("\nStudent Import Log\n")

            log_file.write("="*50 + "\n\n")

            for index, row in df.iterrows():
                full_name = str(row.get('full_name', '')).strip()

                # If we reach an empty or invalid full_name, stop importing
                if not full_name or full_name.lower() in ['nan', 'nat', 'none']:
                    print(f"Reached empty row at index {index}. Import stopped.")
                    break

                # Check if a user with this full name already exists
                user = User.objects.filter(full_name__iexact=full_name).first()

                if user:
                    print(f"User {full_name} already exists, profile updated")
                    # Update existing user details
                    user.gender = row.get('gender', user.gender)
                    user.date_of_birth = row.get('date_of_birth', user.date_of_birth)
                    user.nationality = row.get('nationality', user.nationality)
                    user.role = row.get('role', user.role)
                    user.save()

                else:
                    # Generate new unique 8-digit user_id
                    while True:
                        user_id = str(random.randint(10000001, 99999999))
                        if not User.objects.filter(user_id=user_id).exists():
                            break

                    # Generate 4-digit random pin/password
                    password = str(random.randint(1000, 9999))

                    # Create new user
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


                    # Log only new user creation with ID and password
                    message = f"Name: {user.full_name}. ID: {user.user_id} PIN: {password}"
                    print(message)
                    log_file.write(message + "\n")


                # Wait a few seconds for signal to create StudentProfile
                time.sleep(2)

                # Fetch and update StudentProfile
                try:
                    profile = StudentProfile.objects.get(user=user)
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
                    # Handle current_class name conversion
                    current_class_name = str(row.get('current_class', '')).strip().lower()
                    if current_class_name:
                        current_class_value = CLASS_NAME_TO_NUMBER.get(current_class_name)
                        if current_class_value:
                            profile.current_class = current_class_value
                        else:
                            print(f"Warning: Unknown class name '{current_class_name}' for user {user.full_name}")

                    profile.save()

                    
                except StudentProfile.DoesNotExist:
                    error_msg = f"StudentProfile for user {user.user_id} not found!"
                    self.stdout.write(error_msg)
                    log_file.write(error_msg + "\n")

            log_file.write("\nImport Completed.\n")
            self.stdout.write(self.style.SUCCESS(f"\nAll output saved to {log_file_path}"))
