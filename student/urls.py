from django.urls import path
from .views import export_student_profiles_to_excel

urlpatterns = [
    path("export-students/", export_student_profiles_to_excel, name="export_students"),
]
