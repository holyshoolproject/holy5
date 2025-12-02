from django.urls import path
from .views import export_fee_records, payment_receipt_inline


urlpatterns = [
    path('payments/<int:pk>/receipt/', payment_receipt_inline, name='payment-receipt'),
    path("export-fee-records/", export_fee_records),
]

