from django.urls import path
from .views import export_fee_records

urlpatterns = [
    path("export-fee-records/", export_fee_records),
]
