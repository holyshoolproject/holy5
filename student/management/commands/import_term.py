import os
import django
from openpyxl import Workbook

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sms.settings")  # change 'sms' to your project name
django.setup()

from student.models import AcademicYear   # change to your app name

def export_academic_years():
    wb = Workbook()
    ws = wb.active
    ws.title = "Academic Years"

    # Header
    ws.append(["ID", "Name"])

    # Rows
    for year in AcademicYear.objects.all():
        ws.append([year.id, year.name])

    # Save file
    filename = "academic_years.xlsx"
    wb.save(filename)
    print(f"Exported successfully → {filename}")

if __name__ == "__main__":
    export_academic_years()
