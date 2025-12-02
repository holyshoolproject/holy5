from openpyxl import Workbook
from django.http import HttpResponse
from .models import StudentFeeRecord



# views.py
import io
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Payment
from utils.receipts import build_payment_receipt



# views.py
import io
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Payment
from utils.receipts import build_payment_receipt


def payment_receipt_inline(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related(
            "student_fee_record",
            "student_fee_record__student",
            "student_fee_record__fee_structure",
            "student_fee_record__fee_structure__grade_class",
            "student_fee_record__fee_structure__term",
            "student_fee_record__fee_structure__academic_year",
        ),
        pk=pk
    )

    # 🚧 Optional authorization filter:
    # if not (request.user.is_staff or payment.student_fee_record.student.user_id == request.user.id):
    #     return HttpResponse(status=403)

    buffer = io.BytesIO()
    build_payment_receipt(payment, buffer, small_on_a4=False)  # set True for small block on A4
    buffer.seek(0)

        
    return HttpResponse(
        buffer.getvalue(),
        content_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="receipt-{payment.pk}.pdf"'}
    )




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
