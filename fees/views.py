from openpyxl import Workbook
from django.http import HttpResponse
from .models import StudentFeeRecord

def export_fee_records(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Fee Records"

    ws.append([
        "Student Name",
        "Fee Structure",
        "Amount Paid",
        "Balance",
        "Fully Paid",
        "Date Created"
    ])

    # Select related student and fee_structure for efficiency
    records = StudentFeeRecord.objects.select_related("student__user", "fee_structure")

    for r in records:
        # Get the student's full name from the related User object
        student_name = getattr(r.student.user, "full_name", str(r.student))

        ws.append([
        student_name,
        str(r.fee_structure),  # convert the object to its string representation
        float(r.amount_paid),
        float(r.balance),
        "Yes" if r.is_fully_paid else "No",
        r.date_created.strftime("%Y-%m-%d %H:%M"),
    ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="fee_records.xlsx"'

    wb.save(response)
    return response
