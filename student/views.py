from django.shortcuts import render

# Create your views here.
import openpyxl
from django.http import HttpResponse
from .models import StudentProfile


def export_student_profiles_to_excel(request):
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Student Profiles"

    # Write Excel header
    headers = [
        "Full Name",
        "Current Class",
        "Last School Attended",
        "Class Seeking Admission To",
        "Is Immunized",
        "Has Allergies",
        "Allergic Foods",
        "Has Peculiar Health Issues",
        "Health Issues",
        "Other Related Info",
        "Name of Father",
        "Occupation of Father",
        "Nationality of Father",
        "Contact of Father",
        "Name of Mother",
        "Occupation of Mother",
        "Nationality of Mother",
        "Contact of Mother",
        "House Number"
    ]
    ws.append(headers)

    # Add rows from database
    for profile in StudentProfile.objects.select_related("user"):
        ws.append([
            profile.user.full_name,
            profile.get_current_class_display_name(),
            profile.last_school_attended,
            profile.class_seeking_admission_to,
            profile.is_immunized,
            profile.has_allergies,
            profile.allergic_foods,
            profile.has_peculiar_health_issues,
            profile.health_issues,
            profile.other_related_info,
            profile.name_of_father,
            profile.occupation_of_father,
            profile.nationality_of_father,
            profile.contact_of_father,
            profile.name_of_mother,
            profile.occupation_of_mother,
            profile.nationality_of_mother,
            profile.contact_of_mother,
            profile.house_number,
        ])

    # Prepare the file for download
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="student_profiles.xlsx"'
    wb.save(response)
    return response
