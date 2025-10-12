import os
import pandas as pd
import random
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
from student.models import StudentProfile

class Command(BaseCommand):
    help = 'Import students from Excel and update their profiles'

    def handle(self, *args, **kwargs):
        # Path to Excel file inside app folder
        excel_file = os.path.join(settings.BASE_DIR, 'student', 'kogdata.xlsx')

        if not os.path.exists(excel_file):
            self.stdout.write(self.style.ERROR(f"Excel file not found: {excel_file}"))
            return

        df = pd.read_excel(excel_file)

        # Open a log file to write the output
        log_file_path = os.path.join(settings.BASE_DIR, 'student_import_log.txt')
        with open(log_file_path, 'w', encoding='utf-8') as log_file:

            log_file.write("Student Import Log\n")
            log_file.write("="*50 + "\n\n")

            for index, row in df.iterrows():
                # Generate or get a valid 8-digit user_id (not all zeros)
                user_id = str(row.get('user_id', '')).zfill(8)
                if len(user_id) != 8 or not user_id.isdigit() or user_id == '00000000':
                    while True:
                        user_id = str(random.randint(10000001, 99999999))
                        if not User.objects.filter(user_id=user_id).exists():
                            break

                # Generate 4-digit random pin/password
                password = str(random.randint(1000, 9999))

                # Create user if it doesn't exist
                user, created = User.objects.get_or_create(
                    user_id=user_id,
                    defaults={
                        'full_name': row.get('full_name', 'Unknown'),
                        'gender': row.get('gender'),
                        'date_of_birth': row.get('date_of_birth'),
                        'nationality': row.get('nationality'),
                        'role': row.get('role', 'student'),
                        'password': password  # will be hashed automatically
                    }
                )

                if created:
                    message = f"Created user: {user.full_name} ({user.user_id}) with password {password}"
                else:
                    message = f"User {user.full_name} ({user.user_id}) already exists, profile updated"

                # Write to both stdout and log file
                self.stdout.write(message)
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
                    profile.contact_of_father = row.get('contact_of_father')
                    profile.contact_of_mother = row.get('contact_of_mother')
                    profile.house_number = row.get('house_number')
                    profile.save()
                except StudentProfile.DoesNotExist:
                    error_msg = f"StudentProfile for user {user.user_id} not found!"
                    self.stdout.write(error_msg)
                    log_file.write(error_msg + "\n")

            log_file.write("\nImport Completed.\n")
            self.stdout.write(self.style.SUCCESS(f"\nAll output saved to {log_file_path}"))
