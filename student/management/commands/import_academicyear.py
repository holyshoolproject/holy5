import csv
from django.core.management.base import BaseCommand
from student.models import AcademicYear

class Command(BaseCommand):
    help = "Import AcademicYear from CSV"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to academic_year.csv")

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                name = row["name"].strip()

                # Create AcademicYear if not exists
                ay, created = AcademicYear.objects.get_or_create(name=name)

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created AcademicYear: {name}"))
                else:
                    self.stdout.write(f"Skipped existing AcademicYear: {name}")
